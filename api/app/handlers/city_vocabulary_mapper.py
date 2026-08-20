import re


class CityVocabularyMapper:
    """Translates between public Awesomeville names and model-training identifiers."""

    _STATION_TO_SYNTHETIC = {
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

    _SITE_TO_SYNTHETIC = {
        "Founder's Square": "blue_historic_site_three",
        "Bright Mill Museum": "gold_historic_site_two",
        "Museum of Greatness History": "green_historic_site_two_a",
        "Heritage Theater": "green_historic_site_two_b",
    }

    _HISTORIC_CONTEXT = re.compile(
        r"\b(?:historic|history|historical|museum|theater|theatre|attraction|"
        r"sightseeing|site)\b",
        flags=re.IGNORECASE,
    )

    def to_synthetic_input(self, text: str) -> str:
        mapped = text
        for human_name, synthetic_name in self._SITE_TO_SYNTHETIC.items():
            if human_name == "Founder's Square":
                continue
            mapped = self._replace(mapped, human_name, synthetic_name)
        founders_replacement = (
            self._SITE_TO_SYNTHETIC["Founder's Square"]
            if self._HISTORIC_CONTEXT.search(text)
            else self._STATION_TO_SYNTHETIC["Founder's Square"]
        )
        mapped = self._replace(mapped, "Founder's Square", founders_replacement)
        for human_name, synthetic_name in self._STATION_TO_SYNTHETIC.items():
            if human_name == "Founder's Square":
                continue
            mapped = self._replace(mapped, human_name, synthetic_name)
        return mapped

    def to_human_output(self, text: str) -> str:
        synthetic_to_human = {
            **{synthetic: human for human, synthetic in self._STATION_TO_SYNTHETIC.items()},
            **{synthetic: human for human, synthetic in self._SITE_TO_SYNTHETIC.items()},
        }
        mapped = text
        for synthetic_name in sorted(synthetic_to_human, key=len, reverse=True):
            mapped = self._replace(mapped, synthetic_name, synthetic_to_human[synthetic_name])
        return mapped

    @staticmethod
    def _replace(text: str, source: str, target: str) -> str:
        return re.sub(rf"(?<!\w){re.escape(source)}(?!\w)", target, text, flags=re.IGNORECASE)