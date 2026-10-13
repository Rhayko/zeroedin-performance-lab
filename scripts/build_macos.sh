#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_ROOT"
export PYINSTALLER_CONFIG_DIR="$PROJECT_ROOT/.pyinstaller-cache"
BUILD_ROOT=$(mktemp -d /private/tmp/zeroedin-macos-build.XXXXXX)
trap 'rm -rf "$BUILD_ROOT"' EXIT

npm --prefix frontend run build
.venv/bin/pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "ZeroedIn Performance Lab" \
  --osx-bundle-identifier "com.zeroedin.performancelab" \
  --distpath "$BUILD_ROOT/dist" \
  --workpath "$BUILD_ROOT/build" \
  --specpath "$BUILD_ROOT" \
  --add-data "$PROJECT_ROOT/frontend/dist:frontend/dist" \
  --collect-all uvicorn \
  desktop_launcher.py

mkdir -p release
codesign --force --deep --sign - "$BUILD_ROOT/dist/ZeroedIn Performance Lab.app"
codesign --verify --deep --strict "$BUILD_ROOT/dist/ZeroedIn Performance Lab.app"
mv "release/ZeroedIn-Performance-Lab-macOS.zip" "$BUILD_ROOT/previous-release.zip" 2>/dev/null || true
ditto -c -k --keepParent \
  "$BUILD_ROOT/dist/ZeroedIn Performance Lab.app" \
  "release/ZeroedIn-Performance-Lab-macOS.zip"

echo "Built release/ZeroedIn-Performance-Lab-macOS.zip"
