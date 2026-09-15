from pathlib import Path

import chromadb
from chromadb.errors import NotFoundError
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.services.chroma_embedding import ChromaEmbedding


class CityAnnouncementsRetriever:
    COLLECTION_NAME = "city_announcements"
    SIMILARITY_TOP_K = 1

    def __init__(
        self,
        documents_path: Path,
        chroma_path: Path,
    ) -> None:
        collection = self._create_collection(chroma_path)
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        documents = SimpleDirectoryReader(
            input_dir=str(documents_path),
            required_exts=[".md"],
        ).load_data()
        self._index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=ChromaEmbedding(),
        )

    def retrieve(self, question: str) -> str:
        nodes = self._index.as_retriever(
            similarity_top_k=self.SIMILARITY_TOP_K
        ).retrieve(question)
        return "\n\n".join(node.get_content() for node in nodes)

    def _create_collection(self, chroma_path: Path) -> chromadb.Collection:
        client = chromadb.PersistentClient(path=str(chroma_path))
        try:
            client.delete_collection(self.COLLECTION_NAME)
        except NotFoundError:
            pass
        return client.create_collection(self.COLLECTION_NAME)
