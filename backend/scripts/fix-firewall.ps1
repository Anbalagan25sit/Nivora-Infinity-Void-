# ============================================================================
# Nivora LiveKit Firewall Fix
# Run this as Administrator to allow Python through Windows Firewall
# ============================================================================

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Nivora LiveKit - Windows Firewall Fix" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Python executable path
$pythonPath = "C:\Users\Nivorichi\AppData\Local\Programs\Python\Python313\python.exe"

if (-not (Test-Path $pythonPath)) {
    Write-Host "❌ ERROR: Python not found at: $pythonPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please update the path in this script to your Python installation." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✓ Python found: $pythonPath" -ForegroundColor Green
Write-Host ""

# Remove old rules if they exist
Write-Host "Removing old firewall rules (if any)..." -ForegroundColor Cyan
Remove-NetFirewallRule -DisplayName "Python LiveKit*" -ErrorAction SilentlyContinue

# Create new firewall rules
Write-Host "Creating new firewall rules..." -ForegroundColor Cyan

try {
    # Inbound rule
    New-NetFirewallRule `
        -DisplayName "Python LiveKit Inbound" `
        -Direction Inbound `
        -Program $pythonPath `
        -Action Allow `
        -Protocol TCP `
        -Profile Any `
        -Enabled True | Out-Null

    Write-Host "  ✓ Inbound rule created" -ForegroundColor Green

    # Outbound rule
    New-NetFirewallRule `
        -DisplayName "Python LiveKit Outbound" `
        -Direction Outbound `
        -Program $pythonPath `
        -Action Allow `
        -Protocol TCP `
        -Profile Any `
        -Enabled True | Out-Null

    Write-Host "  ✓ Outbound rule created" -ForegroundColor Green

    # UDP rule (for media)
    New-NetFirewallRule `
        -DisplayName "Python LiveKit UDP" `
        -Direction Inbound `
        -Program $pythonPath `
        -Action Allow `
        -Protocol UDP `
        -Profile Any `
        -Enabled True | Out-Null

    Write-Host "  ✓ UDP rule created" -ForegroundColor Green

} catch {
    Write-Host "❌ ERROR creating firewall rules: $_" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✓ Firewall rules successfully created!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Python is now allowed through Windows Firewall." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run: python agent.py dev" -ForegroundColor White
Write-Host "  2. The 'Connection lost' error should be fixed!" -ForegroundColor White
Write-Host ""

pause
