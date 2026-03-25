#!/bin/bash
# Build script for XPower Banq Mathematical Theory & Proofs paper
# Runs pdflatex twice to resolve internal references (TOC, citations, etc.)

set -e

cd "$(dirname "$0")/.."
TEX_FILE="${1-004.banq-mtp/banq-mtp.tex}"

pdflatex -interaction=nonstopmode -output-directory=004.banq-mtp "$TEX_FILE" || true
pdflatex -interaction=nonstopmode -output-directory=004.banq-mtp "$TEX_FILE" || true
[ -f 004.banq-mtp/banq-mtp.pdf ] || { echo "ERROR: banq-mtp.pdf not produced"; exit 1; }
