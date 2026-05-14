#!/usr/bin/env bash
set -euo pipefail

SAMPLE_SHEET="${1:-C:\Users\Vlad Myahlov\Documents\GitHub\Cultivation-collagenase\BioCult-KB_Aspergillus_sydowii\web_app\data\omics\aspergillus_sydowii\reports\PRJNA542911_sample_sheet.tsv}"
OUT_DIR="${2:-fastq}"
mkdir -p "$OUT_DIR"

tail -n +2 "$SAMPLE_SHEET" | while IFS=$'\t' read -r sample_id run_accession bioproject condition replicate notes; do
  if [[ -z "$run_accession" ]]; then
    continue
  fi
  prefetch "$run_accession"
  fasterq-dump "$run_accession" --split-files --outdir "$OUT_DIR"
done
