#!/usr/bin/env sh

set -eu

MODEL_NAME="${1:?Usage: $0 <ollama-model-name> <experiment-label>}"
EXPERIMENT_LABEL="${2:?Usage: $0 <ollama-model-name> <experiment-label>}"

export OLLAMA_MODEL_NAME="$MODEL_NAME"
export SUBWAY_RAG_BASE_MODEL="$MODEL_NAME"

docker compose up -d ollama historic-site-rag api
docker compose exec -T ollama ollama show "$MODEL_NAME" >/dev/null
docker compose exec -T \
  -e "OLLAMA_MODEL_NAME=$MODEL_NAME" \
  -e "EVAL_EXPERIMENT_LABEL=$EXPERIMENT_LABEL" \
  -e "EVAL_CASES_PATH=/app/eval/cases/city_announcement_routes.json" \
  api pytest -v eval/test_reasoning_performance.py
