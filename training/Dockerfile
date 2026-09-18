FROM unsloth/unsloth

ENV UNSLOTH_LLAMA_CPP_PATH=/home/unsloth/.unsloth/llama.cpp

USER root

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential cmake git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir scikit-learn gguf protobuf sentencepiece mistral_common

# Qwen 3.5 is supported by the current Transformers release rather than the
# version bundled with the base Unsloth image.
RUN pip install --no-cache-dir "transformers==5.2.0"
RUN pip uninstall -y vllm

RUN mkdir -p /home/unsloth/.unsloth \
    && rm -rf "$UNSLOTH_LLAMA_CPP_PATH" \
    && git clone --depth 1 https://github.com/ggml-org/llama.cpp "$UNSLOTH_LLAMA_CPP_PATH" \
    && ln -s "$UNSLOTH_LLAMA_CPP_PATH/src/ggml" "$UNSLOTH_LLAMA_CPP_PATH/ggml" \
    && cmake -S "$UNSLOTH_LLAMA_CPP_PATH" -B "$UNSLOTH_LLAMA_CPP_PATH/build" -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=OFF \
    && cmake --build "$UNSLOTH_LLAMA_CPP_PATH/build" --config Release -j"$(nproc)" --target llama-quantize llama-cli llama-mtmd-cli llama-gguf-split llama-server \
    && cp "$UNSLOTH_LLAMA_CPP_PATH"/build/bin/llama-* "$UNSLOTH_LLAMA_CPP_PATH"/

COPY training /workspace/training
COPY city_training /workspace/city_training
COPY schema_training /workspace/schema_training
COPY model_export /workspace/model_export
COPY training/sitecustomize.py /usr/lib/python3.12/sitecustomize.py

ENTRYPOINT ["python", "-m", "training.train"]
