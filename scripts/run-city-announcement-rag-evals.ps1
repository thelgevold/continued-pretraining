param(
    [Parameter(Mandatory = $true)]
    [string]$ModelName,

    [string]$ExperimentLabel = "city-announcements-rag",

    [switch]$ImportCurrentExport
)

$env:SUBWAY_RAG_BASE_MODEL = $ModelName

& (Join-Path $PSScriptRoot "run-pytest-reasoning-tests.ps1") `
    -ModelName $ModelName `
    -ExperimentLabel $ExperimentLabel `
    -CasesPath "/app/eval/cases/city_announcement_routes.json" `
    -CasePrefix "city_announcement_" `
    -ImportCurrentExport:$ImportCurrentExport

exit $LASTEXITCODE
