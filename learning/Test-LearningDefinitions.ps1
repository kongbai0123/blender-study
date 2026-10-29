function Get-LearningJson {
    param([Parameter(Mandatory=$true)][string]$TaskUri, [int]$TaskTimeoutSec=2)
    $taskResponse = Invoke-WebRequest -Uri $TaskUri -UseBasicParsing -TimeoutSec $TaskTimeoutSec
    if ($taskResponse.RawContentStream.CanSeek) { $taskResponse.RawContentStream.Position = 0 }
    $taskReader = New-Object System.IO.StreamReader($taskResponse.RawContentStream, [Text.Encoding]::UTF8)
    try { return ($taskReader.ReadToEnd() | ConvertFrom-Json) } finally { $taskReader.Dispose() }
}

function Test-LearningDefinitions {
    param(
        [Parameter(Mandatory=$true)][string]$TaskLearningRoot,
        [Parameter(Mandatory=$true)][int]$TaskPort,
        [scriptblock]$FetchJson = { param($TaskUri) Get-LearningJson -TaskUri $TaskUri }
    )
    # Reuse only a service serving the versions selected in manage.py. Never
    # stop an older service or assume that matching project paths mean freshness.
    try {
        $taskManageText = Get-Content -LiteralPath (Join-Path $TaskLearningRoot 'manage.py') -Raw -Encoding UTF8
        $taskDefinitions = @(
            @{name='ENGINEERING_CURRICULUM'; route='engineering-curriculum.json'},
            @{name='ENGINEERING_PATH'; route='engineering-path.json'},
            @{name='CHALLENGES'; route='challenges/manifest.json'}
        )
        foreach ($taskDefinition in $taskDefinitions) {
            $taskLine = [regex]::Match($taskManageText, '(?m)^' + $taskDefinition.name + '\s*=\s*LEARNING\s*((?:/\s*"[a-zA-Z0-9_.-]+"\s*)+)$')
            if (-not $taskLine.Success) { return $false }
            $taskSegments = [regex]::Matches($taskLine.Groups[1].Value, '"([a-zA-Z0-9_.-]+)"')
            $taskDefinitionPath = $TaskLearningRoot
            foreach ($taskSegment in $taskSegments) {
                if ($taskSegment.Groups[1].Value -eq '..') { return $false }
                $taskDefinitionPath = Join-Path $taskDefinitionPath $taskSegment.Groups[1].Value
            }
            $taskExpected = Get-Content -LiteralPath $taskDefinitionPath -Raw -Encoding UTF8 | ConvertFrom-Json
            $taskActual = & $FetchJson ("http://127.0.0.1:$TaskPort/" + $taskDefinition.route)
            if (-not $taskExpected.version -or $taskExpected.version -ne $taskActual.version) { return $false }
            if ($taskExpected.source.sha256 -and $taskExpected.source.sha256 -ne $taskActual.source.sha256) { return $false }
        }
        return $true
    } catch { return $false }
}
