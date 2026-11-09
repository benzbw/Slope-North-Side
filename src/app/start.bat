@echo off
cd /d "%~dp0"
title Slope North Side - sync server (keep this window open)
set "PY="
where py >nul 2>nul && py -3 -c "import sys" >nul 2>nul && set "PY=py -3"
if defined PY goto havepy
python -c "import sys" >nul 2>nul && set "PY=python"
if defined PY goto havepy
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if defined PY goto havepy
echo Python not found. Installing Python 3.12 (2-5 minutes)...
winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if defined PY goto havepy
echo.
echo Could not install Python automatically.
echo Install it from python.org (tick "Add python.exe to PATH"), then run this file again.
pause
exit /b

:havepy
echo Using Python: %PY%
%PY% -c "import faster_whisper" >nul 2>nul
if not errorlevel 1 goto fwok
echo [1/5] Installing speech AI (first time only)...
%PY% -m pip install --quiet --disable-pip-version-check faster-whisper
if errorlevel 1 goto pipfail
:fwok
%PY% -c "import demucs, torch, torchaudio, julius" >nul 2>nul
if not errorlevel 1 goto sepok
echo [2/5] Installing vocal separator (about 1GB, first time only)...
%PY% -m pip install --quiet --disable-pip-version-check demucs soundfile torchaudio
if errorlevel 1 echo Vocal separator failed to install - sync will run without it.
:sepok
%PY% -c "import transformers, uroman, pythainlp" >nul 2>nul
if not errorlevel 1 goto faok
echo [3/5] Installing word-by-word aligner (first time only)...
%PY% -m pip install --quiet --disable-pip-version-check transformers uroman pythainlp
:faok
%PY% -c "import diffusers, accelerate" >nul 2>nul
if not errorlevel 1 goto imgok
echo [4/5] Installing AI cover painter (first time only)...
%PY% -m pip install --quiet --disable-pip-version-check diffusers accelerate
:imgok
%PY% -c "import scipy, soundfile" >nul 2>nul
if not errorlevel 1 goto mixok
echo [5/5] Installing mixer (first time only)...
%PY% -m pip install --quiet --disable-pip-version-check scipy soundfile
:mixok
%PY% -c "import yt_dlp" >nul 2>nul
if not errorlevel 1 goto ytok
echo [6/6] Installing YouTube song fetcher (first time only)...
%PY% -m pip install --quiet --disable-pip-version-check -U yt-dlp
:ytok
echo.
echo ==========================================================
echo  Slope North Side server is starting: http://localhost:8790
echo  KEEP THIS WINDOW OPEN while you use the app.
echo  First sync downloads the AI models once (about 1.5GB).
echo ==========================================================
set PYTHONIOENCODING=utf-8
%PY% start.py
pause
exit /b

:pipfail
echo.
echo Installing the speech AI failed. Take a photo of the text above and send it to Claude.
pause
