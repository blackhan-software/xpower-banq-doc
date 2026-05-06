#!/bin/bash
# Build script for XPower Banq Simulations & Risk Analysis paper
# Runs pdflatex twice to resolve internal references (TOC, citations, etc.)

set -e

cd "$(dirname "$0")/.."
TEX_FILE="${1-005.banq-sim/banq-sim.tex}"

pdflatex -interaction=nonstopmode -output-directory=005.banq-sim "$TEX_FILE" || true
pdflatex -interaction=nonstopmode -output-directory=005.banq-sim "$TEX_FILE" || true
[ -f 005.banq-sim/banq-sim.pdf ] || { echo "ERROR: banq-sim.pdf not produced"; exit 1; }
