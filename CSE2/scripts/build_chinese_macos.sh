#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/prepare_chinese.py
cmake -S . -B build-chinese -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$(brew --prefix)" -DCHINESE=ON -DDOCONFIG=OFF -DFIX_BUGS=ON
cmake --build build-chinese --parallel "$(sysctl -n hw.ncpu)"
python3 scripts/package_chinese_macos.py
