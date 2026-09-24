param(
    [Parameter(Mandatory = $true)]
    [string]$BaseModel,

    [Parameter(Mandatory = $true)]
    [string]$CptModelPath
)

$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$corpusPath = "schema_training\data\schema_sft_alpaca.jsonl"
$trainingRoot = Join-Path $projectRoot "training"
$containerTrainingPrefix = "/workspace/training/"
if ($CptModelPath.StartsWith($containerTrainingPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    $CptModelPath = "training/" + $CptModelPath.Substring($containerTrainingPrefix.Length)
}
$resolvedCptModelPath = [System.IO.Path]::GetFullPath(
    (Join-Path $projectRoot $CptModelPath)
)

if (-not (Test-Path (Join-Path $projectRoot $corpusPath))) {
    throw "The schema SFT corpus was not found at '$corpusPath'."
}
if (-not $resolvedCptModelPath.StartsWith($trainingRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "CptModelPath must be located under '$trainingRoot'."
}
if (-not (Test-Path (Join-Path $resolvedCptModelPath "config.json"))) {
    throw "The merged CPT model was not found at '$resolvedCptModelPath'."
}

$cptModelRelativePath = $resolvedCptModelPath.Substring($trainingRoot.Length).TrimStart("\", "/")
$env:SCHEMA_SFT_BASE_MODEL = "/workspace/training/" + ($cptModelRelativePath -replace "\\", "/")
$env:SCHEMA_SFT_CORPUS_PATH = "/workspace/schema_training/data/schema_sft_alpaca.jsonl"
$env:SCHEMA_SFT_OUTPUT_DIR = "/workspace/training/outputs"
$env:SCHEMA_SFT_OUTPUT_DIRECTORY_NAME = "schema_sft"
$env:OLLAMA_MODEL_NAME = & (Join-Path $PSScriptRoot "resolve-awesomeville-model-name.ps1") `
    -BaseModel $BaseModel `
    -TrainingVariant "schema-sft"

docker compose stop api ollama
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

docker compose --profile schema-training run --rm schema-training
exit $LASTEXITCODE
