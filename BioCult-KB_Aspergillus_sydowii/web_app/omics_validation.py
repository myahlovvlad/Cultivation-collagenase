from __future__ import annotations

import re
import shutil
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GENOME_ACCESSION_RE = re.compile(r"^GC[AF]_\d{9}\.\d+$")
BIOPROJECT_RE = re.compile(r"^PRJNA\d+$")


def validate_genome_accession(accession: str) -> bool:
    return bool(GENOME_ACCESSION_RE.match(accession))


def validate_bioproject_accession(accession: str) -> bool:
    return bool(BIOPROJECT_RE.match(accession))


def check_tool_availability() -> dict[str, bool]:
    return {
        "datasets": shutil.which("datasets") is not None,
        "esearch": shutil.which("esearch") is not None,
        "efetch": shutil.which("efetch") is not None,
        "prefetch": shutil.which("prefetch") is not None,
        "fasterq-dump": shutil.which("fasterq-dump") is not None,
    }


def validate_manifest_structure(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_top_level = {
        "created_at_utc",
        "organism_name",
        "primary_selection",
        "resource_registry",
        "verified_resources",
        "candidate_resources",
        "downloadable_resources",
    }
    missing = sorted(required_top_level - set(manifest))
    if missing:
        errors.append(f"Missing manifest keys: {', '.join(missing)}")

    primary_selection = manifest.get("primary_selection", {})
    genome_accession = primary_selection.get("genome_accession")
    transcriptome_bioproject = primary_selection.get("transcriptome_bioproject")

    if genome_accession and not validate_genome_accession(genome_accession):
        errors.append(f"Invalid genome accession: {genome_accession}")
    if transcriptome_bioproject and not validate_bioproject_accession(transcriptome_bioproject):
        errors.append(f"Invalid BioProject accession: {transcriptome_bioproject}")

    registry = manifest.get("resource_registry", {})
    for group in ("genomes", "transcriptomes", "metabolomes"):
        if group not in registry:
            errors.append(f"Missing registry group: {group}")

    return errors


def check_url_availability(url: str, timeout_s: float = 4.0) -> dict[str, Any]:
    request = Request(url, method="HEAD", headers={"User-Agent": "BioCult-KB/0.1"})
    try:
        with urlopen(request, timeout=timeout_s) as response:
            return {"url": url, "ok": True, "status_code": response.status}
    except HTTPError as exc:
        return {"url": url, "ok": 200 <= exc.code < 400, "status_code": exc.code, "error": str(exc)}
    except URLError as exc:
        return {"url": url, "ok": False, "status_code": None, "error": str(exc.reason)}
    except TimeoutError as exc:
        return {"url": url, "ok": False, "status_code": None, "error": str(exc)}
