from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .. import gem_cobra
from ..schemas import GemFbaInput, TranscriptomeFbaInput


def transcriptome_dir() -> Path:
    path = Path(__file__).resolve().parents[1] / "data" / "omics" / "aspergillus_sydowii" / "transcriptome"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_tpm_csv(dataset_id: str, content: str) -> dict[str, Any]:
    path = transcriptome_dir() / f"{dataset_id}.csv"
    path.write_text(content, encoding="utf-8")
    tpm = load_tpm(path)
    return {"dataset_id": dataset_id, "path": str(path), "gene_count": len(tpm), "status": "ready"}


def load_tpm(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        gene_key = "gene_id" if "gene_id" in fields else fields[0] if fields else "gene_id"
        tpm_key = "TPM" if "TPM" in fields else "tpm" if "tpm" in fields else fields[1] if len(fields) > 1 else "TPM"
        values: dict[str, float] = {}
        for row in reader:
            gene = str(row.get(gene_key) or "").strip()
            if not gene:
                continue
            try:
                values[gene] = float(row.get(tpm_key) or 0.0)
            except ValueError:
                values[gene] = 0.0
        return values


def apply_eflux_weights(model: Any, tpm: dict[str, float], threshold: float = 0.05) -> dict[str, Any]:
    if not tpm:
        return {"model": model, "n_reactions_constrained": 0, "gene_coverage": 0.0, "active_genes": []}
    max_tpm = max(tpm.values()) or 1.0
    constrained = 0
    covered_genes: set[str] = set()
    for reaction in model.reactions:
        genes = list(getattr(reaction, "genes", []))
        if not genes:
            continue
        gene_ids = [gene.id for gene in genes]
        expr = [tpm.get(gene_id, 0.0) for gene_id in gene_ids]
        if not expr:
            continue
        weight = max(min(expr) / max_tpm, threshold)
        if reaction.upper_bound > 0:
            reaction.upper_bound *= weight
            constrained += 1
        covered_genes.update(gene_id for gene_id in gene_ids if gene_id in tpm)
    return {
        "model": model,
        "n_reactions_constrained": constrained,
        "gene_coverage": round(len(covered_genes) / max(len(tpm), 1), 5),
        "active_genes": sorted(gene for gene, value in tpm.items() if value >= max_tpm * threshold)[:50],
    }


def run_transcriptome_fba(input_data: TranscriptomeFbaInput) -> dict[str, Any]:
    path = transcriptome_dir() / f"{input_data.dataset_id}.csv"
    tpm = input_data.tpm or load_tpm(path)
    base = gem_cobra.run_fba(GemFbaInput(medium=input_data.medium, objective=input_data.objective, growth_floor=input_data.growth_floor))
    if not base.get("available"):
        return {**base, "data_source": str(path), "gene_coverage": 0.0, "n_reactions_constrained": 0}
    try:
        model = gem_cobra.load_sbml_model()
        metadata = apply_eflux_weights(model, tpm, threshold=input_data.threshold)
        return {
            **base,
            "data_source": str(path),
            "gene_coverage": metadata["gene_coverage"],
            "n_reactions_constrained": metadata["n_reactions_constrained"],
            "active_genes": metadata["active_genes"],
            "warnings": (base.get("warnings") or []) + ([] if tpm else ["No TPM values supplied; unconstrained GEM-lite result returned."]),
        }
    except Exception as exc:  # noqa: BLE001
        return {**base, "status": "degraded", "error": str(exc), "gene_coverage": 0.0, "n_reactions_constrained": 0}

