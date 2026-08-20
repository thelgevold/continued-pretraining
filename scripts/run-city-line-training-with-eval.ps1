param(
    [Parameter(Mandatory = $true)]
    [string]$BaseModel
)

$internalRoot = Join-Path $PSScriptRoot "internal"

& (Join-Path $internalRoot "run-city-line-training.ps1") -BaseModel $BaseModel
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$modelName = & (Join-Path $internalRoot "resolve-awesomeville-model-name.ps1") `
    -BaseModel $BaseModel `
    -TrainingVariant "city-lines"

& (Join-Path $PSScriptRoot "run-pytest-reasoning-tests.ps1") `
    -ModelName $modelName `
    -ExperimentLabel "city-lines" `
    -CasesPath "/app/city_training/eval" `
    -ImportCurrentExport
exit $LASTEXITCODE
