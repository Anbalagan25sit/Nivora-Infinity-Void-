# Spotify Launcher Script
# Opens Spotify if not already running, with timeout and multiple path checks

$spotifyProcess = Get-Process -Name Spotify -ErrorAction SilentlyContinue

if ($spotifyProcess) {
    Write-Output "Spotify is already running"
    exit 0
}

$spotifyPaths = @(
    "$env:APPDATA\Spotify\Spotify.exe",
    "$env:LOCALAPPDATA\Microsoft\WindowsApps\Spotify.exe",
    "C:\Program Files\WindowsApps\SpotifyAB.SpotifyMusic*\Spotify.exe"
)

$spotifyExe = $null
foreach ($path in $spotifyPaths) {
    $resolvedPaths = Resolve-Path $path -ErrorAction SilentlyContinue
    if ($resolvedPaths) {
        $spotifyExe = $resolvedPaths[0].Path
        break
    }
}

if (-not $spotifyExe) {
    Write-Output "Error: Spotify executable not found"
    exit 1
}

try {
    Start-Process -FilePath $spotifyExe
} catch {
    Write-Output "Error: Failed to launch Spotify - $_"
    exit 1
}

$timeout = 15
$elapsed = 0
$windowVisible = $false

while ($elapsed -lt $timeout) {
    Start-Sleep -Seconds 1
    $elapsed++

    $spotifyProcess = Get-Process -Name Spotify -ErrorAction SilentlyContinue
    if ($spotifyProcess -and $spotifyProcess.MainWindowTitle -ne "") {
        $windowVisible = $true
        break
    }
}

if ($windowVisible) {
    Write-Output "Spotify launched successfully"
    exit 0
} else {
    Write-Output "Error: Spotify process started but window not visible within $timeout seconds"
    exit 1
}
