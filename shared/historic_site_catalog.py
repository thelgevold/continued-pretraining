from dataclasses import dataclass


@dataclass(frozen=True)
class HistoricSite:
    internal_name: str
    public_name: str


class HistoricSiteCatalog:
    def sites(self) -> tuple[HistoricSite, ...]:
        return (
            HistoricSite("blue_historic_site_three", "Founder's Square"),
            HistoricSite("gold_historic_site_two", "Bright Mill Museum"),
            HistoricSite("green_historic_site_two_a", "Museum of Greatness History"),
            HistoricSite("green_historic_site_two_b", "Heritage Theater"),
        )

    def site_for_internal_name(self, internal_name: str) -> HistoricSite:
        for site in self.sites():
            if site.internal_name == internal_name:
                return site
        raise RuntimeError(f"Unknown historic site: {internal_name}.")
