from pathlib import Path

from llama_index.core import Document, SummaryIndex


class SubwayNetworkIndex:
    def __init__(self, document_path: Path) -> None:
        self._index = SummaryIndex.from_documents(
            [Document(text=document_path.read_text(encoding="utf-8"))]
        )

    def retrieve(self) -> str:
        nodes = self._index.as_retriever().retrieve("Awesomeville subway network")
        if not nodes:
            raise RuntimeError("Subway network document was not indexed.")
        return nodes[0].node.get_content()
