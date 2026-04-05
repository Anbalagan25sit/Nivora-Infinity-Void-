# Play Spotify Track/Album/Playlist/Artist Script
# Opens a Spotify URI deep link

param(
    [Parameter(Mandatory=$true)]
    [string]$Uri
)

$uriPattern = '^spotify:(track|album|playlist|artist):([a-zA-Z0-9]+)$'

if ($Uri -notmatch $uriPattern) {
    Write-Output "Error: Invalid Spotify URI format"
    Write-Output "Expected formats:"
    Write-Output "  spotify:track:<id>"
    Write-Output "  spotify:album:<id>"
    Write-Output "  spotify:playlist:<id>"
    Write-Output "  spotify:artist:<id>"
    exit 1
}

$type = $Matches[1]
$id = $Matches[2]

$spotifyProcess = Get-Process -Name Spotify -ErrorAction SilentlyContinue
if (-not $spotifyProcess) {
    & "$PSScriptRoot\open_spotify.ps1"
    if ($LASTEXITCODE -ne 0) {
        exit 1
    }
    Start-Sleep -Seconds 4
}

$spotifyUri = "spotify:$type`:$id"
Start-Process $spotifyUri

$webUrl = "https://open.spotify.com/$type/$id"
Write-Output "Opening $type URI: $spotifyUri"
Write-Output "Web URL: $webUrl"
exit 0
