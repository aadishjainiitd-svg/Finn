#!/usr/bin/env bash
set -euo pipefail
python --version
node --version
npm --version
python -c "import sys; assert sys.version_info[:2] == (3,12)"
node -e "if (+process.versions.node.split('.')[0] < 22) process.exit(1)"
pip install -r requirements.txt
npm ci --prefix frontend
npm run build --prefix frontend
