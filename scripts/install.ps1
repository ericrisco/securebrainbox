# SecureBrainBox Installer for Windows
# Usage: irm https://get.securebrainbox.dev/win | iex
# Or: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"

# Colors via Write-Host
function Write-Step($step, $msg) { Write-Host "[$step]" -ForegroundColor Blue -NoNewline; Write-Host " $msg" }
function Write-Ok($msg) { Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Dim($msg) { Write-Host $msg -ForegroundColor DarkGray }

# Banner
Write-Host ""
Write-Host "  SecureBrainBox" -ForegroundColor Blue
Write-Host "  Your private second brain that never forgets." -ForegroundColor DarkGray
Write-Host "  100% local - No cloud - Full privacy" -ForegroundColor DarkGray
Write-Host ""

# ============================================
# Step 1: Check/Install Python
# ============================================
Write-Step "1/5" "Checking Python..."

$pythonCmd = $null

# Check common Python locations
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -ge 10) {
                $pythonCmd = $cmd
                Write-Ok "Python found: $version ($cmd)"
                break
            } else {
                Write-Dim "Found $version but need 3.10+, skipping..."
            }
        }
    } catch {
        # Command not found, try next
    }
}

# Check Windows Store Python
if (-not $pythonCmd) {
    $storePython = "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe"
    if (Test-Path $storePython) {
        try {
            $version = & $storePython --version 2>&1
            if ($version -match "Python 3") {
                $pythonCmd = $storePython
                Write-Ok "Python found (Windows Store): $version"
            }
        } catch {}
    }
}

# Check winget Python
if (-not $pythonCmd) {
    $wingetPython = "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe"
    $found = Get-Item $wingetPython -ErrorAction SilentlyContinue | Sort-Object -Descending | Select-Object -First 1
    if ($found) {
        try {
            $version = & $found.FullName --version 2>&1
            if ($version -match "Python 3") {
                $pythonCmd = $found.FullName
                Write-Ok "Python found: $version"
            }
        } catch {}
    }
}

# Python not found — install it
if (-not $pythonCmd) {
    Write-Warn "Python 3.10+ not found. Installing..."
    Write-Host ""

    $installed = $false

    # Method 1: Try winget (Windows 10 1709+ / Windows 11)
    try {
        $wingetVersion = & winget --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Dim "Installing Python via winget..."
            & winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent
            if ($LASTEXITCODE -eq 0) {
                # Refresh PATH
                $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
                
                # Find the newly installed Python
                foreach ($cmd in @("python", "python3", "py")) {
                    try {
                        $version = & $cmd --version 2>&1
                        if ($version -match "Python 3") {
                            $pythonCmd = $cmd
                            $installed = $true
                            Write-Ok "Python installed via winget: $version"
                            break
                        }
                    } catch {}
                }

                # Also check default install location
                if (-not $installed) {
                    $defaultPath = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
                    if (Test-Path $defaultPath) {
                        $pythonCmd = $defaultPath
                        $installed = $true
                        Write-Ok "Python installed at: $defaultPath"
                    }
                }
            }
        }
    } catch {
        Write-Dim "winget not available, trying alternative..."
    }

    # Method 2: Download installer directly
    if (-not $installed) {
        Write-Dim "Downloading Python 3.12 installer..."
        $installerUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
        $installerPath = "$env:TEMP\python-installer.exe"

        try {
            Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
            
            Write-Dim "Running Python installer (silent, includes pip, adds to PATH)..."
            $proc = Start-Process -FilePath $installerPath -ArgumentList `
                "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_pip=1", "Include_test=0" `
                -Wait -PassThru
            
            if ($proc.ExitCode -eq 0) {
                # Refresh PATH
                $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
                
                # Find Python
                $defaultPath = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
                if (Test-Path $defaultPath) {
                    $pythonCmd = $defaultPath
                    $installed = $true
                    Write-Ok "Python 3.12 installed successfully"
                } else {
                    # Search PATH
                    foreach ($cmd in @("python", "python3")) {
                        try {
                            $version = & $cmd --version 2>&1
                            if ($version -match "Python 3") {
                                $pythonCmd = $cmd
                                $installed = $true
                                Write-Ok "Python installed: $version"
                                break
                            }
                        } catch {}
                    }
                }
            } else {
                Write-Err "Python installer failed (exit code: $($proc.ExitCode))"
            }
            
            # Cleanup
            Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Err "Failed to download Python installer: $_"
        }
    }

    if (-not $pythonCmd) {
        Write-Err "Could not install Python automatically."
        Write-Host ""
        Write-Host "Please install Python 3.12 manually from:" -ForegroundColor Yellow
        Write-Host "  https://www.python.org/downloads/" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "IMPORTANT: Check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
}

Write-Host ""

# ============================================
# Step 2: Check Docker
# ============================================
Write-Step "2/5" "Checking Docker..."

$hasDocker = $false
try {
    $dockerVersion = & docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $hasDocker = $true
        Write-Ok "Docker found: $dockerVersion"
    }
} catch {}

if (-not $hasDocker) {
    Write-Err "Docker not found!"
    Write-Host ""
    Write-Host "Please install Docker Desktop from:" -ForegroundColor Yellow
    Write-Host "  https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Check Docker running
try {
    & docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "not running" }
    Write-Ok "Docker is running"
} catch {
    Write-Err "Docker is not running! Please start Docker Desktop."
    exit 1
}

# Check Docker Compose
try {
    & docker compose version 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "Docker Compose available"
    } else { throw "no compose" }
} catch {
    Write-Err "Docker Compose not found. Please update Docker Desktop."
    exit 1
}

Write-Host ""

# ============================================
# Step 3: Download SecureBrainBox
# ============================================
Write-Step "3/5" "Downloading SecureBrainBox..."

$installDir = "$env:USERPROFILE\.securebrainbox"
$appDir = "$installDir\app"

New-Item -ItemType Directory -Path $installDir -Force | Out-Null

# Check git
$hasGit = $false
try {
    & git --version 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { $hasGit = $true }
} catch {}

if (Test-Path "$appDir\.git") {
    Write-Dim "Updating existing installation..."
    Push-Location $appDir
    & git pull --quiet origin main
    Pop-Location
} elseif ($hasGit) {
    Write-Dim "Cloning repository..."
    & git clone --depth 1 --quiet https://github.com/ericrisco/securebrainbox.git $appDir
} else {
    Write-Dim "Downloading archive..."
    $zipUrl = "https://github.com/ericrisco/securebrainbox/archive/main.zip"
    $zipPath = "$env:TEMP\securebrainbox.zip"
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
    Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP\sbb-extract" -Force
    
    if (Test-Path $appDir) { Remove-Item $appDir -Recurse -Force }
    Move-Item "$env:TEMP\sbb-extract\securebrainbox-main" $appDir
    
    Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:TEMP\sbb-extract" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Ok "SecureBrainBox downloaded"
Write-Host ""

# ============================================
# Step 4: Setup Python environment
# ============================================
Write-Step "4/5" "Setting up Python environment..."

Push-Location $appDir

# Create venv
if (-not (Test-Path ".venv")) {
    Write-Dim "Creating virtual environment..."
    & $pythonCmd -m venv .venv
}

# Activate and install
Write-Dim "Installing dependencies..."
& .venv\Scripts\pip.exe install --quiet --upgrade pip 2>&1 | Out-Null
& .venv\Scripts\pip.exe install --quiet . 2>&1 | Out-Null

Pop-Location

Write-Ok "Python environment ready"
Write-Host ""

# ============================================
# Step 5: Create CLI wrapper
# ============================================
Write-Step "5/5" "Creating CLI command..."

# Create wrapper batch file
$binDir = "$env:USERPROFILE\.local\bin"
New-Item -ItemType Directory -Path $binDir -Force | Out-Null

$wrapperContent = @"
@echo off
set INSTALL_DIR=%USERPROFILE%\.securebrainbox\app
if not exist "%INSTALL_DIR%" (
    echo SecureBrainBox not installed. Run the installer first.
    exit /b 1
)
cd /d "%INSTALL_DIR%"
call .venv\Scripts\activate.bat
python -m src.cli.main %*
"@

Set-Content -Path "$binDir\sbb.cmd" -Value $wrapperContent -Encoding ASCII

# Also create PowerShell wrapper
$psWrapper = @"
`$installDir = "`$env:USERPROFILE\.securebrainbox\app"
if (-not (Test-Path `$installDir)) {
    Write-Host "SecureBrainBox not installed." -ForegroundColor Red
    exit 1
}
Push-Location `$installDir
& .venv\Scripts\python.exe -m src.cli.main @args
Pop-Location
"@

Set-Content -Path "$binDir\sbb.ps1" -Value $psWrapper -Encoding UTF8

Write-Ok "CLI ready"
Write-Host ""

# Check if bin dir is in PATH
if ($env:PATH -notlike "*$binDir*") {
    Write-Warn "Add this directory to your PATH:"
    Write-Host ""
    Write-Host "    $binDir" -ForegroundColor Cyan
    Write-Host ""
    Write-Dim "Run this command to add it permanently:"
    Write-Host '    [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";' + $binDir + '", "User")' -ForegroundColor Cyan
    Write-Host ""
    
    # Auto-add to PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -notlike "*$binDir*") {
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$binDir", "User")
        $env:PATH = "$env:PATH;$binDir"
        Write-Ok "Added to PATH automatically"
    }
}

# ============================================
# Done!
# ============================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✅ SecureBrainBox installed successfully!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "Next step - run the setup wizard:" 
Write-Host ""
Write-Host "    sbb install" -ForegroundColor Blue
Write-Host ""
Write-Host "This will configure your Telegram bot and start services."
Write-Host ""
