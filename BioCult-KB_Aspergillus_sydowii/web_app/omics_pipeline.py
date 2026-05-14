from __future__ import annotations

import csv
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

from . import omics_registry, omics_validation
from .schemas import OmicsProjectRequest


ASSET_EXTENSIONS = {
    ".fa": "fasta",
    ".fasta": "fasta",
    ".fna": "genomic_fasta",
    ".faa": "protein_fasta",
    ".ffn": "cds_fasta",
    ".gff": "gff",
    ".gff3": "gff3",
    ".gbff": "genbank",
    ".gbk": "genbank",
    ".json": "report",
    ".jsonl": "report",
    ".tsv": "table",
    ".csv": "table",
}

BIOSYNTHESIS_KEYWORDS = {
    "protease_peptidase": ["protease", "peptidase", "proteinase", "metalloprotease", "serine protease"],
    "collagenase_candidate": ["collagenase", "collagenolytic", "collagen"],
    "secretory_system": ["signal peptide", "secreted", "secretion", "extracellular"],
    "transport": ["transporter", "permease", "abc transporter", "major facilitator"],
    "carbon_metabolism": ["glycosidase", "amylase", "dehydrogenase", "oxidoreductase"],
    "secondary_metabolism": ["polyketide", "nonribosomal", "terpene", "cytochrome p450", "methyltransferase"],
}


def omics_root() -> Path:
    return Path(__file__).resolve().parent / "data" / "omics" / "aspergillus_sydowii"


def build_manifest(request: OmicsProjectRequest) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "organism_name": "Aspergillus sydowii",
        "primary_selection": {
            "genome_accession": request.genome_accession,
            "transcriptome_bioproject": request.transcriptome_bioproject,
            "metabolome_label": request.metabolome_label,
        },
        "resource_registry": omics_registry.serialize_registry(),
        "verified_resources": omics_registry.get_verified_resources(),
        "candidate_resources": omics_registry.get_candidate_resources(),
        "downloadable_resources": omics_registry.get_downloadable_resources(),
        "pipeline_scope": {
            "genome_package": "NCBI Datasets assembly package with genome, GFF3, RNA, CDS, proteins, GBFF, and reports.",
            "transcriptome": "BioProject to SRA RunInfo discovery; transcriptome constrains condition-specific model and does not replace metabolome.",
            "metabolomics": "References and candidate endpoints are kept separate until manual metadata validation.",
        },
    }


def build_commands(request: OmicsProjectRequest, root: Path | None = None) -> dict[str, str]:
    root = root or omics_root()
    raw_dir = root / "raw"
    reports_dir = root / "reports"
    genome_zip = raw_dir / f"{request.genome_accession}_ncbi_dataset.zip"
    runinfo_path = reports_dir / f"{request.transcriptome_bioproject}_runinfo.csv"
    return {
        "download_genome_rest": (
            "NCBI Datasets REST: "
            f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/{request.genome_accession}/download"
        ),
        "download_genome": (
            f"datasets download genome accession {request.genome_accession} "
            "--include genome,gff3,rna,cds,protein,gbff,seq-report "
            f"--filename \"{genome_zip}\""
        ),
        "unzip_genome": f"python -m zipfile -e \"{genome_zip}\" \"{raw_dir / request.genome_accession}\"",
        "discover_transcriptome": (
            f"esearch -db sra -query \"{request.transcriptome_bioproject}[BioProject]\" "
            f"| efetch -format runinfo > \"{runinfo_path}\""
        ),
        "download_reads": f"bash \"{reports_dir / f'{request.transcriptome_bioproject}_download_reads.sh'}\"",
    }


def genome_download_url(accession: str) -> str:
    include_types = [
        "GENOME_FASTA",
        "GENOME_GFF",
        "RNA_FASTA",
        "CDS_FASTA",
        "PROT_FASTA",
        "GENOME_GBFF",
        "SEQUENCE_REPORT",
    ]
    query = "&".join(f"include_annotation_type={item}" for item in include_types)
    return f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/{accession}/download?{query}"


def index_assets(package_dir: Path) -> list[dict[str, Any]]:
    if not package_dir.exists():
        return []

    assets: list[dict[str, Any]] = []
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        asset_type = ASSET_EXTENSIONS.get(suffix)
        if asset_type is None and path.name.endswith(".gff3.gz"):
            asset_type = "gff3"
        if asset_type is None:
            continue
        assets.append(
            {
                "path": str(path),
                "relative_path": str(path.relative_to(package_dir)),
                "asset_type": asset_type,
                "size_bytes": path.stat().st_size,
            }
        )
    return assets


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_sample_sheet(path: Path, bioproject: str, run_ids: list[str] | None = None) -> None:
    run_ids = run_ids or []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["sample_id", "run_accession", "bioproject", "condition", "replicate", "notes"])
        for index, run_id in enumerate(run_ids, start=1):
            writer.writerow([f"{bioproject}_sample_{index}", run_id, bioproject, "unknown", index, "Fill after SRA metadata review"])


def write_download_script(path: Path, sample_sheet_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    script = f"""#!/usr/bin/env bash
set -euo pipefail

SAMPLE_SHEET="${{1:-{sample_sheet_path}}}"
OUT_DIR="${{2:-fastq}}"
mkdir -p "$OUT_DIR"

tail -n +2 "$SAMPLE_SHEET" | while IFS=$'\\t' read -r sample_id run_accession bioproject condition replicate notes; do
  if [[ -z "$run_accession" ]]; then
    continue
  fi
  prefetch "$run_accession"
  fasterq-dump "$run_accession" --split-files --outdir "$OUT_DIR"
done
"""
    path.write_text(script, encoding="utf-8")


def parse_runinfo(runinfo_path: Path) -> list[dict[str, str]]:
    if not runinfo_path.exists():
        return []
    with runinfo_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader if row.get("Run")]


def discover_transcriptome_runinfo_http(bioproject: str) -> dict[str, Any]:
    reports_dir = omics_root() / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    runinfo_path = reports_dir / f"{bioproject}_runinfo.csv"
    summary_path = reports_dir / f"{bioproject}_summary.json"
    sample_sheet_path = reports_dir / f"{bioproject}_sample_sheet.tsv"
    download_script_path = reports_dir / f"{bioproject}_download_reads.sh"
    url = f"https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/runinfo?term={bioproject}"

    urlretrieve(url, runinfo_path)
    rows = parse_runinfo(runinfo_path)
    run_ids = [row["Run"] for row in rows]
    total_size_mb = sum(float(row.get("size_MB") or 0) for row in rows)
    total_bases = sum(int(row.get("bases") or 0) for row in rows)
    write_sample_sheet(sample_sheet_path, bioproject, run_ids=run_ids)
    write_download_script(download_script_path, sample_sheet_path)
    summary = {
        "bioproject": bioproject,
        "run_count": len(rows),
        "run_ids": run_ids,
        "total_size_MB": round(total_size_mb, 1),
        "total_bases": total_bases,
        "runinfo_path": str(runinfo_path),
        "sample_sheet_path": str(sample_sheet_path),
        "download_script_path": str(download_script_path),
        "status": "runinfo_discovered",
        "read_download_note": "RNA-seq reads are large. Use SRA Toolkit or generated download_path values deliberately; transcriptome is a condition-specific layer, not metabolome replacement.",
    }
    write_json(summary_path, summary)
    return summary


def scaffold_project(request: OmicsProjectRequest) -> dict[str, Any]:
    root = omics_root()
    reports_dir = root / "reports"
    raw_dir = root / "raw"
    packages_dir = raw_dir / request.genome_accession
    root.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(request)
    manifest_errors = omics_validation.validate_manifest_structure(manifest)
    commands = build_commands(request, root=root)

    manifest_path = reports_dir / "manifest.json"
    assets_index_path = reports_dir / "assets_index.json"
    runinfo_path = reports_dir / f"{request.transcriptome_bioproject}_runinfo.csv"
    summary_path = reports_dir / f"{request.transcriptome_bioproject}_summary.json"
    sample_sheet_path = reports_dir / f"{request.transcriptome_bioproject}_sample_sheet.tsv"
    download_script_path = reports_dir / f"{request.transcriptome_bioproject}_download_reads.sh"

    assets = index_assets(packages_dir)
    write_json(manifest_path, manifest)
    write_json(
        assets_index_path,
        {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "package_dir": str(packages_dir),
            "assets": assets,
            "note": "Assets are empty until the NCBI genome package is downloaded and unpacked.",
        },
    )
    if not runinfo_path.exists():
        runinfo_path.write_text(
            "Run,ReleaseDate,LoadDate,spots,bases,spots_with_mates,avgLength,size_MB,AssemblyName,download_path,Experiment,LibraryName,LibraryStrategy,LibrarySelection,LibrarySource,LibraryLayout,InsertSize,InsertDev,Platform,Model,SRAStudy,BioProject,Study_Pubmed_id,ProjectID,Sample,BioSample,SampleType,TaxID,ScientificName,SampleName,g1k_pop_code,source,g1k_analysis_group,Subject_ID,Sex,Disease,Tumor,Affection_Status,Analyte_Type,Histological_Type,Body_Site,CenterName,Submission,dbgap_study_accession,Consent,RunHash,ReadHash\n",
            encoding="utf-8",
        )
    write_json(
        summary_path,
        {
            "bioproject": request.transcriptome_bioproject,
            "runinfo_path": str(runinfo_path),
            "discovery_command": commands["discover_transcriptome"],
            "status": "pending_runinfo_discovery",
            "note": "Run Entrez Direct discovery to populate runinfo, then regenerate sample sheet with confirmed run accessions.",
        },
    )
    write_sample_sheet(sample_sheet_path, request.transcriptome_bioproject)
    write_download_script(download_script_path, sample_sheet_path)

    return {
        "project_dir": str(root),
        "artifacts": {
            "manifest": str(manifest_path),
            "assets_index": str(assets_index_path),
            "runinfo": str(runinfo_path),
            "summary": str(summary_path),
            "sample_sheet": str(sample_sheet_path),
            "download_script": str(download_script_path),
        },
        "commands": commands,
        "tool_status": omics_validation.check_tool_availability(),
        "validation": {
            "manifest_valid": not manifest_errors,
            "manifest_errors": manifest_errors,
            "genome_accession_valid": omics_validation.validate_genome_accession(request.genome_accession),
            "transcriptome_bioproject_valid": omics_validation.validate_bioproject_accession(request.transcriptome_bioproject),
        },
        "manifest": manifest,
    }


def download_genome_package(request: OmicsProjectRequest) -> dict[str, Any]:
    commands = build_commands(request)
    if not omics_validation.check_tool_availability()["datasets"]:
        return {
            "ok": False,
            "command": commands["download_genome"],
            "error": "NCBI Datasets CLI is not available in PATH.",
        }
    completed = subprocess.run(commands["download_genome"], shell=True, capture_output=True, text=True, check=False)
    return {
        "ok": completed.returncode == 0,
        "command": commands["download_genome"],
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
    }


def download_genome_package_rest(accession: str) -> dict[str, Any]:
    root = omics_root()
    raw_dir = root / "raw"
    package_dir = raw_dir / accession
    reports_dir = root / "reports"
    raw_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    zip_path = raw_dir / f"{accession}_ncbi_dataset.zip"
    url = genome_download_url(accession)

    if not zip_path.exists():
        urlretrieve(url, zip_path)

    package_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(package_dir)
    assets = index_assets(package_dir)
    return {
        "accession": accession,
        "ok": True,
        "url": url,
        "zip_path": str(zip_path),
        "zip_size_bytes": zip_path.stat().st_size,
        "package_dir": str(package_dir),
        "asset_count": len(assets),
        "assets": assets,
    }


def download_all_verified_genome_packages() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for item in omics_registry.get_verified_resources()["genomes"]:
        accession = str(item["accession"])
        try:
            results.append(download_genome_package_rest(accession))
        except Exception as exc:  # noqa: BLE001 - returned to UI/API as per-run status.
            results.append({"accession": accession, "ok": False, "error": str(exc), "url": genome_download_url(accession)})

    assets = []
    for result in results:
        assets.extend(result.get("assets", []))
    write_json(
        omics_root() / "reports" / "assets_index.json",
        {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "downloaded_genome_packages": results,
            "assets": assets,
        },
    )
    return {
        "downloaded": results,
        "ok_count": sum(1 for item in results if item.get("ok")),
        "error_count": sum(1 for item in results if not item.get("ok")),
        "asset_count": len(assets),
    }


def _scan_text_file(path: Path, keywords: list[str]) -> list[str]:
    matches: list[str] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                lowered = line.lower()
                if any(keyword in lowered for keyword in keywords):
                    matches.append(line.strip()[:500])
                    if len(matches) >= 30:
                        break
    except OSError:
        return []
    return matches


def build_biosynthesis_asset_report() -> dict[str, Any]:
    root = omics_root()
    raw_dir = root / "raw"
    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    files = [
        path
        for path in raw_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".faa", ".gff", ".gbff", ".fna"}
    ]
    categories: dict[str, dict[str, Any]] = {}
    for category, keywords in BIOSYNTHESIS_KEYWORDS.items():
        evidence: list[dict[str, Any]] = []
        for path in files:
            matches = _scan_text_file(path, keywords)
            if matches:
                evidence.append(
                    {
                        "file": str(path),
                        "relative_file": str(path.relative_to(raw_dir)),
                        "match_count_capped": len(matches),
                        "examples": matches[:5],
                    }
                )
        categories[category] = {
            "keyword_set": keywords,
            "evidence_file_count": len(evidence),
            "evidence": evidence[:20],
        }

    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scanned_file_count": len(files),
        "categories": categories,
        "interpretation": {
            "protease_peptidase": "Primary search space for collagenase/protease production hypotheses.",
            "collagenase_candidate": "Direct keyword hits are strong clues but require sequence/domain validation.",
            "secondary_metabolism": "BGC-related potential may compete with or complement enzyme production depending on stress state.",
            "transport": "Transporters constrain substrate uptake and secretion of extracellular products.",
        },
    }
    write_json(reports_dir / "biosynthesis_potential_report.json", report)
    return report


def unzip_genome_package(request: OmicsProjectRequest) -> dict[str, Any]:
    root = omics_root()
    genome_zip = root / "raw" / f"{request.genome_accession}_ncbi_dataset.zip"
    package_dir = root / "raw" / request.genome_accession
    if not genome_zip.exists():
        return {"ok": False, "error": f"Genome package zip not found: {genome_zip}"}
    package_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(genome_zip) as archive:
        archive.extractall(package_dir)
    assets = index_assets(package_dir)
    return {"ok": True, "package_dir": str(package_dir), "asset_count": len(assets), "assets": assets}
