#!/bin/bash
# Build script for XPower Banq paper
# Runs pdflatex twice to resolve internal references (TOC, citations, etc.)

set -e

cd "$(dirname "$0")"
TEX_FILE="${1-xpower-banq-apx.tex}"

pdflatex -interaction=nonstopmode "$TEX_FILE"
pdflatex -interaction=nonstopmode "$TEX_FILE"
