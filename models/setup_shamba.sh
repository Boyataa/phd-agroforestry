#!/usr/bin/env bash
# Install SHAMBA v1.2 (branch cirevo/initial-improvements) into models/shamba with Python 3.10.
# The SHAMBA code is NOT stored in this repository (University of Edinburgh licence/terms);
# this script fetches it from GitHub each time. Run from the repository folder:  bash models/setup_shamba.sh
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d shamba ]; then
  git clone --depth 1 -b cirevo/initial-improvements https://github.com/shamba-model/shamba.git shamba
fi
command -v uv >/dev/null || pip install --user uv
uv python install 3.10.16
cd shamba/shamba
uv venv --clear --python 3.10.16 .venv
uv pip install --python .venv/bin/python poetry
.venv/bin/poetry config virtualenvs.create false --local
VIRTUAL_ENV="$PWD/.venv" .venv/bin/poetry install --no-root
echo "SHAMBA ready. Run:  models/shamba/shamba/.venv/bin/python models/shamba/shamba/shamba_command_line.py"
echo "Note: in the cloud workspace SHAMBA cannot download climate (Open-Meteo) or soil (ISRIC SoilGrids) data;"
echo "      enter them in the input template instead (see models/README.md)."
