from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .schemas import MediaOptimizationInput


PRIMARY_ACCESSION = "GCF_001890705.1"

CATEGORY_DEFINITIONS: dict[str, dict[str, Any]] = {
    "protease_peptidase": {
        "label": "Протеазы и пептидазы",
        "keywords": ["protease", "peptidase", "proteinase", "metalloprotease", "serine protease", "endopeptidase"],
        "interpretation": "Основной слой доказательств для коллагенолитической гипотезы; прямая аннотация collagenase отслеживается отдельно.",
    },
    "secretory_system": {
        "label": "Секреторный и внеклеточный аппарат",
        "keywords": ["signal peptide", "secreted", "secretion", "extracellular"],
        "interpretation": "Поддерживает вывод внеклеточных ферментов и секретируемых белков.",
    },
    "transport": {
        "label": "Транспортеры и пермеазы",
        "keywords": ["transporter", "permease", "abc transporter", "major facilitator", "mfs transporter"],
        "interpretation": "Ограничивает гипотезы по поглощению субстратов, ионному балансу и экспорту продукта.",
    },
    "carbon_redox_metabolism": {
        "label": "Центральный углеродный обмен, redox и дыхание",
        "keywords": [
            "glycosidase",
            "glucosidase",
            "amylase",
            "cellulase",
            "xylanase",
            "dehydrogenase",
            "oxidoreductase",
            "respiratory",
            "cytochrome",
        ],
        "interpretation": "Доказательства конверсии углерода, redox-баланса и кислород-зависимого метаболизма.",
    },
    "secondary_metabolism": {
        "label": "Вторичный метаболизм",
        "keywords": ["polyketide", "nonribosomal", "terpene", "cytochrome p450", "methyltransferase", "nrps", "pks"],
        "interpretation": "BGC-связанный потенциал, который при стрессе может конкурировать с ростом или секрецией.",
    },
    "cell_cycle": {
        "label": "Маркеры клеточного цикла и деления",
        "keywords": ["cyclin", "cyclin-dependent", "cdk", "cell division", "mitotic", "mitosis"],
        "interpretation": "В v1 это только слой доказательств; ODE/FBA-симуляция клеточного цикла не выполняется.",
    },
}

DIRECT_COLLAGENASE_KEYWORDS = ["collagenase", "collagenolytic", "collagen"]
TEXT_ASSETS = {
    "gbff": "genomic.gbff",
    "gff": "genomic.gff",
    "protein": "protein.faa",
    "cds": "cds_from_genomic.fna",
    "rna": "rna.fna",
}


@dataclass(frozen=True)
class FastaStats:
    sequence_count: int
    total_bp: int
    n50_bp: int
    max_bp: int


def _web_app_root() -> Path:
    return Path(__file__).resolve().parent


def _knowledge_root() -> Path:
    return _web_app_root().parent


def locate_primary_assembly(accession: str = PRIMARY_ACCESSION) -> Path:
    candidates = [
        _web_app_root()
        / "data"
        / "omics"
        / "aspergillus_sydowii"
        / "raw"
        / accession
        / "ncbi_dataset"
        / "data"
        / accession,
        _knowledge_root()
        / "Aspergillus sydowii_dataset_all data_NCBI"
        / "ncbi_dataset"
        / "data"
        / accession,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _read_dataset_summary(accession: str) -> dict[str, Any]:
    summary_path = _knowledge_root() / "Aspergillus sydowii_dataset_all data_NCBI" / "ncbi_dataset" / "data" / "data_summary.tsv"
    if not summary_path.exists():
        return {}
    lines = summary_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if not lines:
        return {}
    headers = lines[0].split("\t")
    for line in lines[1:]:
        values = line.split("\t")
        row = dict(zip(headers, values))
        if row.get("Assembly Accession") == accession:
            return row
    return {}


def _find_genomic_fasta(assembly_dir: Path, accession: str) -> Path | None:
    exact = assembly_dir / f"{accession}_Aspsy1_genomic.fna"
    if exact.exists():
        return exact
    for path in assembly_dir.glob("*.fna"):
        lowered = path.name.lower()
        if "genomic" in lowered and "cds_from" not in lowered and "rna" not in lowered:
            return path
    return None


def _fasta_stats(path: Path | None) -> FastaStats:
    if path is None or not path.exists():
        return FastaStats(sequence_count=0, total_bp=0, n50_bp=0, max_bp=0)
    lengths: list[int] = []
    current = 0
    seen = False
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if line.startswith(">"):
                if seen:
                    lengths.append(current)
                seen = True
                current = 0
            else:
                current += len(line.strip())
        if seen:
            lengths.append(current)
    total = sum(lengths)
    ordered = sorted(lengths, reverse=True)
    halfway = total / 2
    cumulative = 0
    n50 = 0
    for length in ordered:
        cumulative += length
        if cumulative >= halfway:
            n50 = length
            break
    return FastaStats(sequence_count=len(lengths), total_bp=total, n50_bp=n50, max_bp=ordered[0] if ordered else 0)


def _count_fasta_records(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        return sum(1 for line in handle if line.startswith(">"))


def _scan_file(path: Path, keywords: list[str]) -> tuple[int, list[str]]:
    if not path.exists():
        return 0, []
    lowered_keywords = [keyword.lower() for keyword in keywords]
    count = 0
    examples: list[str] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            lowered = line.lower()
            if any(keyword in lowered for keyword in lowered_keywords):
                count += 1
                if len(examples) < 5:
                    examples.append(line.strip()[:260])
    return count, examples


def _confidence(sources: list[str], total_matches: int) -> str:
    source_set = set(sources)
    if total_matches <= 0:
        return "low"
    if "protein" in source_set and ("gff" in source_set or "gbff" in source_set):
        return "high"
    if len(source_set) >= 2:
        return "medium"
    return "low"


def _score(total_matches: int, sources: list[str], keyword_hits: int) -> int:
    if total_matches <= 0:
        return 0
    evidence_component = min(78, round(math.log1p(total_matches) / math.log(180) * 78))
    diversity_component = min(14, len(set(sources)) * 3)
    keyword_component = min(8, keyword_hits * 2)
    return min(100, evidence_component + diversity_component + keyword_component)


def _build_category_report(assembly_dir: Path, name: str, definition: dict[str, Any]) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    total_matches = 0
    sources: list[str] = []
    keyword_hit_set: set[str] = set()
    for asset_name, filename in TEXT_ASSETS.items():
        path = assembly_dir / filename
        count, examples = _scan_file(path, definition["keywords"])
        if count:
            total_matches += count
            sources.append(asset_name)
            lowered_examples = " ".join(examples).lower()
            keyword_hit_set.update(keyword for keyword in definition["keywords"] if keyword.lower() in lowered_examples)
            evidence[asset_name] = {
                "path": str(path),
                "match_count": count,
                "examples": examples,
            }
    return {
        "name": name,
        "label": definition["label"],
        "keywords": definition["keywords"],
        "match_count": total_matches,
        "source_count": len(set(sources)),
        "sources": sorted(set(sources)),
        "score": _score(total_matches, sources, len(keyword_hit_set)),
        "confidence": _confidence(sources, total_matches),
        "interpretation": definition["interpretation"],
        "evidence": evidence,
    }


@lru_cache(maxsize=4)
def build_genome_report(accession: str = PRIMARY_ACCESSION) -> dict[str, Any]:
    assembly_dir = locate_primary_assembly(accession)
    summary = _read_dataset_summary(accession)
    genomic_fasta = _find_genomic_fasta(assembly_dir, accession)
    stats = _fasta_stats(genomic_fasta)
    files = {asset_name: assembly_dir / filename for asset_name, filename in TEXT_ASSETS.items()}
    categories = {
        name: _build_category_report(assembly_dir, name, definition)
        for name, definition in CATEGORY_DEFINITIONS.items()
    }
    direct_gbff_count, direct_examples = _scan_file(files["gbff"], DIRECT_COLLAGENASE_KEYWORDS)
    direct_protein_count, direct_protein_examples = _scan_file(files["protein"], DIRECT_COLLAGENASE_KEYWORDS)
    protein_count = _count_fasta_records(files["protein"])
    cds_count = _count_fasta_records(files["cds"])
    rna_count = _count_fasta_records(files["rna"])
    gene_count = int(summary.get("Gene Count") or protein_count or 0)

    warnings: list[str] = [
        "v1 - модель потенциала по аннотации, а не полноразмерная flux-balance GEM.",
        "Автоматический gap-filling и полноразмерная курируемая реконструкция не выполняются в этом слое.",
    ]
    if direct_gbff_count == 0 and direct_protein_count == 0:
        warnings.append(
            "No direct collagenase/collagenolytic keyword hit: в GBFF/protein не найден прямой признак; коллагенолитический потенциал выведен из протеаз/пептидаз и секреции."
        )

    return {
        "accession": accession,
        "assembly_dir": str(assembly_dir),
        "assembly_found": assembly_dir.exists(),
        "genome_summary": {
            "organism": summary.get("Organism Scientific Name", "Aspergillus sydowii CBS 593.65"),
            "assembly_name": summary.get("Assembly Name", "Aspsy1"),
            "source": summary.get("Source", "RefSeq"),
            "level": summary.get("Level", "Scaffold"),
            "total_bp": stats.total_bp,
            "sequence_count": stats.sequence_count,
            "n50_bp": stats.n50_bp,
            "max_sequence_bp": stats.max_bp,
            "gene_count": gene_count,
            "protein_count": protein_count,
            "cds_count": cds_count,
            "rna_count": rna_count,
        },
        "available_files": {
            key: {"path": str(path), "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0}
            for key, path in files.items()
        },
        "categories": list(categories.values()),
        "categories_by_name": categories,
        "direct_collagenase_evidence": {
            "keywords": DIRECT_COLLAGENASE_KEYWORDS,
            "gbff_match_count": direct_gbff_count,
            "protein_match_count": direct_protein_count,
            "examples": direct_examples + direct_protein_examples,
            "found_direct_annotation": direct_gbff_count > 0 or direct_protein_count > 0,
        },
        "warnings": warnings,
        "model_boundaries": [
            "В v1 основная сборка зафиксирована как GCF_001890705.1.",
            "Признаки клеточного цикла учитываются только как аннотационный потенциал; ODE/event-модель не симулируется.",
            "Индексы являются поддержкой решений и требуют валидации по измерениям культивирования.",
        ],
    }


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _status(score: int) -> str:
    if score >= 74:
        return "active"
    if score >= 45:
        return "balanced"
    return "limiting"


def _model_to_dict(input_data: MediaOptimizationInput) -> dict[str, Any]:
    if hasattr(input_data, "model_dump"):
        return input_data.model_dump()
    return input_data.dict()


def evaluate_conditions(input_data: MediaOptimizationInput, genome_report: dict[str, Any] | None = None) -> dict[str, Any]:
    report = genome_report or build_genome_report()
    by_name = report["categories_by_name"]
    carbon_fit = _clamp(input_data.molasses_g_l / 28)
    nitrogen_fit = _clamp(input_data.peptone_g_l / 90)
    collagen_signal = _clamp(input_data.collagen_g_l / 8)
    ph_fit = _clamp(1 - abs(input_data.pH - 7.25) / 0.9)
    oxygen_fit = _clamp((input_data.aeration_vvm * 0.48) + (input_data.rpm - 160) / 260)
    temperature_fit = _clamp(1 - abs(input_data.temperature_C - 25) / 7)
    viscosity_pressure = _clamp((carbon_fit * 0.22) + (nitrogen_fit * 0.34) + (collagen_signal * 0.26) + max(0, input_data.molasses_g_l - 30) / 45)

    protease = by_name["protease_peptidase"]["score"] / 100
    secretion = by_name["secretory_system"]["score"] / 100
    transport = by_name["transport"]["score"] / 100
    carbon_redox = by_name["carbon_redox_metabolism"]["score"] / 100
    secondary = by_name["secondary_metabolism"]["score"] / 100
    cell_cycle = by_name["cell_cycle"]["score"] / 100

    programs = [
        {
            "name": "Углеродный и redox-потенциал",
            "score": round(100 * ((carbon_redox * 0.38) + (carbon_fit * 0.26) + (oxygen_fit * 0.22) + (transport * 0.14))),
            "status": "",
            "rationale": "Аннотация углеродного/redox-обмена взвешена доступностью мелассы, переносом кислорода и доказательствами транспортеров.",
        },
        {
            "name": "Потенциал секретируемых протеаз",
            "score": round(100 * ((protease * 0.34) + (secretion * 0.24) + (nitrogen_fit * 0.18) + (collagen_signal * 0.14) + (ph_fit * 0.10))),
            "status": "",
            "rationale": "Доказательства протеаз/пептидаз усиливаются снабжением азотом, коллагеновым субстратом, признаками секреции и соответствием pH.",
        },
        {
            "name": "Готовность кислорода и транспорта",
            "score": round(100 * ((oxygen_fit * 0.38) + (transport * 0.30) + (carbon_redox * 0.22) + (temperature_fit * 0.10))),
            "status": "",
            "rationale": "Аэрация, перемешивание и доказательства транспортеров задают процессный резерв аэробного метаболизма.",
        },
        {
            "name": "Аннотационный слой клеточного цикла",
            "score": round(100 * ((cell_cycle * 0.44) + (carbon_fit * 0.18) + (nitrogen_fit * 0.18) + (ph_fit * 0.10) + (temperature_fit * 0.10))),
            "status": "",
            "rationale": "Маркеры клеточного цикла поддерживают потенциал роста, но v1 не симулирует динамику G1/S/G2/M.",
        },
        {
            "name": "Давление вторичного метаболизма",
            "score": round(100 * ((secondary * 0.38) + (viscosity_pressure * 0.26) + (1 - oxygen_fit) * 0.20 + max(0, input_data.molasses_g_l - 24) / 60)),
            "status": "",
            "rationale": "BGC-связанные признаки становятся значимее при стрессе, высокой нагрузке и кислородном давлении.",
        },
    ]
    for program in programs:
        score = max(0, min(100, int(program["score"])))
        program["score"] = score
        program["status"] = "watch" if program["name"] == "Давление вторичного метаболизма" and score >= 55 else _status(score)

    collagen_direct = report["direct_collagenase_evidence"]["found_direct_annotation"]
    collagenase_readout = round(
        100
        * (
            (protease * 0.26)
            + (secretion * 0.20)
            + (collagen_signal * 0.18)
            + (nitrogen_fit * 0.14)
            + (oxygen_fit * 0.12)
            + (ph_fit * 0.10)
        )
    )
    biomass_readout = round(100 * ((carbon_fit * 0.28) + (nitrogen_fit * 0.20) + (oxygen_fit * 0.22) + (carbon_redox * 0.18) + (cell_cycle * 0.12)))
    oxygen_risk = round(100 * _clamp((carbon_fit * 0.30) + (biomass_readout / 100 * 0.28) + (viscosity_pressure * 0.24) - (oxygen_fit * 0.22)))

    interpretation = [
        "Используйте это как модель приоритизации для дизайна культуры, а не как стехиометрическое доказательство роста.",
        "Коллагеназная активность остаётся выведенным фенотипом до доменной валидации и экспериментального анализа протеазных кандидатов.",
    ]
    if not collagen_direct:
        interpretation.append("В просмотренных файлах NCBI отсутствует прямая аннотация collagenase; нельзя называть конкретный ген коллагеназой только по выводу v1.")
    if oxygen_risk >= 55:
        interpretation.append("Давление кислорода/вязкости достаточно высокое: pO₂ и KLA нужно считать жёсткими процессными ограничениями.")
    if collagenase_readout >= 75 and oxygen_risk < 60:
        interpretation.append("Текущая среда совместима со сценарием скрининга секретируемых протеаз/коллагенолитической активности.")

    return {
        "input": _model_to_dict(input_data),
        "programs": programs,
        "projection": {
            "biomass_potential_index": max(0, min(100, biomass_readout)),
            "collagenolytic_potential_index": max(0, min(100, collagenase_readout)),
            "oxygen_process_risk_index": max(0, min(100, oxygen_risk)),
            "viscosity_pressure_index": round(100 * viscosity_pressure),
            "secondary_metabolism_pressure_index": next(item["score"] for item in programs if item["name"] == "Давление вторичного метаболизма"),
            "confidence": "high" if by_name["protease_peptidase"]["confidence"] == "high" and by_name["secretory_system"]["confidence"] != "low" else "medium",
        },
        "interpretation": interpretation,
    }


def build_system_biology_model(input_data: MediaOptimizationInput | None = None) -> dict[str, Any]:
    report = build_genome_report(PRIMARY_ACCESSION)
    conditions = evaluate_conditions(input_data or MediaOptimizationInput(), report)
    compact_report = dict(report)
    compact_report.pop("categories_by_name", None)
    return {
        "model_version": "system_biology_v1",
        "primary_accession": PRIMARY_ACCESSION,
        "genome_report": compact_report,
        "condition_evaluation": conditions,
    }


def dump_report_json(path: Path) -> None:
    path.write_text(json.dumps(build_system_biology_model(), ensure_ascii=False, indent=2), encoding="utf-8")
