# Go to Previous Track Script
# Uses nircmd, SendKeys, or Windows API

$spotify = Get-Process -Name Spotify -ErrorAction SilentlyContinue
if (-not $spotify) {
    Write-Output "Error: Spotify is not running"
    exit 1
}

# Method 1: Try nircmd
$nircmdPaths = @(
    "$env:LOCALAPPDATA\Microsoft\WindowsApps\nircmd.exe",
    "C:\Program Files\nircmd\nircmd.exe",
    "$env:APPDATA\nircmd.exe"
)

foreach ($path in $nircmdPaths) {
    if (Test-Path $path) {
        try {
            & $path mediaprev
            Start-Sleep -Milliseconds 500
            $title = $spotify.MainWindowTitle
            if ($title -and $title -notlike "Spotify*") {
                Write-Output "Now playing: $title"
            }
            exit 0
        } catch {
            continue
        }
    }
}

# Method 2: SendKeys fallback (char 177 = VK_MEDIA_PREV_TRACK)
try {
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
    [System.Windows.Forms.SendKeys]::SendWait([char]177)
    Start-Sleep -Milliseconds 500
    $spotify = Get-Process -Name Spotify -ErrorAction SilentlyContinue
    if ($spotify) {
        $title = $spotify.MainWindowTitle
        if ($title -and $title -notlike "Spotify*") {
            Write-Output "Now playing: $title"
        }
    }
    exit 0
} catch {
    # Continue to Method 3
}

# Method 3: Windows API
try {
    Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Keyboard {
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
}
"@

    $VK_MEDIA_PREV_TRACK = 0xB1
    $KEYEVENTF_EXTENDEDKEY = 0x0001
    $KEYEVENTF_KEYUP = 0x0002

    [Keyboard]::keybd_event($VK_MEDIA_PREV_TRACK, 0, $KEYEVENTF_EXTENDEDKEY, [UIntPtr]::Zero)
    [Keyboard]::keybd_event($VK_MEDIA_PREV_TRACK, 0, $KEYEVENTF_EXTENDEDKEY -bor $KEYEVENTF_KEYUP, [UIntPtr]::Zero)

    Start-Sleep -Milliseconds 500
    $spotify = Get-Process -Name Spotify -ErrorAction SilentlyContinue
    if ($spotify) {
        $title = $spotify.MainWindowTitle
        if ($title -and $title -notlike "Spotify*") {
            Write-Output "Now playing: $title"
        }
    }
    exit 0
} catch {
    Write-Output "Error: Failed to go to previous track - $_"
    exit 1
}
