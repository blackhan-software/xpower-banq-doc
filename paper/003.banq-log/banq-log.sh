#!/bin/bash
# Build script for XPower Banq Log-Index paper
# Runs pdflatex twice to resolve internal references (TOC, citations, etc.)

set -e

cd "$(dirname "$0")/.."
TEX_FILE="${1-003.banq-log/banq-log.tex}"

pdflatex -interaction=nonstopmode -output-directory=003.banq-log "$TEX_FILE" || true
pdflatex -interaction=nonstopmode -output-directory=003.banq-log "$TEX_FILE" || true
[ -f 003.banq-log/banq-log.pdf ] || { echo "ERROR: banq-log.pdf not produced"; exit 1; }
