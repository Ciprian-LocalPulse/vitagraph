#!/usr/bin/env bash
# Regenerate VitaGraph_White_Paper.pdf from VitaGraph_White_Paper.md.
#
# Requires: pandoc, wkhtmltopdf (both command-line tools).
#   Debian/Ubuntu: sudo apt-get install pandoc wkhtmltopdf
#   macOS:         brew install pandoc wkhtmltopdf
#
# Usage:
#   ./build_pdf.sh
set -euo pipefail
cd "$(dirname "$0")"

pandoc VitaGraph_White_Paper.md \
  -f markdown -t html5 \
  --standalone \
  --css whitepaper.css \
  --metadata title="VitaGraph White Paper" \
  -o /tmp/vitagraph_whitepaper_render.html

wkhtmltopdf --enable-local-file-access \
  /tmp/vitagraph_whitepaper_render.html \
  VitaGraph_White_Paper.pdf

rm -f /tmp/vitagraph_whitepaper_render.html
echo "Wrote VitaGraph_White_Paper.pdf"
