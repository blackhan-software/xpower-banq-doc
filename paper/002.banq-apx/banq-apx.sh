#!/bin/bash
# Build script for XPower Banq paper
# Runs pdflatex twice to resolve internal references (TOC, citations, etc.)

set -e

cd "$(dirname "$0")/.."
TEX_FILE="${1-002.banq-apx/banq-apx.tex}"

pdflatex -interaction=nonstopmode -output-directory=002.banq-apx "$TEX_FILE" || true
pdflatex -interaction=nonstopmode -output-directory=002.banq-apx "$TEX_FILE" || true
[ -f 002.banq-apx/banq-apx.pdf ] || { echo "ERROR: banq-apx.pdf not produced"; exit 1; }
