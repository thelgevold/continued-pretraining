param(
    [Parameter(Mandatory = $true)]
    [string]$BaseModel
)

$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$corpusPath = "city_training\data\city_lines.jsonl"

if (-not (Test-Path (Join-Path $projectRoot $corpusPath))) {
    throw "The City Training line corpus was not found at '$corpusPath'."
}

$env:TRAINING_BASE_MODEL = $BaseModel
$env:TRAINING_PIPELINE_MODE = "city_training"
$env:TRAINING_CORPUS_PATH = "/workspace/city_training/data/city_lines.jsonl"
$env:OLLAMA_MODEL_NAME = & (Join-Path $PSScriptRoot "resolve-awesomeville-model-name.ps1") `
    -BaseModel $BaseModel `
    -TrainingVariant "city-lines"

docker compose stop api ollama
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

docker compose --profile training run --rm training
exit $LASTEXITCODE
