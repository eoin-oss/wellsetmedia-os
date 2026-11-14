#!/bin/zsh
# one-shot VSL run: build into Resolve project 'vsl auto' -> readability gate -> render to Desktop
set -e
cd "${0:A:h}"
python3 build_vsl.py build "vsl auto"
python3 ../../engine/readable.py ../../jobs/vsl/text_manifest.json
python3 render_vsl.py ~/Desktop VSL
