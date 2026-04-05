# Toggle Spotify Repeat Mode Script
# Uses Ctrl+R keyboard shortcut
# State tracked in ~/.spotify_state.json

$stateFile = "$env:USERPROFILE\.spotify_state.json"

# Initialize state file if not exists
if (-not (Test-Path $stateFile)) {
    '{"repeat":"off"}' | Out-File -FilePath $stateFile -Encoding UTF8
}

# Read current state
$state = Get-Content $stateFile -Raw | ConvertFrom-Json
$currentMode = $state.repeat
$modes = @("off", "context", "track")
$nextModeIndex = ($modes.IndexOf($currentMode) + 1) % $modes.Count
$nextMode = $modes[$nextModeIndex]

$spotify = Get-Process -Name Spotify -ErrorAction SilentlyContinue
if (-not $spotify) {
    Write-Output "Error: Spotify is not running"
    exit 1
}

# Save window state to restore later
$wasMinimized = $spotify.WindowStyle -eq "Minimized"
$hwnd = $spotify.MainWindowHandle

try {
    # Bring Spotify to foreground
    Add-Type @"
using System;
using System.Runtime.InteropServices;
public class User32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@
    [User32]::SetForegroundWindow($hwnd) | Out-Null

    Start-Sleep -Milliseconds 200

    # Send Ctrl+R
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
    [System.Windows.Forms.SendKeys]::SendWait("^r")

    Start-Sleep -Milliseconds 200

    # Restore minimized state if needed
    if ($wasMinimized) {
        # Minimize back
        # Actually, we can't easily minimize just the window without affecting behavior
        # For simplicity, just leave it foreground - user can minimize manually
    }

    # Update state file
    $state.repeat = $nextMode
    $state | ConvertTo-Json | Out-File -FilePath $stateFile -Encoding UTF8

    $modeNames = @{
        "off" = "Repeat Off"
        "context" = "Repeat All"
        "track" = "Repeat One"
    }

    Write-Output "Repeat mode: $($modeNames[$nextMode])"
    exit 0

} catch {
    Write-Output "Error: Failed to toggle repeat - $_"
    exit 1
}
