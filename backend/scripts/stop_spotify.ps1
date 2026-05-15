# Stop Spotify Script
# Three modes: --pause, --quit, --kill-all

param(
    [ValidateSet("pause", "quit", "kill-all")]
    [string]$Mode = "pause"
)

function Send-MediaKey {
    param([int]$Vk)

    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        [System.Windows.Forms.SendKeys]::SendWait([char]$Vk)
        return $true
    } catch {
        try {
            Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Keyboard {
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
}
"@
            $KEYEVENTF_EXTENDEDKEY = 0x0001
            $KEYEVENTF_KEYUP = 0x0002
            [Keyboard]::keybd_event($Vk, 0, $KEYEVENTF_EXTENDEDKEY, [UIntPtr]::Zero)
            [Keyboard]::keybd_event($Vk, 0, $KEYEVENTF_EXTENDEDKEY -bor $KEYEVENTF_KEYUP, [UIntPtr]::Zero)
            return $true
        } catch {
            return $false
        }
    }
}

switch ($Mode) {
    "pause" {
        $spotify = Get-Process -Name Spotify -ErrorAction SilentlyContinue
        if (-not $spotify) {
            Write-Output "Spotify is not running"
            exit 0
        }

        $VK_MEDIA_PLAY_PAUSE = 0xB3
        if (Send-MediaKey -Vk $VK_MEDIA_PLAY_PAUSE) {
            Write-Output "Spotify playback paused"
            exit 0
        } else {
            Write-Output "Error: Failed to pause Spotify"
            exit 1
        }
    }

    "quit" {
        $spotify = Get-Process -Name Spotify -ErrorAction SilentlyContinue
        if (-not $spotify) {
            Write-Output "Spotify is not running"
            exit 0
        }

        Stop-Process -Name Spotify -Force
        $crashService = Get-Process -Name SpotifyCrashService -ErrorAction SilentlyContinue
        if ($crashService) {
            Stop-Process -Name SpotifyCrashService -Force
        }

        Write-Output "Spotify has been closed"
        exit 0
    }

    "kill-all" {
        $processes = @("Spotify", "SpotifyCrashService", "SpotifyWebHelper")
        $killedAny = $false

        foreach ($proc in $processes) {
            $p = Get-Process -Name $proc -ErrorAction SilentlyContinue
            if ($p) {
                Stop-Process -Name $proc -Force
                $killedAny = $true
            }
        }

        if ($killedAny) {
            Write-Output "All Spotify processes terminated"
            exit 0
        } else {
            Write-Output "No Spotify processes were running"
            exit 0
        }
    }
}
