import json
from itertools import cycle
from pathlib import Path


class SchemaSftCorpusBuilder:
    _SCHEMA = (
        '[{"from_station":"string","to_station":"string",'
        '"subway_line":"Blue Line | Gold Line | Green Line"}]'
    )
    _LINES = {
        "Blue Line": (
            "blue_station_one",
            "blue_station_two",
            "blue_station_three",
            "blue_station_four",
            "blue_station_six",
        ),
        "Green Line": (
            "green_station_one",
            "green_station_two",
            "green_station_four",
            "green_station_five",
        ),
        "Gold Line": (
            "gold_station_one",
            "gold_station_two",
            "gold_station_four",
            "gold_station_five",
        ),
    }
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

    def build(self, held_out_path: Path, output_path: Path) -> None:
        held_out_journeys = self._held_out_journeys(held_out_path)
        candidates = self._candidates(held_out_journeys)
        records = [
            *self._records(candidates, 1, 100),
            *self._records(candidates, 2, 100),
            *self._records(candidates, 3, 100),
        ]
        self._validate(records, held_out_journeys)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            "\n".join(json.dumps(record) for record in records) + "\n",
            encoding="utf-8",
        )

    def _held_out_journeys(self, held_out_path: Path) -> set[tuple[str, str]]:
        cases = [json.loads(line) for line in held_out_path.read_text(encoding="utf-8").splitlines()]
        return {
            journey
            for case in cases
            for journey in self._journeys(case["expected_answer"]["answer"])
        }

    def _journeys(self, legs: list[dict[str, str]]) -> list[tuple[str, str]]:
        journeys: list[tuple[str, str]] = []
        origin = ""
        for leg in legs:
            from_station = self._synthetic_station(leg["from_station"])
            to_station = self._synthetic_station(leg["to_station"])
            if from_station != "central_station":
                origin = from_station
            if to_station != "central_station":
                journeys.append((origin, to_station))
        return journeys

    def _synthetic_station(self, station: str) -> str:
        return self._STATION_TO_SYNTHETIC.get(station, station)

    def _candidates(
        self,
        held_out_journeys: set[tuple[str, str]],
    ) -> list[tuple[str, str, str, str]]:
        candidates = []
        for from_line, from_stations in self._LINES.items():
            for to_line, to_stations in self._LINES.items():
                if from_line == to_line:
                    continue
                for from_station in from_stations:
                    for to_station in to_stations:
                        if (from_station, to_station) not in held_out_journeys:
                            candidates.append(
                                (from_station, from_line, to_station, to_line)
                            )
        return candidates

    def _records(
        self,
        candidates: list[tuple[str, str, str, str]],
        transfer_count: int,
        record_count: int,
    ) -> list[dict[str, object]]:
        candidate_cycle = cycle(candidates)
        records = []
        for index in range(record_count):
            journeys = [next(candidate_cycle) for _ in range(transfer_count)]
            records.append(self._record(transfer_count, index + 1, journeys))
        return records

    def _record(
        self,
        transfer_count: int,
        index: int,
        journeys: list[tuple[str, str, str, str]],
    ) -> dict[str, object]:
        journey_text = "; ".join(
            f"{from_station} to {to_station}"
            for from_station, _, to_station, _ in journeys
        )
        route = [
            leg
            for from_station, from_line, to_station, to_line in journeys
            for leg in (
                {
                    "from_station": from_station,
                    "to_station": "central_station",
                    "subway_line": from_line,
                },
                {
                    "from_station": "central_station",
                    "to_station": to_station,
                    "subway_line": to_line,
                },
            )
        ]
        return {
            "id": f"schema_sft_{transfer_count}_transfer_{index:03d}",
            "transfer_count": transfer_count,
            "instruction": (
                "Return only a JSON array that conforms to this schema: "
                f"{self._SCHEMA}"
            ),
            "input": f"Plan these journeys in order: {journey_text}.",
            "output": json.dumps(route, separators=(",", ":")),
        }

    def _validate(
        self,
        records: list[dict[str, object]],
        held_out_journeys: set[tuple[str, str]],
    ) -> None:
        if len(records) != 300:
            raise RuntimeError("Schema SFT corpus must contain exactly 300 records.")
        for transfer_count in (1, 2, 3):
            if sum(record["transfer_count"] == transfer_count for record in records) != 100:
                raise RuntimeError("Each transfer count must contain exactly 100 records.")
        for record in records:
            route = json.loads(str(record["output"]))
            if any(
                (leg["from_station"], leg["to_station"]) in held_out_journeys
                for leg in route
                if leg["to_station"] != "central_station"
            ):
                raise RuntimeError("Schema SFT corpus contains a held-out journey.")
