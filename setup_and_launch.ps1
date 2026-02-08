# Conscious - Moshi Server Setup and Launch (PowerShell)
# Run: .\setup_and_launch.ps1
# Or: powershell -ExecutionPolicy Bypass -File setup_and_launch.ps1

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Conscious - Moshi Server"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Conscious - Moshi Server Setup and Launch" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $pyVer = C:\Python313\python.exe --version 2>&1
    Write-Host "  $pyVer" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Install Python 3.10-3.13." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Check/Install PyTorch
Write-Host "[2/5] Checking PyTorch..." -ForegroundColor Yellow
$torchOK = C:\Python313\python.exe -c "import torch; print(f'PyTorch {torch.__version__} - CUDA: {torch.cuda.is_available()}')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  PyTorch not found. Installing with CUDA 12.4..." -ForegroundColor Yellow
    C:\Python313\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to install PyTorch." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "  PyTorch installed successfully." -ForegroundColor Green
} else {
    Write-Host "  $torchOK" -ForegroundColor Green
}

# Step 3: Check/Install Moshi
Write-Host "[3/5] Checking Moshi..." -ForegroundColor Yellow
$moshiOK = C:\Python313\python.exe -c "import moshi; print('Moshi OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Moshi not found. Installing..." -ForegroundColor Yellow
    C:\Python313\Scripts\pip.exe install moshi
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to install Moshi." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "  Moshi installed successfully." -ForegroundColor Green
} else {
    Write-Host "  Moshi already installed." -ForegroundColor Green
}

# Step 4: Check/Install sounddevice
Write-Host "[4/5] Checking sounddevice..." -ForegroundColor Yellow
$sdOK = C:\Python313\python.exe -c "import sounddevice; print(f'sounddevice {sounddevice.__version__}')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  sounddevice not found. Installing..." -ForegroundColor Yellow
    C:\Python313\Scripts\pip.exe install "sounddevice==0.5"
} else {
    Write-Host "  $sdOK" -ForegroundColor Green
}

# Step 5: GPU check
Write-Host "[5/5] Checking GPU..." -ForegroundColor Yellow
$gpuInfo = C:\Python313\python.exe -c "import torch; print(f'{torch.cuda.get_device_name(0)} - {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB VRAM')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  $gpuInfo" -ForegroundColor Green
}

# Check VRAM availability
$nvidiaSmi = nvidia-smi --query-gpu=memory.used,memory.total,memory.free --format=csv,noheader,nounits 2>&1
if ($nvidiaSmi -match "(\d+), (\d+), (\d+)") {
    $used = [int]$Matches[1]
    $total = [int]$Matches[2]
    $free = [int]$Matches[3]
    Write-Host "  VRAM: ${used}MB used / ${total}MB total / ${free}MB free" -ForegroundColor Green
    if ($free -lt 15000) {
        Write-Host ""
        Write-Host "  WARNING: Moshi needs ~15GB VRAM. Only ${free}MB free." -ForegroundColor Red
        Write-Host "  Close other GPU apps (LM Studio, etc.) and try again." -ForegroundColor Red
        Read-Host "Press Enter to continue anyway, or Ctrl+C to exit"
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Launching Moshi Server" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  NO_TORCH_COMPILE=1  (disables torch.compile for Python 3.13 Windows)" -ForegroundColor DarkGray
Write-Host "  TORCHDYNAMO_DISABLE=1 (safety net for triton incompatibility)" -ForegroundColor DarkGray
Write-Host "  CUDA Graphs ENABLED (works on Python 3.13, needed for real-time audio)" -ForegroundColor Green
Write-Host ""
Write-Host "  Model is ~15GB. Loading takes 2-3 minutes." -ForegroundColor Yellow
Write-Host "  Wait for: 'Running on http://localhost:8998'" -ForegroundColor Yellow
Write-Host "  Then open http://localhost:8998 in Chrome and click Connect." -ForegroundColor Yellow
Write-Host ""

# Set environment variables
$env:NO_TORCH_COMPILE = "1"
$env:TORCHDYNAMO_DISABLE = "1"
$env:PYTHONUNBUFFERED = "1"

# Launch
C:\Python313\python.exe -u -m moshi.server

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
