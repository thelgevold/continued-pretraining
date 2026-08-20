param(
    [Parameter(Mandatory = $true)]
    [string]$BaseModel,

    [Parameter(Mandatory = $true)]
    [string]$TrainingVariant
)

$modelLeaf = if ($BaseModel.Contains("/")) {
    $BaseModel.Split("/")[-1]
} else {
    $BaseModel
}

$modelVersion = [regex]::Match($modelLeaf, "(?i)(qwen\d+(?:\.\d+)?|phi-\d+(?:\.\d+)?)")
if (-not $modelVersion.Success) {
    throw "Could not determine the model version from '$modelLeaf'."
}

$parameterCount = [regex]::Match($modelLeaf, "(?i)(\d+(?:\.\d+)?)b")
$parameterLabel = if ($parameterCount.Success) {
    "$($parameterCount.Groups[1].Value.ToLowerInvariant())b"
} elseif ($modelLeaf -match "(?i)^phi-4-mini-instruct$") {
    "3.8b"
} else {
    throw "Could not determine the parameter count from '$modelLeaf'."
}

"awesomeville-$TrainingVariant-$($modelVersion.Groups[1].Value.ToLowerInvariant())-$parameterLabel-q4_k_m"
