@echo off
title Conscious - Moshi Server Setup and Launch
echo ============================================================
echo  Conscious - Moshi Server Setup and Launch
echo ============================================================
echo.

:: ============================================================
:: Step 0: Auto-kill any stale Moshi server on port 8998
:: ============================================================
echo [0/6] Checking for stale server on port 8998...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8998 " ^| findstr "LISTENING" 2^>nul') do (
    echo   Found process %%p on port 8998 - killing it...
    taskkill /PID %%p /F >nul 2>&1
    echo   Killed stale server (PID %%p).
)
echo   Port 8998 is free.
echo.

:: ============================================================
:: Step 1: Check Python
:: ============================================================
echo [1/6] Checking Python...
C:\Python313\python.exe --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found at C:\Python313\python.exe
    echo Please install Python 3.13 to C:\Python313\
    pause
    exit /b 1
)
C:\Python313\python.exe --version
echo.

:: ============================================================
:: Step 2: Check/Install PyTorch with CUDA
:: ============================================================
echo [2/6] Checking PyTorch...
C:\Python313\python.exe -c "import torch; print(f'PyTorch {torch.__version__} - CUDA: {torch.cuda.is_available()}')" 2>nul
if errorlevel 1 (
    echo PyTorch not found. Installing PyTorch with CUDA 12.4...
    echo This is a ~2.5GB download and may take several minutes.
    C:\Python313\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    if errorlevel 1 (
        echo ERROR: Failed to install PyTorch.
        pause
        exit /b 1
    )
    echo PyTorch installed successfully.
) else (
    echo PyTorch OK.
)
echo.

:: ============================================================
:: Step 3: Check/Install Moshi
:: ============================================================
echo [3/6] Checking Moshi...
C:\Python313\python.exe -c "import moshi; print('Moshi OK')" 2>nul
if errorlevel 1 (
    echo Moshi not found. Installing...
    C:\Python313\Scripts\pip.exe install moshi
    if errorlevel 1 (
        echo ERROR: Failed to install Moshi.
        pause
        exit /b 1
    )
    echo Moshi installed successfully.
) else (
    echo Moshi OK.
)
echo.

:: ============================================================
:: Step 4: Check/Install sounddevice
:: ============================================================
echo [4/6] Checking sounddevice...
C:\Python313\python.exe -c "import sounddevice; print(f'sounddevice {sounddevice.__version__}')" 2>nul
if errorlevel 1 (
    echo sounddevice not found. Installing...
    C:\Python313\Scripts\pip.exe install sounddevice==0.5
)
echo.

:: ============================================================
:: Step 5: Check GPU VRAM and warn about conflicts
:: ============================================================
echo [5/6] Checking GPU...
C:\Python313\python.exe -c "import torch; m=torch.cuda.get_device_properties(0).total_mem//1024//1024; f=torch.cuda.mem_get_info(0)[0]//1024//1024; u=m-f; print(f'  GPU: {torch.cuda.get_device_name(0)}'); print(f'  VRAM: {m}MB total, {f}MB free, {u}MB used'); exit(0 if f>14000 else 1)" 2>nul
if errorlevel 1 (
    echo.
    echo  WARNING: Less than 14GB VRAM free!
    echo  Moshi needs ~15GB. Close GPU-heavy apps like:
    echo    - LM Studio
    echo    - Stable Diffusion
    echo    - Games
    echo.
    echo  Press any key to try anyway, or Ctrl+C to exit.
    pause >nul
)
echo.

:: ============================================================
:: Step 6: Set env vars and launch
:: ============================================================
echo [6/6] Launching Moshi server...
echo.
echo  Config:
echo    NO_TORCH_COMPILE=1   (torch.compile disabled - Py3.13 Windows)
echo    CUDA Graphs ENABLED  (real-time audio optimization)
echo.
echo  Model is ~15GB. First load takes 2-3 minutes.
echo  Wait for "Running on http://localhost:8998"
echo.
echo ============================================================
echo  USAGE TIPS:
echo    - Open http://localhost:8998 in Chrome
echo    - Click Connect (mic must be allowed in Windows Privacy Settings)
echo    - If response gets slow after 5-10 min, press F5 to refresh
echo      (this resets the conversation and restores instant responses)
echo    - To stop: close this window or press Ctrl+C
echo ============================================================
echo.

set NO_TORCH_COMPILE=1
set TORCHDYNAMO_DISABLE=1
set PYTHONUNBUFFERED=1

C:\Python313\python.exe -u -m moshi.server

echo.
echo Server stopped.
pause
