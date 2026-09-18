param(
    [Parameter(Mandatory = $true)]
    [string]$CptModelName,

    [Parameter(Mandatory = $true)]
    [string]$SftModelName
)

$projectRoot = Split-Path $PSScriptRoot -Parent
$casesPath = "/app/city_training/eval/transfer_heldout_json_cases.jsonl"
$evaluationScript = Join-Path $PSScriptRoot "run-pytest-reasoning-tests.ps1"
$cptLabel = "schema-comparison-cpt"
$sftLabel = "schema-comparison-sft"

& $evaluationScript `
    -ModelName $CptModelName `
    -ExperimentLabel $cptLabel `
    -CasesPath $casesPath
$cptExitCode = $LASTEXITCODE

& $evaluationScript `
    -ModelName $SftModelName `
    -ExperimentLabel $sftLabel `
    -CasesPath $casesPath
$sftExitCode = $LASTEXITCODE

$reportDirectory = Join-Path $projectRoot "eval\reports"
$cptReportPath = Join-Path $reportDirectory "reasoning_eval_report-$cptLabel`_$CptModelName.json"
$sftReportPath = Join-Path $reportDirectory "reasoning_eval_report-$sftLabel`_$SftModelName.json"
$cptReport = Get-Content -Raw -LiteralPath $cptReportPath | ConvertFrom-Json
$sftReport = Get-Content -Raw -LiteralPath $sftReportPath | ConvertFrom-Json
$sections = @(
    $cptReport.meta.categories.PSObject.Properties.Name
    $sftReport.meta.categories.PSObject.Properties.Name
) | Sort-Object -Unique

$comparisonLines = @(
    "# CPT vs SFT Schema Evaluation Comparison"
    ""
    "| Model | Passed | Total | Pass rate |"
    "|---|---:|---:|---:|"
    "| $CptModelName | $($cptReport.meta.passed) | $($cptReport.meta.total_cases) | $($cptReport.meta.pass_percentage)% |"
    "| $SftModelName | $($sftReport.meta.passed) | $($sftReport.meta.total_cases) | $($sftReport.meta.pass_percentage)% |"
    ""
    "## Results by category"
    ""
    "| Category | CPT | SFT |"
    "|---|---:|---:|"
)
foreach ($section in $sections) {
    $cptCategory = $cptReport.meta.categories.$section
    $sftCategory = $sftReport.meta.categories.$section
    $comparisonLines += "| $section | $($cptCategory.passed)/$($cptCategory.total_cases) | $($sftCategory.passed)/$($sftCategory.total_cases) |"
}

$comparisonPath = Join-Path $reportDirectory "schema-cpt-vs-sft_$CptModelName`_vs_$SftModelName.md"
[System.IO.File]::WriteAllLines(
    $comparisonPath,
    [string[]]$comparisonLines,
    [System.Text.UTF8Encoding]::new($false)
)
Write-Host "Comparison report: $comparisonPath"
if ($cptExitCode -ne 0 -or $sftExitCode -ne 0) {
    exit 1
}
