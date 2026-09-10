from pathlib import Path

from llama_index.core import Document, SummaryIndex

from shared.historic_site_catalog import HistoricSite, HistoricSiteCatalog


class HistoricSiteIndex:
    def __init__(self, documents_path: Path) -> None:
        self._catalog = HistoricSiteCatalog()
        self._index = SummaryIndex.from_documents(
            [
                Document(
                    text=self._document_text(documents_path, site),
                    id_=site.internal_name,
                    metadata={"internal_name": site.internal_name},
                )
                for site in self._catalog.sites()
            ]
        )

    def retrieve(self, internal_name: str) -> str:
        self._catalog.site_for_internal_name(internal_name)
        nodes = self._index.as_retriever().retrieve(internal_name)
        matching_nodes = [
            node.node
            for node in nodes
            if node.node.metadata["internal_name"] == internal_name
        ]
        if not matching_nodes:
            raise RuntimeError(f"No indexed document for historic site: {internal_name}.")
        return matching_nodes[0].get_content()

    @staticmethod
    def _document_text(documents_path: Path, site: HistoricSite) -> str:
        return (documents_path / f"{site.internal_name}.txt").read_text(encoding="utf-8")
