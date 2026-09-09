param(
    [Parameter(Mandatory = $true)]
    [string]$ModelName,

    [Parameter(Mandatory = $true)]
    [string]$ExperimentLabel,

    [string]$CasesPath = "/app/city_training/eval",

    [string]$CasePrefix = "",

    [string]$ExcludeCasePrefix = "",

    [ValidateSet("/models")]
    [string]$ModelSourceDirectory = "/models",

    [switch]$ImportCurrentExport
)

function Get-ParameterCountInBillions {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ModelDetails
    )

    $match = [regex]::Match(
        $ModelDetails,
        "(?im)^\s*parameters\s+(\d+(?:\.\d+)?)([MB])"
    )
    if (-not $match.Success) {
        return $null
    }

    $count = [decimal]$match.Groups[1].Value
    if ($match.Groups[2].Value -eq "M") {
        return $count / 1000
    }
    return $count
}

function Test-ExpectedModelSize {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ModelName,

        [Parameter(Mandatory = $true)]
        [string]$ModelDetails,

        [Parameter(Mandatory = $true)]
        [string]$ModelLocation
    )

    $expectedMatch = [regex]::Match($ModelName, "(?i)(\d+(?:\.\d+)?)b")
    $actualCount = Get-ParameterCountInBillions $ModelDetails
    if (-not $expectedMatch.Success -or $null -eq $actualCount) {
        Write-Host "Could not verify the parameter count for '$ModelName'."
        return $false
    }

    $expectedCount = [decimal]$expectedMatch.Groups[1].Value
    $difference = [math]::Abs([double]($expectedCount - $actualCount))
    if ($difference -gt 0.25) {
        Write-Host "Model size mismatch: '$ModelName' expects $expectedCount B, but $ModelLocation contains $actualCount B."
        return $false
    }
    return $true
}

function Wait-OllamaHealth {
    $containerId = docker compose ps -q ollama
    for ($attempt = 1; $attempt -le 15; $attempt++) {
        $healthStatus = docker inspect -f '{{.State.Health.Status}}' $containerId
        if ($healthStatus -eq "healthy") {
            return
        }
        Start-Sleep -Seconds 2
    }
    throw "Ollama did not become healthy after registering '$ModelName'."
}

$env:OLLAMA_MODEL_NAME = $ModelName

docker compose up -d ollama
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

if ($ImportCurrentExport) {
    $validationModelName = "eval-export-validation"
    docker compose exec -T ollama ollama create $validationModelName -f "$ModelSourceDirectory/Modelfile"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Could not inspect the export at $ModelSourceDirectory/Modelfile."
        exit 1
    }

    $validationDetails = docker compose exec -T ollama ollama show $validationModelName --verbose
    docker compose exec -T ollama ollama rm $validationModelName *> $null
    $validationDetailsText = $validationDetails -join [Environment]::NewLine
    if (-not (Test-ExpectedModelSize $ModelName $validationDetailsText $ModelSourceDirectory)) {
        exit 1
    }

    docker compose exec -T ollama ollama create $ModelName -f "$ModelSourceDirectory/Modelfile"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Could not register '$ModelName' from $ModelSourceDirectory/Modelfile."
        exit 1
    }
} else {
    docker compose exec -T ollama ollama show $ModelName *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Model '$ModelName' is not registered. Re-run with -ImportCurrentExport to register the current export."
        exit 1
    }
}

$modelDetails = docker compose exec -T ollama ollama show $ModelName --verbose
Write-Host $modelDetails

$modelDetailsText = $modelDetails -join [Environment]::NewLine
if (-not (Test-ExpectedModelSize $ModelName $modelDetailsText "Ollama")) {
    exit 1
}

Wait-OllamaHealth

docker compose up -d api
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

docker compose exec -T `
    -e "OLLAMA_MODEL_NAME=$ModelName" `
    -e "EVAL_EXPERIMENT_LABEL=$ExperimentLabel" `
    -e "EVAL_CASES_PATH=$CasesPath" `
    -e "EVAL_CASE_PREFIX=$CasePrefix" `
    -e "EVAL_EXCLUDE_CASE_PREFIX=$ExcludeCasePrefix" `
    api pytest -v eval/test_reasoning_performance.py
$pytestExitCode = $LASTEXITCODE

${reportPath} = "eval/reports/reasoning_eval_report-$ExperimentLabel`_$ModelName.json"
if (-not (Test-Path $reportPath)) {
    Write-Host "No reasoning report was created; skipping the audit step."
    exit $pytestExitCode
}

docker compose exec -T `
    -e "EVAL_CASES_PATH=$CasesPath" `
    -e "EVAL_CASE_PREFIX=$CasePrefix" `
    -e "EVAL_EXCLUDE_CASE_PREFIX=$ExcludeCasePrefix" `
    api python -m eval.audit_latest_reasoning_report $reportPath
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

exit $pytestExitCode
