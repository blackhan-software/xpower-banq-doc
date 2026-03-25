#!/bin/bash
# Build script for XPower Banq References & Glossary paper
# Runs pdflatex twice to resolve internal references (TOC, citations, etc.)
# Note: banq-ref's glossary cross-references theorems/definitions in
# banq-mtp and banq-sim. Standalone builds resolve these via the xr package
# reading sibling .aux files; ensure those PDFs are built first or the
# cross-doc refs will render as "??".

set -e

cd "$(dirname "$0")/.."
TEX_FILE="${1-006.banq-ref/banq-ref.tex}"

pdflatex -interaction=nonstopmode -output-directory=006.banq-ref "$TEX_FILE" || true
pdflatex -interaction=nonstopmode -output-directory=006.banq-ref "$TEX_FILE" || true
[ -f 006.banq-ref/banq-ref.pdf ] || { echo "ERROR: banq-ref.pdf not produced"; exit 1; }
