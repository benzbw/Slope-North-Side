@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo installing > img_log.txt
python -m pip install --disable-pip-version-check -q diffusers accelerate >> img_log.txt 2>&1
echo start >> img_log.txt
python img_gen.py >> img_log.txt 2>&1
echo end exit=%errorlevel% >> img_log.txt
