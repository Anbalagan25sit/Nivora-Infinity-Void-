# Toggle Spotify Play/Pause Script
# Uses multiple methods: nircmd, SendKeys, Windows API

$spotify = Get-Process -Name Spotify -ErrorAction SilentlyContinue
if (-not $spotify) {
    Write-Output "Error: Spotify is not running"
    exit 1
}

# Method 1: Try nircmd first
$nircmdPaths = @(
    "$env:LOCALAPPDATA\Microsoft\WindowsApps\nircmd.exe",
    "C:\Program Files\nircmd\nircmd.exe",
    "$env:APPDATA\nircmd.exe"
)

foreach ($path in $nircmdPaths) {
    if (Test-Path $path) {
        try {
            & $path mediaplay
            exit 0
        } catch {
            continue
        }
    }
}

# Method 2: SendKeys fallback
try {
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
    [System.Windows.Forms.SendKeys]::SendWait([char]179)
    exit 0
} catch {
    # Continue to Method 3
}

# Method 3: Windows API keybd_event
try {
    Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Keyboard {
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
}
"@

    $VK_MEDIA_PLAY_PAUSE = 0xB3
    $KEYEVENTF_EXTENDEDKEY = 0x0001
    $KEYEVENTF_KEYUP = 0x0002

    [Keyboard]::keybd_event($VK_MEDIA_PLAY_PAUSE, 0, $KEYEVENTF_EXTENDEDKEY, [UIntPtr]::Zero)
    [Keyboard]::keybd_event($VK_MEDIA_PLAY_PAUSE, 0, $KEYEVENTF_EXTENDEDKEY -bor $KEYEVENTF_KEYUP, [UIntPtr]::Zero)

    exit 0
} catch {
    Write-Output "Error: Failed to toggle play/pause - $_"
    exit 1
}
