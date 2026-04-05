# Toggle Spotify Shuffle Script
# Uses Ctrl+S keyboard shortcut
# State tracked in ~/.spotify_state.json

$stateFile = "$env:USERPROFILE\.spotify_state.json"

# Initialize state file if not exists
if (-not (Test-Path $stateFile)) {
    '{"shuffle":false}' | Out-File -FilePath $stateFile -Encoding UTF8
}

# Read current state
$state = Get-Content $stateFile -Raw | ConvertFrom-Json
$currentShuffle = $state.shuffle
$nextShuffle = -not $currentShuffle

$spotify = Get-Process -Name Spotify -ErrorAction SilentlyContinue
if (-not $spotify) {
    Write-Output "Error: Spotify is not running"
    exit 1
}

# Save window state
$wasMinimized = $spotify.WindowStyle -eq "Minimized"
$hwnd = $spotify.MainWindowHandle

try {
    # Bring Spotify to foreground
    Add-Type @"
using System;
using System.Runtime.InteropServices;
public class User32 {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@
    [User32]::SetForegroundWindow($hwnd) | Out-Null

    Start-Sleep -Milliseconds 200

    # Send Ctrl+S
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
    [System.Windows.Forms.SendKeys]::SendWait("^s")

    Start-Sleep -Milliseconds 200

    # Update state file
    $state.shuffle = $nextShuffle
    $state | ConvertTo-Json | Out-File -FilePath $stateFile -Encoding UTF8

    if ($nextShuffle) {
        Write-Output "Shuffle is now ON"
    } else {
        Write-Output "Shuffle is now OFF"
    }

    exit 0

} catch {
    Write-Output "Error: Failed to toggle shuffle - $_"
    exit 1
}
