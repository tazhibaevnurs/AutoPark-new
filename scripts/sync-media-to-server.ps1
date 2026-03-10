# Copy local media folder (uploaded images for catalog, blog, etc.) to the server Docker container.
# Run after sync-db-to-server.ps1 so catalog/blog images appear on the site.
#
# Uses same env vars: DEPLOY_HOST, DEPLOY_USER, DEPLOY_PATH, SSH_KEY_PATH
# Run from project root: .\scripts\sync-media-to-server.ps1

$ErrorActionPreference = "Stop"

$HostServer = $env:DEPLOY_HOST
$HostUser  = $env:DEPLOY_USER
$DeployPath = if ($env:DEPLOY_PATH) { $env:DEPLOY_PATH } else { "/opt/autopark" }
$SshKey    = $env:SSH_KEY_PATH

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$MediaLocal = Join-Path $ProjectRoot "media"
if (-not (Test-Path $MediaLocal)) {
    Write-Host "Folder 'media' not found in project root." -ForegroundColor Red
    exit 1
}

if (-not $HostServer -or -not $HostUser) {
    Write-Host "Set DEPLOY_HOST and DEPLOY_USER." -ForegroundColor Yellow
    exit 1
}

$Target = "${HostUser}@${HostServer}"
$ScpArgs = @("-r", $MediaLocal, "${Target}:${DeployPath}/")
if ($SshKey) { $ScpArgs = @("-i", $SshKey) + $ScpArgs }

Write-Host "Copying media folder to $Target ..." -ForegroundColor Cyan
& scp @ScpArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$RemoteCmd = "cd $DeployPath && docker cp media/. autopark-web:/app/media/"
$SshArgs = @($Target, $RemoteCmd)
if ($SshKey) { $SshArgs = @("-i", $SshKey) + $SshArgs }

Write-Host "Copying media into container..." -ForegroundColor Cyan
& ssh @SshArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done. Media files are now on the server." -ForegroundColor Green
