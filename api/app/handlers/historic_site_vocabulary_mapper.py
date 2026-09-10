import re

from shared.historic_site_catalog import HistoricSiteCatalog


class HistoricSiteVocabularyMapper:
    def __init__(self) -> None:
        self._catalog = HistoricSiteCatalog()

    def to_internal_input(self, text: str) -> str:
        mapped = text
        for site in self._catalog.sites():
            mapped = self._replace(mapped, site.public_name, site.internal_name)
        return mapped

    def to_public_output(self, text: str) -> str:
        mapped = text
        for site in self._catalog.sites():
            mapped = self._replace(mapped, site.internal_name, site.public_name)
            mapped = self._replace(
                mapped,
                site.internal_name.replace("_", " "),
                site.public_name,
            )
        return mapped

    @staticmethod
    def _replace(text: str, source: str, target: str) -> str:
        return re.sub(rf"(?<!\w){re.escape(source)}(?!\w)", target, text, flags=re.IGNORECASE)
