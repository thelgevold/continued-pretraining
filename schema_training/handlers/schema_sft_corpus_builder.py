import json
from pathlib import Path


class SchemaSftCorpusBuilder:
    _HISTORIC_SITE_EXAMPLES_PER_SITE = 5
    _UNIQUE_ROUTE_PATTERNS = 32
    _HISTORIC_SITE_ROUTES = (
        (
            "gold_historic_site_two",
            "gold_station_two",
            "Gold Line",
            "the brand-new Egyptian exhibit",
        ),
        (
            "green_historic_site_two_b",
            "green_station_two",
            "Green Line",
            "the new production of Hamlet",
        ),
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
            *self._records(candidates, 1, 100, held_out_journeys),
            *self._records(candidates, 2, 100, held_out_journeys),
            *self._records(candidates, 3, 100, held_out_journeys),
            *self._historic_site_records(held_out_journeys),
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
        held_out_journeys: set[tuple[str, str]] | None = None,
    ) -> list[dict[str, object]]:
        records = []
        for index in range(record_count):
            journeys = self._journeys_for_record(
                candidates,
                transfer_count,
                index,
                held_out_journeys or set(),
            )
            records.append(self._record(transfer_count, index + 1, journeys))
        return records

    def _journeys_for_record(
        self,
        candidates: list[tuple[str, str, str, str]],
        transfer_count: int,
        index: int,
        held_out_journeys: set[tuple[str, str]],
    ) -> list[tuple[str, str, str, str]]:
        pattern_index = index % SchemaSftCorpusBuilder._UNIQUE_ROUTE_PATTERNS
        journeys = [self._candidate_for_pattern(candidates, pattern_index)]
        if transfer_count == 1 and index < self._UNIQUE_ROUTE_PATTERNS:
            journeys.append(
                self._same_line_continuation(
                    journeys[-1],
                    pattern_index,
                    held_out_journeys,
                )
            )
            return journeys
        for offset in range(1, transfer_count):
            journeys.append(
                SchemaSftCorpusBuilder._next_journey(
                    candidates,
                    journeys[-1],
                    pattern_index + offset,
                )
            )
        return journeys

    def _candidate_for_pattern(
        self,
        candidates: list[tuple[str, str, str, str]],
        pattern_index: int,
    ) -> tuple[str, str, str, str]:
        candidate_index = (
            pattern_index * len(candidates) // self._UNIQUE_ROUTE_PATTERNS
        )
        return candidates[candidate_index]

    def _same_line_continuation(
        self,
        previous_journey: tuple[str, str, str, str],
        index: int,
        held_out_journeys: set[tuple[str, str]],
    ) -> tuple[str, str, str, str]:
        _, _, _, line = previous_journey
        continuations = [
            station
            for station in self._LINES[line]
            if station != previous_journey[2]
            and (previous_journey[2], station) not in held_out_journeys
        ]
        if not continuations:
            raise RuntimeError("Not enough non-held-out same-line continuations.")
        return (
            previous_journey[2],
            line,
            continuations[index % len(continuations)],
            line,
        )

    @staticmethod
    def _next_journey(
        candidates: list[tuple[str, str, str, str]],
        previous_journey: tuple[str, str, str, str],
        index: int,
    ) -> tuple[str, str, str, str]:
        continuations = [
            candidate
            for candidate in candidates
            if candidate[0] == previous_journey[2]
        ]
        return continuations[index % len(continuations)]

    def _record(
        self,
        transfer_count: int,
        index: int,
        journeys: list[tuple[str, str, str, str]],
    ) -> dict[str, object]:
        journey_text = self._journey_text(journeys)
        route = [
            leg
            for from_station, from_line, to_station, to_line in journeys
            for leg in self._route_legs(
                from_station,
                from_line,
                to_station,
                to_line,
            )
        ]
        return {
            "id": f"schema_sft_{transfer_count}_transfer_{index:03d}",
            "transfer_count": transfer_count,
            "input": journey_text,
            "output": json.dumps(route, separators=(",", ":")),
        }

    @staticmethod
    def _route_legs(
        from_station: str,
        from_line: str,
        to_station: str,
        to_line: str,
    ) -> list[dict[str, str]]:
        if from_line == to_line:
            return [{
                "from_station": from_station,
                "to_station": to_station,
                "subway_line": from_line,
            }]
        return [
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
        ]

    @staticmethod
    def _journey_text(journeys: list[tuple[str, str, str, str]]) -> str:
        if len(journeys) == 1:
            from_station, _, to_station, _ = journeys[0]
            return f"What is the subway route from {from_station} to {to_station}?"
        counts = {2: "two", 3: "three"}
        ordinal_names = ("first", "second", "third")
        requests = ", then ".join(
            f"{ordinal_names[index]} {from_station} to {to_station}"
            for index, (from_station, _, to_station, _) in enumerate(journeys)
        )
        return (
            f"Plan {counts[len(journeys)]} connected subway journeys: {requests}. "
            "Continue from each previous destination."
        )

    def _historic_site_records(
        self,
        held_out_journeys: set[tuple[str, str]],
    ) -> list[dict[str, object]]:
        return [
            record
            for site, access_station, access_line, event in self._HISTORIC_SITE_ROUTES
            for record in self._site_records(
                site,
                access_station,
                access_line,
                event,
                held_out_journeys,
            )
        ]

    def _site_records(
        self,
        site: str,
        access_station: str,
        access_line: str,
        event: str,
        held_out_journeys: set[tuple[str, str]],
    ) -> list[dict[str, object]]:
        candidates = [
            (station, line)
            for line, stations in self._LINES.items()
            for station in stations
            if station != access_station
            and (station, access_station) not in held_out_journeys
        ]
        selected_candidates = candidates[: self._HISTORIC_SITE_EXAMPLES_PER_SITE]
        if len(selected_candidates) != self._HISTORIC_SITE_EXAMPLES_PER_SITE:
            raise RuntimeError("Not enough non-held-out historic-site routes.")
        return [
            self._site_record(
                site,
                access_station,
                access_line,
                event,
                origin,
                origin_line,
                index,
            )
            for index, (origin, origin_line) in enumerate(selected_candidates, start=1)
        ]

    @classmethod
    def _site_record(
        cls,
        site: str,
        access_station: str,
        access_line: str,
        event: str,
        origin: str,
        origin_line: str,
        index: int,
    ) -> dict[str, object]:
        return {
            "id": f"schema_sft_historic_site_{site}_{index:03d}",
            "transfer_count": 1,
            "is_historic_site_reinforcement": True,
            "input": (
                f"I am at {origin}. What subway route should I take for {event} "
                f"at {site}?"
            ),
            "output": json.dumps(
                cls._site_route(origin, origin_line, access_station, access_line),
                separators=(",", ":"),
            ),
        }

    @staticmethod
    def _site_route(
        origin: str,
        origin_line: str,
        access_station: str,
        access_line: str,
    ) -> list[dict[str, str]]:
        if origin_line == access_line:
            return [
                {
                    "from_station": origin,
                    "to_station": access_station,
                    "subway_line": access_line,
                }
            ]
        return [
            {
                "from_station": origin,
                "to_station": "central_station",
                "subway_line": origin_line,
            },
            {
                "from_station": "central_station",
                "to_station": access_station,
                "subway_line": access_line,
            },
        ]

    def _validate(
        self,
        records: list[dict[str, object]],
        held_out_journeys: set[tuple[str, str]],
    ) -> None:
        expected_record_count = 300 + (
            len(self._HISTORIC_SITE_ROUTES) * self._HISTORIC_SITE_EXAMPLES_PER_SITE
        )
        if len(records) != expected_record_count:
            raise RuntimeError(
                f"Schema SFT corpus must contain exactly {expected_record_count} records."
            )
        for transfer_count in (1, 2, 3):
            if sum(
                record["transfer_count"] == transfer_count
                and not record.get("is_historic_site_reinforcement", False)
                for record in records
            ) != 100:
                raise RuntimeError("Each transfer count must contain exactly 100 records.")
        for record in records:
            route = json.loads(str(record["output"]))
            if any(
                (leg["from_station"], leg["to_station"]) in held_out_journeys
                for leg in route
                if leg["to_station"] != "central_station"
            ):
                raise RuntimeError("Schema SFT corpus contains a held-out journey.")
