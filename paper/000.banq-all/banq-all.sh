#!/bin/bash
# Build all XPower Banq paper PDFs (six standalones + the unified bundle).
# Each standalone child is built first via its own .sh script (two pdflatex
# passes). Then the bundle is built by latexmk against 000.banq-all/banq.tex,
# which uses \subfile to include the children with continuous numbering and
# a single hyperref namespace.

set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Building 001.banq-pro/banq-pro.pdf ==="
bash 001.banq-pro/banq-pro.sh

echo "=== Building 002.banq-lck/banq-lck.pdf ==="
bash 002.banq-lck/banq-lck.sh

echo "=== Building 003.banq-log/banq-log.pdf ==="
bash 003.banq-log/banq-log.sh

echo "=== Building 004.banq-mtp/banq-mtp.pdf ==="
bash 004.banq-mtp/banq-mtp.sh

echo "=== Building 005.banq-sim/banq-sim.pdf ==="
bash 005.banq-sim/banq-sim.sh

echo "=== Building 006.banq-ref/banq-ref.pdf ==="
bash 006.banq-ref/banq-ref.sh

echo "=== Building 000.banq-all/banq-all.pdf (unified bundle) ==="
# latexmk drives pdflatex with auto-determined pass count, propagating real
# build failures (including unresolved cross-references after the final pass)
# instead of the previous "|| true" suppression of all errors. Output lands
# at 000.banq-all/banq.pdf, which we rename to banq-all.pdf to match the
# legacy filename consumers expect.
latexmk -pdf -interaction=nonstopmode -halt-on-error \
        -output-directory=000.banq-all 000.banq-all/banq.tex
[ -f 000.banq-all/banq.pdf ] || { echo "ERROR: bundle PDF not produced"; exit 1; }
mv -f 000.banq-all/banq.pdf 000.banq-all/banq-all.pdf

echo "=== Done ==="
echo "  001.banq-pro/banq-pro.pdf  (protocol whitepaper)"
echo "  002.banq-lck/banq-lck.pdf  (ring-buffer time locks)"
echo "  003.banq-log/banq-log.pdf  (log-space compounding index)"
echo "  004.banq-mtp/banq-mtp.pdf  (mathematical theory & proofs)"
echo "  005.banq-sim/banq-sim.pdf  (simulations & risk analysis)"
echo "  006.banq-ref/banq-ref.pdf  (references & glossary)"
echo "  000.banq-all/banq-all.pdf  (unified bundle)"
