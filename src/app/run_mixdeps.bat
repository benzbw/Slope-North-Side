@echo off
cd /d "%~dp0"
echo installing > mixdeps_log.txt
python -m pip install --disable-pip-version-check -q scipy soundfile >> mixdeps_log.txt 2>&1
echo end exit=%errorlevel% >> mixdeps_log.txt
