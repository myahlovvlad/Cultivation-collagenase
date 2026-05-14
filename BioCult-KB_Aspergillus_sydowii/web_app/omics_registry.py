from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class OmicsResource:
    label: str
    accession: str
    url: str
    kind: str
    source: str
    notes: str
    verification_status: str
    download_hint: str


GENOME_RESOURCES = [
    OmicsResource(
        label="A. sydowii CBS 593.65 assembly Aspsy1",
        accession="GCA_001890705.1",
        url="https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_001890705.1",
        kind="genome-assembly",
        source="NCBI Datasets",
        notes="Primary GenBank assembly candidate for the reproducible genome package ingest.",
        verification_status="verified",
        download_hint="datasets download genome accession GCA_001890705.1 --include genome,gff3,rna,cds,protein,gbff,seq-report",
    ),
    OmicsResource(
        label="A. sydowii CBS 593.65 RefSeq assembly",
        accession="GCF_001890705.1",
        url="https://www.ncbi.nlm.nih.gov/assembly/GCF_001890705.1",
        kind="genome-assembly",
        source="NCBI Assembly",
        notes="RefSeq mirror for the same strain context; useful for cross-checking annotation provenance.",
        verification_status="verified",
        download_hint="datasets download genome accession GCF_001890705.1 --include genome,gff3,rna,cds,protein,gbff,seq-report",
    ),
    OmicsResource(
        label="A. sydowii ASM3419260v1",
        accession="GCA_034192605.1",
        url="https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_034192605.1",
        kind="genome-assembly",
        source="NCBI Datasets",
        notes="Additional public assembly for comparative checks before strain-specific modeling.",
        verification_status="verified",
        download_hint="datasets download genome accession GCA_034192605.1 --include genome,gff3,rna,cds,protein,gbff,seq-report",
    ),
    OmicsResource(
        label="A. sydowii ASM5094813v1",
        accession="GCA_050948135.1",
        url="https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_050948135.1",
        kind="genome-assembly",
        source="NCBI Datasets",
        notes="Additional public assembly; keep as a registry source but do not mix with the primary model without provenance.",
        verification_status="verified",
        download_hint="datasets download genome accession GCA_050948135.1 --include genome,gff3,rna,cds,protein,gbff,seq-report",
    ),
    OmicsResource(
        label="A. sydowii AS31 assembly",
        accession="GCA_026319385.1",
        url="https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_026319385.1",
        kind="genome-assembly",
        source="NCBI Datasets",
        notes="Verified public assembly for an alternate strain context.",
        verification_status="verified",
        download_hint="datasets download genome accession GCA_026319385.1 --include genome,gff3,rna,cds,protein,gbff,seq-report",
    ),
]


TRANSCRIPTOME_RESOURCES = [
    OmicsResource(
        label="A. sydowii H-1 RNA-seq BioProject",
        accession="PRJNA542911",
        url="https://www.ncbi.nlm.nih.gov/sra/?term=PRJNA542911",
        kind="rna-seq-bioproject",
        source="NCBI SRA",
        notes="RNA-seq entry point referenced in the project context; run discovery should be done through SRA RunInfo.",
        verification_status="verified-publication",
        download_hint="esearch -db sra -query 'PRJNA542911[BioProject]' | efetch -format runinfo",
    ),
]


METABOLOME_RESOURCES = [
    OmicsResource(
        label="A. sydowii co-culture metabolomics paper",
        accession="PMC7881642",
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC7881642/",
        kind="publication",
        source="PubMed Central",
        notes="Verified provenance reference for metabolomics workflow design and metadata cross-checks.",
        verification_status="verified-reference",
        download_hint="Use as provenance source; do not treat as a raw data archive.",
    ),
    OmicsResource(
        label="MassIVE metabolomics candidate endpoint",
        accession="MSV-candidate",
        url="https://massive.ucsd.edu/ProteoSAFe/dataset.jsp?task=f65bfac6208a436fab483cd284f52a33",
        kind="dataset-browser",
        source="MassIVE",
        notes="Candidate endpoint from the context file; requires manual organism/sample metadata validation.",
        verification_status="candidate",
        download_hint="Validate dataset metadata before any automated raw download.",
    ),
    OmicsResource(
        label="GNPS2 dataset browser candidate",
        accession="ST001257",
        url="https://explorer.gnps2.org/ST001257",
        kind="dataset-browser",
        source="GNPS2",
        notes="Candidate browser endpoint; useful for dereplication context after manual validation.",
        verification_status="candidate",
        download_hint="Use as a candidate browser endpoint only until sample metadata is confirmed.",
    ),
    OmicsResource(
        label="OmicsDI GNPS dataset index",
        accession="MSV000087365",
        url="https://www.omicsdi.org/dataset/gnps/MSV000087365",
        kind="dataset-index",
        source="OmicsDI",
        notes="Candidate index entry that may link external GNPS/MassIVE metadata.",
        verification_status="candidate",
        download_hint="Cross-check organism, strain, sample provenance, and publication link.",
    ),
    OmicsResource(
        label="Aspergillus Metabolome Database paper",
        accession="AMD-reference",
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC8156648/",
        kind="knowledgebase",
        source="PubMed Central",
        notes="Reference source for Aspergillus metabolite annotation support.",
        verification_status="verified-reference",
        download_hint="Use as annotation knowledgebase, not as project raw data.",
    ),
]


def _filter_by_status(items: Iterable[OmicsResource], allowed_statuses: set[str]) -> list[dict[str, Any]]:
    return [asdict(item) for item in items if item.verification_status in allowed_statuses]


def get_verified_resources() -> dict[str, list[dict[str, Any]]]:
    return {
        "genomes": _filter_by_status(GENOME_RESOURCES, {"verified"}),
        "transcriptomes": _filter_by_status(TRANSCRIPTOME_RESOURCES, {"verified", "verified-publication"}),
        "metabolomes": _filter_by_status(METABOLOME_RESOURCES, {"verified", "verified-reference"}),
    }


def get_candidate_resources() -> dict[str, list[dict[str, Any]]]:
    return {
        "genomes": _filter_by_status(GENOME_RESOURCES, {"candidate", "publication-only"}),
        "transcriptomes": _filter_by_status(TRANSCRIPTOME_RESOURCES, {"candidate", "publication-only"}),
        "metabolomes": _filter_by_status(METABOLOME_RESOURCES, {"candidate", "publication-only"}),
    }


def get_downloadable_resources() -> dict[str, list[dict[str, Any]]]:
    verified = get_verified_resources()
    return {
        group: [item for item in items if item.get("download_hint")]
        for group, items in verified.items()
    }


def serialize_registry() -> dict[str, Any]:
    return {
        "genomes": [asdict(item) for item in GENOME_RESOURCES],
        "transcriptomes": [asdict(item) for item in TRANSCRIPTOME_RESOURCES],
        "metabolomes": [asdict(item) for item in METABOLOME_RESOURCES],
        "verified": get_verified_resources(),
        "candidate": get_candidate_resources(),
        "downloadable": get_downloadable_resources(),
    }
