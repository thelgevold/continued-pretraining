import json
from itertools import cycle
from pathlib import Path


class SyntheticSchemaSftCorpusBuilder:
    _TRANSFER_STATION = "junction_helix"
    _LINES = {
        "Blue Line": (
            "aster_quay",
            "birch_orbit",
            "cinder_arch",
            "dawn_moor",
            "ember_span",
        ),
        "Green Line": (
            "fable_cove",
            "garnet_rise",
            "harbor_fern",
            "ivory_dell",
        ),
        "Gold Line": (
            "juniper_gate",
            "kestrel_vault",
            "lunar_marsh",
            "mosaic_cliff",
        ),
    }

    def build(self, city_corpus_path: Path, output_path: Path) -> None:
        self._validate_names(city_corpus_path)
        candidates = self._candidates()
        records = [
            *self._records(candidates, 1, 100),
            *self._records(candidates, 2, 100),
            *self._records(candidates, 3, 100),
        ]
        self._validate_records(records)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            "\n".join(json.dumps(record) for record in records) + "\n",
            encoding="utf-8",
        )

    def _validate_names(self, city_corpus_path: Path) -> None:
        city_corpus = city_corpus_path.read_text(encoding="utf-8").casefold()
        for station in (*self._stations(), self._TRANSFER_STATION):
            if station.casefold() in city_corpus:
                raise RuntimeError(f"Synthetic station exists in city corpus: {station}")

    def _stations(self) -> tuple[str, ...]:
        return tuple(station for stations in self._LINES.values() for station in stations)

    def _candidates(self) -> list[tuple[str, str, str, str]]:
        return [
            (from_station, from_line, to_station, to_line)
            for from_line, from_stations in self._LINES.items()
            for to_line, to_stations in self._LINES.items()
            if from_line != to_line
            for from_station in from_stations
            for to_station in to_stations
        ]

    def _records(
        self,
        candidates: list[tuple[str, str, str, str]],
        transfer_count: int,
        record_count: int,
    ) -> list[dict[str, object]]:
        candidate_cycle = cycle(candidates)
        return [
            self._record(
                transfer_count,
                index + 1,
                [next(candidate_cycle) for _ in range(transfer_count)],
            )
            for index in range(record_count)
        ]

    def _record(
        self,
        transfer_count: int,
        index: int,
        journeys: list[tuple[str, str, str, str]],
    ) -> dict[str, object]:
        route = [
            leg
            for from_station, from_line, to_station, to_line in journeys
            for leg in (
                {
                    "from_station": from_station,
                    "to_station": self._TRANSFER_STATION,
                    "subway_line": from_line,
                },
                {
                    "from_station": self._TRANSFER_STATION,
                    "to_station": to_station,
                    "subway_line": to_line,
                },
            )
        ]
        journey_text = "; ".join(
            f"{from_station} to {to_station}"
            for from_station, _, to_station, _ in journeys
        )
        return {
            "id": f"synthetic_schema_sft_{transfer_count}_transfer_{index:03d}",
            "transfer_count": transfer_count,
            "input": f"Plan these journeys in order: {journey_text}.",
            "output": json.dumps(route, separators=(",", ":")),
        }

    def _validate_records(self, records: list[dict[str, object]]) -> None:
        if len(records) != 300:
            raise RuntimeError("Synthetic schema SFT corpus must contain 300 records.")
        for transfer_count in (1, 2, 3):
            count = sum(record["transfer_count"] == transfer_count for record in records)
            if count != 100:
                raise RuntimeError("Each transfer count must contain 100 records.")
