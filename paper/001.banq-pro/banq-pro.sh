#!/bin/bash
# Build script for XPower Banq paper
# Runs pdflatex twice to resolve internal references (TOC, citations, etc.)

set -e

cd "$(dirname "$0")/.."
TEX_FILE="${1-001.banq-pro/banq-pro.tex}"

pdflatex -interaction=nonstopmode -output-directory=001.banq-pro "$TEX_FILE" || true
pdflatex -interaction=nonstopmode -output-directory=001.banq-pro "$TEX_FILE" || true
[ -f 001.banq-pro/banq-pro.pdf ] || { echo "ERROR: banq-pro.pdf not produced"; exit 1; }
