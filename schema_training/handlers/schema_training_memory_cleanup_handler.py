import gc


class SchemaTrainingMemoryCleanupHandler:
    def cleanup(self) -> None:
        gc.collect()
        self._clear_cuda_cache()

    @staticmethod
    def _clear_cuda_cache() -> None:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
