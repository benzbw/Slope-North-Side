@echo off
cd /d "%~dp0"
echo [%date% %time%] installing > fa_log.txt
python -m pip install --disable-pip-version-check -q transformers uroman pythainlp >> fa_log.txt 2>&1
echo [%date% %time%] start >> fa_log.txt
set PYTHONIOENCODING=utf-8
python fa.py >> fa_log.txt 2>&1
echo [%date% %time%] end exit=%errorlevel% >> fa_log.txt
