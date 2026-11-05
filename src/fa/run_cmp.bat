@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo start > fa_log.txt
python fa.py royin thai2rom uroman >> fa_log.txt 2>&1
echo end exit=%errorlevel% >> fa_log.txt
