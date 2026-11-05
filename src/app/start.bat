@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Slope North Side
set "PY="
where py >nul 2>nul && py -3 -c "import sys" >nul 2>nul && set "PY=py -3"
if defined PY goto havepy
python -c "import sys" >nul 2>nul && set "PY=python"
if defined PY goto havepy
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if defined PY goto havepy

echo ยังไม่มี Python ในเครื่อง กำลังติดตั้งให้อัตโนมัติ ใช้เวลาประมาณ 2-5 นาที
winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if defined PY goto havepy
echo.
echo ติดตั้ง Python อัตโนมัติไม่สำเร็จ
echo ให้ติดตั้งเองจาก python.org และติ๊ก Add python.exe to PATH แล้วดับเบิลคลิกไฟล์นี้ใหม่
pause
exit /b

:havepy
echo ใช้ Python: %PY%
echo กำลังติดตั้งตัว AI ถอดเสียง ครั้งแรกนานหน่อย ครั้งต่อไปจะข้ามไปเลย
%PY% -m pip install --quiet --disable-pip-version-check faster-whisper
if errorlevel 1 goto pipfail
%PY% -c "import demucs, torch, torchaudio, julius" >nul 2>nul
if not errorlevel 1 goto sepok
echo.
echo กำลังติดตั้งตัวแยกเสียงร้องออกจากบีต ครั้งเดียว ดาวน์โหลดราว 1GB ใช้เวลาหลายนาที
%PY% -m pip install --quiet --disable-pip-version-check demucs soundfile torchaudio
if errorlevel 1 echo ติดตั้งตัวแยกเสียงไม่สำเร็จ จะซิงค์แบบไม่แยกเสียงแทน
:sepok
%PY% -c "import transformers, uroman, pythainlp" >nul 2>nul
if not errorlevel 1 goto faok
echo.
echo กำลังติดตั้งตัวจับเวลาทีละคำ (forced alignment) ครั้งเดียว
%PY% -m pip install --quiet --disable-pip-version-check transformers uroman pythainlp
:faok
%PY% -c "import diffusers, accelerate" >nul 2>nul
if not errorlevel 1 goto imgok
echo.
echo กำลังติดตั้งตัววาดภาพปกด้วย AI ครั้งเดียว
%PY% -m pip install --quiet --disable-pip-version-check diffusers accelerate
:imgok
%PY% -c "import scipy, soundfile" >nul 2>nul
if not errorlevel 1 goto mixok
echo.
echo กำลังติดตั้งตัวมิกซ์เสียง ครั้งเดียว
%PY% -m pip install --quiet --disable-pip-version-check scipy soundfile
:mixok
echo.
echo เปิดแอปในเบราว์เซอร์... ห้ามปิดหน้าต่างนี้ระหว่างใช้งาน
echo ครั้งแรกที่กดซิงค์ จะดาวน์โหลดโมเดล AI ประมาณ 1.5GB ครั้งเดียว
%PY% start.py
pause
exit /b

:pipfail
echo.
echo ติดตั้งตัว AI ไม่สำเร็จ ถ่ายรูปข้อความด้านบนส่งให้ Claude ดูได้เลย
pause
