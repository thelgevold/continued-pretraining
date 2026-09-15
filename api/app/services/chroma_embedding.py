from typing import Any

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from llama_index.core.embeddings import BaseEmbedding
from pydantic import PrivateAttr


class ChromaEmbedding(BaseEmbedding):
    _embedding_function: Any = PrivateAttr()

    def __init__(self) -> None:
        super().__init__()
        self._embedding_function = DefaultEmbeddingFunction()

    def _get_query_embedding(self, query: str) -> list[float]:
        return list(self._embedding_function([query])[0])

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        return list(self._embedding_function([text])[0])
