#!/bin/bash
# Build script for XPower Banq Lock paper
# Runs pdflatex twice to resolve internal references (TOC, citations, etc.)

set -e

cd "$(dirname "$0")"
TEX_FILE="${1-xpower-banq-lck.tex}"

pdflatex -interaction=nonstopmode "$TEX_FILE"
pdflatex -interaction=nonstopmode "$TEX_FILE"
