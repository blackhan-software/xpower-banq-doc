#!/bin/bash
# Build all XPower Banq paper PDFs and combine into a single document.
# Runs pdflatex twice per document to resolve internal references,
# then merges with pdfunite.

set -e

cd "$(dirname "$0")"

echo "=== Building xpower-banq.pdf ==="
pdflatex -interaction=nonstopmode xpower-banq.tex
pdflatex -interaction=nonstopmode xpower-banq.tex

echo "=== Building xpower-banq-apx.pdf ==="
pdflatex -interaction=nonstopmode xpower-banq-apx.tex
pdflatex -interaction=nonstopmode xpower-banq-apx.tex

echo "=== Building xpower-banq-lck.pdf ==="
pdflatex -interaction=nonstopmode xpower-banq-lck.tex
pdflatex -interaction=nonstopmode xpower-banq-lck.tex

echo "=== Merging into xpower-banq-all.pdf ==="
pdfunite xpower-banq.pdf xpower-banq-apx.pdf xpower-banq-lck.pdf xpower-banq-all.pdf

echo "=== Done ==="
echo "  xpower-banq.pdf      (main paper)"
echo "  xpower-banq-apx.pdf  (appendices)"
echo "  xpower-banq-lck.pdf  (lock paper)"
echo "  xpower-banq-all.pdf  (combined)"
