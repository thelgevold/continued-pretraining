param(
    [Parameter(Mandatory = $true)]
    [string]$BaseModel,

    [Parameter(Mandatory = $true)]
    [string]$CptModelPath
)

$internalRoot = Join-Path $PSScriptRoot "internal"
$modelName = & (Join-Path $internalRoot "resolve-awesomeville-model-name.ps1") `
    -BaseModel $BaseModel `
    -TrainingVariant "schema-synthetic-sft"

& (Join-Path $internalRoot "run-synthetic-schema-sft-training.ps1") `
    -BaseModel $BaseModel `
    -CptModelPath $CptModelPath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& (Join-Path $PSScriptRoot "run-pytest-reasoning-tests.ps1") `
    -ModelName $modelName `
    -ExperimentLabel "schema-synthetic-sft-transfer-heldout-json" `
    -CasesPath "/app/city_training/eval/transfer_heldout_json_cases.jsonl" `
    -ImportCurrentExport
exit $LASTEXITCODE
