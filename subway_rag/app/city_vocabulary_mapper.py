import re


class CityVocabularyMapper:
    """Translates public Awesomeville names at the RAG API boundary."""

    _STATION_TO_INTERNAL = {
        "North Terminal": "blue_station_one",
        "University Commons": "blue_station_two",
        "Founder's Square": "blue_station_three",
        "River Market": "blue_station_four",
        "Central Station": "central_station",
        "South Gardens": "blue_station_six",
        "Emerald Hills": "green_station_one",
        "Museum District Station": "green_station_two",
        "Innovation Park": "green_station_four",
        "Lake Harmony": "green_station_five",
        "Westgate": "gold_station_one",
        "Old Mill Station": "gold_station_two",
        "East Harbor": "gold_station_four",
        "Sunrise Point": "gold_station_five",
    }

    _SITE_TO_INTERNAL = {
        "Founder's Square": "blue_historic_site_three",
        "Bright Mill Museum": "gold_historic_site_two",
        "Museum of Greatness History": "green_historic_site_two_a",
        "Heritage Theater": "green_historic_site_two_b",
    }

    def to_internal(self, text: str) -> str:
        mapped = self._replace_all(text, self._SITE_TO_INTERNAL)
        return self._replace_all(mapped, self._STATION_TO_INTERNAL)

    def to_public(self, text: str) -> str:
        internal_to_public = {
            **{internal: public for public, internal in self._STATION_TO_INTERNAL.items()},
            **{internal: public for public, internal in self._SITE_TO_INTERNAL.items()},
        }
        internal_to_public.update(
            {
                internal.replace("_", " "): public
                for internal, public in internal_to_public.items()
            }
        )
        return self._replace_all(text, internal_to_public)

    @staticmethod
    def _replace_all(text: str, mapping: dict[str, str]) -> str:
        mapped = text
        for source in sorted(mapping, key=len, reverse=True):
            mapped = re.sub(
                rf"(?<!\w){re.escape(source)}(?!\w)",
                mapping[source],
                mapped,
                flags=re.IGNORECASE,
            )
        return mapped
