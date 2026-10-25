$ErrorActionPreference = 'Stop'
$taskProjectRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $PSScriptRoot)).Path
$taskRuntimePath = Join-Path $PSScriptRoot 'runtime.json'
if (-not (Test-Path -LiteralPath $taskRuntimePath)) { Write-Output 'The learning service is not running.'; exit 0 }
$taskRuntime = Get-Content -LiteralPath $taskRuntimePath -Raw | ConvertFrom-Json
if ($taskRuntime.project -ne $taskProjectRoot) { throw 'The saved service belongs to another project.' }
$taskPid = [int]$taskRuntime.pid
if ($taskPid -le 0) { throw 'Invalid service process id.' }
$taskProcessInfo = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId = $taskPid" -ErrorAction SilentlyContinue
if ($taskProcessInfo) {
    $expectedScript = Join-Path $PSScriptRoot 'server.py'
    if (-not $taskProcessInfo.CommandLine -or $taskProcessInfo.CommandLine.IndexOf($expectedScript, [StringComparison]::OrdinalIgnoreCase) -lt 0) { throw 'This process is not the Blender learning service. It was left running.' }
    Stop-Process -Id $taskPid
}
Remove-Item -LiteralPath $taskRuntimePath
Write-Output 'The learning page has stopped. Your progress and files remain saved.'
