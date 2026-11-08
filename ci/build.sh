#!/usr/bin/env bash
# ประกอบแอปจาก src/ อย่างเดียว (ไม่ใช้ไฟล์เพลงจริง) — ใช้ใน GitHub Actions และทดสอบในเครื่อง
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/out}"
W="$(mktemp -d)"
cp "$ROOT"/src/{new.html,shell_boot.js,shell.css,shell.js,trend.html,mixstudio.html,xdata.js,explore.html} "$W"/
: > "$W/audio.b64"
mkdir -p "$W/app"
cp "$ROOT/src/app/sw.js" "$ROOT/src/app/manifest.json" "$W/app/"
cp "$ROOT/icon-192.png" "$ROOT/icon-512.png" "$W/app/"
rm -rf "$OUT"; mkdir -p "$OUT"
SNS_W="$W" SNS_APP="$W/app" SNS_FIX=off FUSED="$ROOT/src/data/fused_fa5.json" SWV=ci python3 "$ROOT/src/app/build.py" "$OUT/build" >/dev/null
python3 "$ROOT/src/app/build_web.py" "$OUT/build" "$OUT/web" ci
echo "build ok -> $OUT/web"
