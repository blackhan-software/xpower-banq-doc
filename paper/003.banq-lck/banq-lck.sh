#!/bin/bash
# Build script for XPower Banq Lock paper
# Runs pdflatex twice to resolve internal references (TOC, citations, etc.)

set -e

cd "$(dirname "$0")/.."
TEX_FILE="${1-003.banq-lck/banq-lck.tex}"

pdflatex -interaction=nonstopmode -output-directory=003.banq-lck "$TEX_FILE" || true
pdflatex -interaction=nonstopmode -output-directory=003.banq-lck "$TEX_FILE" || true
[ -f 003.banq-lck/banq-lck.pdf ] || { echo "ERROR: banq-lck.pdf not produced"; exit 1; }
