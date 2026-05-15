# Spotify Volume Control Script
# Methods: COM interfaces (spotify-specific) or nircmd (system volume)

param(
    [ValidateSet("set", "up", "down", "mute", "unmute")]
    [string]$Action,

    [int]$Value = 10
)

# Convert percentage (0-100) to Windows audio scalar (0.0-1.0)
function Convert-ToScalar {
    param([int]$Percent)
    return [math]::Min(100, [math]::Max(0, $Percent)) / 100.0
}

# Method 1: Control Spotify specifically using Audio Session API
function Set-SpotifyVolume {
    param([double]$Volume)

    try {
        # Load required COM types
        Add-Type @"
using System;
using System.Runtime.InteropServices;

[Guid("bfb7ff88-7239-4fc9-8fa2-07c950be9c6d"),
 InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioSessionControl2 {
    void GetState(out AudioSessionState pRetVal);
    void GetDisplayName([Out, MarshalAs(UnmanagedType.LPWStr)] out string pRetVal);
    void SetDisplayName([MarshalAs(UnmanagedType.LPWStr)] string Value, Guid EventContext);
    void GetIconPath([Out, MarshalAs(UnmanagedType.LPWStr)] out string pRetVal);
    void SetIconPath([MarshalAs(UnmanagedType.LPWStr)] string Value, Guid EventContext);
    void GetGroupingParam(out Guid pRetVal);
    void SetGroupingParam(ref Guid Override, Guid EventContext);
    void RegisterAudioSessionNotification(IAudioSessionEvents NewNotifications);
    void UnregisterAudioSessionNotification(IAudioSessionEvents NewNotifications);
    void GetSessionIdentifier([Out, MarshalAs(UnmanagedType.LPWStr)] out string pRetVal);
    void GetSessionInstanceIdentifier([Out, MarshalAs(UnmanagedType.LPWStr)] out string pRetVal);
    void GetProcessId(out uint pRetVal);
    void IsSystemSoundsSession();
    void SetDuckingPreference(bool optOut);
}

[Guid("e2f5bb11-0570-40ca-acdd-3a417ab477c7"),
 InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface ISimpleAudioVolume {
    void SetMasterVolume(float fLevel, Guid EventContext);
    void GetMasterVolume(out float pfLevel);
    void SetMute(bool bMute, Guid EventContext);
    void GetMute(out bool pbMute);
}

[Guid("73f34bea-4426-4d5c-a76c-78b265b3e982"),
 InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioSessionEnumerator {
    void GetCount(out int SessionCount);
    void GetSession(int SessionCount, out IAudioSessionControl2 Session);
}

[Guid("bfa971f1-4d5e-40bb-935e-967039bfb424"),
 InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioSessionManager2 {
    void GetSessionEnumerator(out IAudioSessionEnumerator SessionEnum);
    void RegisterSessionNotification(IAudioSessionNotifications SessionNotification);
    void UnregisterSessionNotification(IAudioSessionNotifications SessionNotification);
}

[Guid("951744363-3b21-4a77-9b8b-55171b3c320d"),
 InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice {
    void Activate(ref Guid iid, uint dwClsCtx, IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface);
}

[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"),
 InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator {
    int EnumAudioEndpoints(int dataFlow, int dwStateMask, out int Devices);
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppDevice);
}

public class Audio {
    [DllImport("ole32.dll")]
    public static extern int CoCreateInstance([MarshalAs(UnmanagedType.LPStruct)] Guid clsid,
        [MarshalAs(UnmanagedType.IUnknown)] object inner, uint context, [MarshalAs(UnmanagedType.LPStruct)] Guid iid, [MarshalAs(UnmanagedType.IUnknown)] out object ppv);

    [DllImport("ole32.dll")]
    public static extern void CoTaskMemFree(IntPtr pv);

    [StructLayout(LayoutKind.Sequential)]
    public struct PROPERTYKEY {
        public Guid fmtid;
        public uint pid;
    }
}

[StructLayout(LayoutKind.Sequential)]
struct AudioSessionState {
    public int Value;
}
"@

        # CLSIDs
        $CLSID_MMDeviceEnumerator = [Guid]::new("BCDE0395-E52F-467C-8E3D-C4579291692E")
        $IID_IMMDeviceEnumerator = [Guid]::new("A95664D2-9614-4F35-A746-DE8DB63617E6")
        $IID_IAudioSessionManager2 = [Guid]::new("77AA99A0-F75D-4628-920C-6C0D65069F9D")

        # Create device enumerator
        $enumerator = [Activator]::CreateInstance([type]::GetTypeFromCLSID($CLSID_MMDeviceEnumerator))

        # Get default audio endpoint (eRender = 0, eMultimedia = 1)
        $device = $enumerator.GetDefaultAudioEndpoint(0, 1, [ref]$IID_IMMDeviceEnumerator)

        # Get session manager
        $sessionManager = $device.Activate([ref]$IID_IAudioSessionManager2, 23, [IntPtr]::Zero, [ref]$null)

        # Get session enumerator
        $sessionEnum = $sessionManager.GetSessionEnumerator()
        $sessionCount = 0
        $sessionEnum.GetCount([ref]$sessionCount)

        # Find Spotify session
        for ($i = 0; $i -lt $sessionCount; $i++) {
            $session = $null
            $sessionEnum.GetSession($i, [ref]$session)

            if ($session -eq $null) {
                continue
            }

            # Get process ID
            $procId = 0
            try {
                [void]$session.GetProcessId([ref]$procId)
            } catch {
                continue
            }

            # Check if this is Spotify
            try {
                $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
                if ($proc -and $proc.ProcessName -like "*Spotify*") {
                    $simpleVolume = $session -as [ISimpleAudioVolume]

                    if ($Action -eq "set") {
                        $simpleVolume.SetMasterVolume($Volume, [Guid]::Empty)
                    } elseif ($Action -eq "up" -or $Action -eq "down") {
                        $currentVolume = 0.0
                        $simpleVolume.GetMasterVolume([ref]$currentVolume)
                        $newVolume = $currentVolume + ($Value / 100.0 * ($Action -eq "up" ? 1 : -1))
                        $newVolume = [math]::Max(0, [math]::Min(1, $newVolume))
                        $simpleVolume.SetMasterVolume($newVolume, [Guid]::Empty)
                    } elseif ($Action -eq "mute") {
                        $simpleVolume.SetMute($true, [Guid]::Empty)
                    } elseif ($Action -eq "unmute") {
                        $simpleVolume.SetMute($false, [Guid]::Empty)
                    }

                    # Get final volume for printing
                    if ($Action -ne "mute" -and $Action -ne "unmute") {
                        $finalVolume = 0.0
                        $simpleVolume.GetMasterVolume([ref]$finalVolume)
                        $percent = [math]::Round($finalVolume * 100)
                        Write-Output "Spotify volume: ${percent}%"
                    } else {
                        $isMuted = $false
                        $simpleVolume.GetMute([ref]$isMuted)
                        if ($isMuted) {
                            Write-Output "Spotify volume: muted"
                        } else {
                            Write-Output "Spotify volume: unmuted"
                        }
                    }

                    return 0
                }
            } catch {
                continue
            }
        }

        Write-Output "Error: Spotify audio session not found (is Spotify running?)"
        return 1

    } catch {
        Write-Output "COM method failed: $_"
        Write-Output "Falling back to nircmd..."
        return 2
    }
}

# Method 2: Use nircmd for system volume
function Set-VolumeNircmd {
    param([string]$Action, [int]$Value)

    $nircmdPaths = @(
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\nircmd.exe",
        "C:\Program Files\nircmd\nircmd.exe",
        "$env:APPDATA\nircmd.exe"
    )

    foreach ($path in $nircmdPaths) {
        if (Test-Path $path) {
            switch ($Action) {
                "set" {
                    $sysVolume = [math]::Round($Value / 100.0 * 65535)
                    & $path setsysvolume $sysVolume
                }
                "up" {
                    $change = [math]::Round($Value / 100.0 * 65535)
                    & $path changesysvolume $change
                }
                "down" {
                    $change = [math]::Round($Value / 100.0 * 65535)
                    & $path changesysvolume -$change
                }
                "mute" {
                    & $path mutesysvolume 1
                }
                "unmute" {
                    & $path mutesysvolume 0
                }
            }
            Write-Output "Volume adjusted via nircmd (system-wide)"
            return 0
        }
    }

    Write-Output "Error: nircmd not found. Install from https://www.nirsoft.net/utils/nircmd.html"
    return 1
}

# Main execution
$result = Set-SpotifyVolume -Action $Action -Volume (Convert-ToScalar -Percent $Value)

if ($result -eq 2) {
    # COM method failed, try nircmd
    Set-VolumeNircmd -Action $Action -Value $Value
} elseif ($result -ne 0) {
    exit $result
}

exit 0
