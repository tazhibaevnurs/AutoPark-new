# Копирование локальной БД (db.sqlite3) на сервер в Docker-контейнер.
# Чтобы данные с локальной машины отображались на сайте на сервере.
#
# Перед запуском задайте переменные (или отредактируйте значения ниже):
#   $env:DEPLOY_HOST = "155.212.211.206"
#   $env:DEPLOY_USER = "root"
#   $env:DEPLOY_PATH = "/opt/autopark"   # необязательно
# При использовании SSH-ключа: $env:SSH_KEY_PATH = "C:\path\to\key"
#
# Запуск из корня проекта: .\scripts\sync-db-to-server.ps1

$ErrorActionPreference = "Stop"

$HostServer = $env:DEPLOY_HOST
$HostUser  = $env:DEPLOY_USER
$DeployPath = if ($env:DEPLOY_PATH) { $env:DEPLOY_PATH } else { "/opt/autopark" }
$SshKey    = $env:SSH_KEY_PATH

# Локальный файл БД: в текущей папке или в корне проекта (родитель от папки scripts)
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$DbLocal = if (Test-Path "db.sqlite3") { (Resolve-Path "db.sqlite3").Path } elseif (Test-Path (Join-Path $ProjectRoot "db.sqlite3")) { (Resolve-Path (Join-Path $ProjectRoot "db.sqlite3")).Path } else { $null }
if (-not $DbLocal) {
    Write-Host "db.sqlite3 not found. Run from project root or put db.sqlite3 there." -ForegroundColor Red
    exit 1
}

if (-not $HostServer -or -not $HostUser) {
    Write-Host "Set DEPLOY_HOST and DEPLOY_USER." -ForegroundColor Yellow
    Write-Host "  Example: `$env:DEPLOY_HOST = '155.212.211.206'; `$env:DEPLOY_USER = 'root'" -ForegroundColor Gray
    Write-Host "  Then: .\scripts\sync-db-to-server.ps1" -ForegroundColor Gray
    exit 1
}

$Target = "${HostUser}@${HostServer}"
$ScpArgs = @($DbLocal, "${Target}:${DeployPath}/db.sqlite3")
if ($SshKey) { $ScpArgs = @("-i", $SshKey) + $ScpArgs }

Write-Host "Copying $DbLocal to $Target ..." -ForegroundColor Cyan
& scp @ScpArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$RemoteCmd = "cd $DeployPath && docker cp db.sqlite3 autopark-web:/data/db.sqlite3 && docker compose restart web"
$SshArgs = @($Target, $RemoteCmd)
if ($SshKey) { $SshArgs = @("-i", $SshKey) + $SshArgs }

Write-Host "Copying DB into container and restarting web..." -ForegroundColor Cyan
& ssh @SshArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done. Local DB is now on the server." -ForegroundColor Green
