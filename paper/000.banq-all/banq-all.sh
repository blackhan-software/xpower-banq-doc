#!/bin/bash
# Build all XPower Banq paper PDFs and combine into a single document.
# Runs pdflatex twice per document to resolve internal references,
# then merges with pdfunite.

set -e

cd "$(dirname "$0")/.."

echo "=== Building banq-pro.pdf ==="
pdflatex -interaction=nonstopmode -output-directory=001.banq-pro 001.banq-pro/banq-pro.tex || true
pdflatex -interaction=nonstopmode -output-directory=001.banq-pro 001.banq-pro/banq-pro.tex || true
[ -f 001.banq-pro/banq-pro.pdf ] || { echo "ERROR: banq-pro.pdf not produced"; exit 1; }

echo "=== Building banq-apx.pdf ==="
pdflatex -interaction=nonstopmode -output-directory=002.banq-apx 002.banq-apx/banq-apx.tex || true
pdflatex -interaction=nonstopmode -output-directory=002.banq-apx 002.banq-apx/banq-apx.tex || true
[ -f 002.banq-apx/banq-apx.pdf ] || { echo "ERROR: banq-apx.pdf not produced"; exit 1; }

echo "=== Building banq-lck.pdf ==="
pdflatex -interaction=nonstopmode -output-directory=003.banq-lck 003.banq-lck/banq-lck.tex || true
pdflatex -interaction=nonstopmode -output-directory=003.banq-lck 003.banq-lck/banq-lck.tex || true
[ -f 003.banq-lck/banq-lck.pdf ] || { echo "ERROR: banq-lck.pdf not produced"; exit 1; }

echo "=== Building banq-log.pdf ==="
pdflatex -interaction=nonstopmode -output-directory=004.banq-log 004.banq-log/banq-log.tex || true
pdflatex -interaction=nonstopmode -output-directory=004.banq-log 004.banq-log/banq-log.tex || true
[ -f 004.banq-log/banq-log.pdf ] || { echo "ERROR: banq-log.pdf not produced"; exit 1; }

echo "=== Merging into banq-all.pdf ==="
pdfunite \
  001.banq-pro/banq-pro.pdf \
  002.banq-apx/banq-apx.pdf \
  003.banq-lck/banq-lck.pdf \
  004.banq-log/banq-log.pdf \
  000.banq-all/banq-all.pdf

echo "=== Done ==="
echo "  001.banq-pro/banq-pro.pdf  (protocol paper)"
echo "  002.banq-apx/banq-apx.pdf  (appendices)"
echo "  003.banq-lck/banq-lck.pdf  (lock paper)"
echo "  004.banq-log/banq-log.pdf  (log-index paper)"
echo "  000.banq-all/banq-all.pdf  (combined)"
