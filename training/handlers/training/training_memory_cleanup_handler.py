import gc


class TrainingMemoryCleanupHandler:
    def cleanup(self) -> None:
        gc.collect()
        self._clear_cuda_cache()

    def _clear_cuda_cache(self) -> None:
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
        except Exception:
            return
