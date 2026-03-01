#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv-min1pipe"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
python -m pip install -e "${REPO_ROOT}[dev,vision,opt]"

echo "Created and provisioned ${VENV_DIR}"
