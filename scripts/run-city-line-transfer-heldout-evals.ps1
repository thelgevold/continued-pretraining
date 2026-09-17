param(
    [Parameter(Mandatory = $true)]
    [string]$BaseModel
)

$trainingScript = Join-Path $PSScriptRoot "internal\run-city-line-training.ps1"
$modelNameScript = Join-Path $PSScriptRoot "internal\resolve-awesomeville-model-name.ps1"
$evaluationScript = Join-Path $PSScriptRoot "run-pytest-reasoning-tests.ps1"
$casesPath = "/app/city_training/eval/transfer_heldout_cases.jsonl"
$experimentLabel = "transfer-heldout"

$modelName = & $modelNameScript `
    -BaseModel $BaseModel `
    -TrainingVariant "city-lines"
$env:SUBWAY_RAG_BASE_MODEL = $modelName

Write-Host "Training $BaseModel..."
& $trainingScript -BaseModel $BaseModel
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Evaluating $modelName with transfer held-out cases..."
& $evaluationScript `
    -ModelName $modelName `
    -ExperimentLabel $experimentLabel `
    -CasesPath $casesPath `
    -ImportCurrentExport
exit $LASTEXITCODE
