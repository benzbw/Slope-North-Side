#!/bin/bash
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "ยังไม่มี Python3 ให้ติดตั้งจาก python.org"; read; exit; }
python3 -m pip install --quiet faster-whisper
python3 start.py
