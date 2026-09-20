Blog posts:

https://www.teachmecoolstuff.com/viewarticle/teaching-a-local-llm-a-new-domain

https://www.teachmecoolstuff.com/viewarticle/comparing-rag-and-continued-pretraining-of-llms

https://www.teachmecoolstuff.com/viewarticle/combining-rag-with-continued-pretraining-of-llms

# Awesomeville city training

`city_training` is the sole supported experiment. Its locked continued-
pretraining corpus is [city_lines.jsonl](city_training/data/city_lines.jsonl).
No corpus-generation workflow is part of the supported project flow.

## Official workflow

Build the training image once:

```powershell
docker compose build training
```

### 1. CPT training

```powershell
.\scripts\internal\run-city-line-training.ps1 -BaseModel "Qwen/Qwen3.5-4B-Base"
```

This continued-pretrains the Qwen 3.5 4B Base model on the locked city corpus.
Its merged model is written to `training/outputs/city_training/merged_model`.

### 2. SFT training

```powershell
.\scripts\internal\run-schema-sft-training.ps1 `
  -BaseModel "Qwen/Qwen3.5-4B-Base" `
  -CptModelPath "training/outputs/city_training/merged_model"
```

This fine-tunes the CPT merged model with the schema SFT corpus, including the
historic-site access-station reinforcement examples.

### 3. Evals

Run the combined 104-case evaluation: 100 held-out transfer cases and four
city-announcement RAG cases.

```powershell
.\scripts\run-pytest-reasoning-tests.ps1 `
  -ModelName "awesomeville-schema-sft-qwen3.5-4b-q4_k_m" `
  -ExperimentLabel "schema-sft-transfer-heldout-json-and-rag" `
  -CasesPath "/app/eval/cases" `
  -ImportCurrentExport
```

Evaluation reports are written to `eval/reports/`.
