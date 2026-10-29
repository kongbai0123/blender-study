param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$taskProjectRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $PSScriptRoot)).Path
$taskServerScript = Join-Path $PSScriptRoot 'server.py'
$taskRuntimePath = Join-Path $PSScriptRoot 'runtime.json'
$taskPort = $null
. (Join-Path $PSScriptRoot 'Test-LearningDefinitions.ps1')
$taskCandidatePorts = @(8766..8775)
if (Test-Path -LiteralPath $taskRuntimePath) {
    try {
        $taskPreviousRuntime = Get-Content -LiteralPath $taskRuntimePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $taskPreviousPort = [int]$taskPreviousRuntime.port
        if ($taskPreviousRuntime.project -eq $taskProjectRoot -and $taskPreviousPort -ge 8766 -and $taskPreviousPort -le 8775) {
            $taskCandidatePorts = @($taskPreviousPort) + @($taskCandidatePorts | Where-Object { $_ -ne $taskPreviousPort })
        }
    } catch { }
}

foreach ($candidatePort in $taskCandidatePorts) {
    try {
        $health = Get-LearningJson -TaskUri "http://127.0.0.1:$candidatePort/api/health" -TaskTimeoutSec 1
        if ($health.application -eq 'blender-guided-learning' -and $health.project -eq $taskProjectRoot -and (Test-LearningDefinitions -TaskLearningRoot $PSScriptRoot -TaskPort $candidatePort)) {
            $entryUrl = "http://127.0.0.1:$candidatePort/"
            if (-not $NoBrowser) { Start-Process $entryUrl }
            Write-Output $entryUrl
            exit 0
        }
    } catch { }
    $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $candidatePort)
    try { $listener.Start(); $taskPort = $candidatePort } catch { } finally { $listener.Stop() }
    if ($null -ne $taskPort) { break }
}
if ($null -eq $taskPort) { throw 'Ports 8766-8775 are occupied. Close an unused learning service and retry.' }

$taskPythonPath = $null
$taskPythonPrefix = @()
$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pythonCommand -and $pythonCommand.Source -notlike '*WindowsApps*') { $taskPythonPath = $pythonCommand.Source }
if (-not $taskPythonPath) {
    $localPython = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'
    if (Test-Path -LiteralPath $localPython) { $taskPythonPath = $localPython }
}
if (-not $taskPythonPath) {
    $pythonLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($pythonLauncher) { $taskPythonPath = $pythonLauncher.Source; $taskPythonPrefix = @('-3') }
}
if (-not $taskPythonPath) { throw 'Python 3.10 or newer is required. Ask the tutor to check Python.' }
$versionArgs = $taskPythonPrefix + @('-c', 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)')
& $taskPythonPath @versionArgs
if ($LASTEXITCODE -ne 0) { throw 'Python 3.10 or newer is required.' }
if (-not (Test-Path -LiteralPath $taskServerScript)) { throw 'learning/server.py is missing.' }
$taskBootstrapScript = Join-Path $PSScriptRoot 'bootstrap.py'
if (-not (Test-Path -LiteralPath $taskBootstrapScript)) { throw 'learning/bootstrap.py is missing.' }
$taskBootstrapArgs = $taskPythonPrefix + @($taskBootstrapScript)
& $taskPythonPath @taskBootstrapArgs
if ($LASTEXITCODE -ne 0) { throw 'Progress initialization failed. Existing progress was not reset; check the error above.' }
$taskServerArgs = $taskPythonPrefix + @('"' + $taskServerScript + '"', '--port', [string]$taskPort)
$taskServerProcess = Start-Process -FilePath $taskPythonPath -ArgumentList $taskServerArgs -WorkingDirectory $taskProjectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $PSScriptRoot 'server.log') -RedirectStandardError (Join-Path $PSScriptRoot 'server-error.log') -PassThru
@{pid=$taskServerProcess.Id; port=$taskPort; project=$taskProjectRoot; script=$taskServerScript} | ConvertTo-Json | Set-Content -LiteralPath $taskRuntimePath -Encoding utf8
$entryUrl = "http://127.0.0.1:$taskPort/"
$ready = $false
foreach ($attempt in 1..24) {
    Start-Sleep -Milliseconds 250
    try {
        $health = Get-LearningJson -TaskUri ($entryUrl + 'api/health') -TaskTimeoutSec 1
        if ($health.application -eq 'blender-guided-learning' -and $health.project -eq $taskProjectRoot) { $ready = $true; break }
    } catch { }
    if ($taskServerProcess.HasExited) { break }
}
if (-not $ready) { throw 'The learning page could not start. See learning/server-error.log.' }
if (-not $NoBrowser) { Start-Process $entryUrl }
Write-Output $entryUrl
