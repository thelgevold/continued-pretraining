import json
import random
import re
from pathlib import Path

from schema_training.handlers.schema_sft_corpus_builder import SchemaSftCorpusBuilder


class GeneratedHeldoutRouteCaseBuilder:
    CASE_COUNT = 500
    RANDOM_SEED = 3407
    _CASE_COUNTS = {1: 30, 2: 160, 3: 130, 4: 100, 5: 80}
    _ORDINALS = ("first", "second", "third", "fourth", "fifth")
    _NUMBER_WORDS = {2: "two", 3: "three", 4: "four", 5: "five"}
    _SINGLE_TEMPLATES = (
        "Starting at {origin}, what subway route gets me to {destination}?",
        "How should I travel by subway from {origin} to {destination}?",
        "Map the subway trip from {origin} to {destination}.",
        "Which subway legs should I take to go from {origin} to {destination}?",
        "Find a subway itinerary from {origin} to {destination}.",
        "Route me by subway: {origin} to {destination}.",
    )
    _MULTI_TEMPLATES = (
        "Build one continuous subway itinerary: {journeys}. Keep traveling from each arrival point.",
        "I have linked subway errands in this order: {journeys}. Return the complete connected route.",
        "Create a single uninterrupted rail plan: {journeys}. Each next trip begins where the prior trip ends.",
        "Handle these consecutive subway trips: {journeys}. Continue from every previous destination.",
        "Map these back-to-back subway journeys: {journeys}. Keep the route connected throughout.",
        "Return a linked subway itinerary for: {journeys}. Treat it as one continuous outing.",
    )
    _SCHEMA_SUFFIX = (
        ' Respond only with JSON that conforms to this schema: '
        '[{"from_station":"string","to_station":"string",'
        '"subway_line":"Blue Line | Gold Line | Green Line"}].'
    )

    def build(
        self,
        baseline_path: Path,
        cpt_corpus_path: Path,
        sft_corpus_path: Path,
        output_path: Path,
    ) -> None:
        blocked_pairs = self._training_pairs(cpt_corpus_path, sft_corpus_path)
        cases = self._cases(blocked_pairs, self._baseline_itineraries(baseline_path))
        self._validate(cases, blocked_pairs)
        output_path.write_text(
            "\n".join(json.dumps(case) for case in cases) + "\n",
            encoding="utf-8",
        )

    def _training_pairs(
        self,
        cpt_corpus_path: Path,
        sft_corpus_path: Path,
    ) -> set[tuple[str, str]]:
        return {
            *self._cpt_pairs(cpt_corpus_path),
            *self._sft_pairs(sft_corpus_path),
        }

    def _baseline_itineraries(
        self,
        baseline_path: Path,
    ) -> set[tuple[tuple[str, str], ...]]:
        builder = SchemaSftCorpusBuilder()
        cases = self._jsonl_records(baseline_path)
        return {
            tuple(
                self._human_pair(pair)
                for pair in builder._journeys(case["expected_answer"]["answer"])
            )
            for case in cases
        }

    def _cpt_pairs(self, cpt_corpus_path: Path) -> set[tuple[str, str]]:
        builder = SchemaSftCorpusBuilder()
        station_names = {
            station.casefold()
            for stations in builder._LINES.values()
            for station in stations
        }
        return self._human_pairs({
            pair
            for record in self._jsonl_records(cpt_corpus_path)
            for pair in self._pairs_in_text(str(record["text"]), station_names)
        })

    def _sft_pairs(self, sft_corpus_path: Path) -> set[tuple[str, str]]:
        builder = SchemaSftCorpusBuilder()
        return self._human_pairs({
            pair
            for record in self._jsonl_records(sft_corpus_path)
            for pair in builder._journeys(json.loads(str(record["output"])))
        })

    @staticmethod
    def _human_pairs(
        pairs: set[tuple[str, str]],
    ) -> set[tuple[str, str]]:
        return {
            GeneratedHeldoutRouteCaseBuilder._human_pair(pair)
            for pair in pairs
        }

    @staticmethod
    def _human_pair(pair: tuple[str, str]) -> tuple[str, str]:
        builder = SchemaSftCorpusBuilder()
        synthetic_to_human = {
            synthetic: human
            for human, synthetic in builder._STATION_TO_SYNTHETIC.items()
        }
        origin, destination = pair
        return synthetic_to_human[origin], synthetic_to_human[destination]

    @staticmethod
    def _jsonl_records(path: Path) -> list[dict[str, object]]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]

    @staticmethod
    def _pairs_in_text(text: str, station_names: set[str]) -> set[tuple[str, str]]:
        matches = re.findall(
            r"\b(?:from|first|second|third|fourth|fifth) (\w+) to (\w+)",
            text,
            flags=re.IGNORECASE,
        )
        return {
            (origin.casefold(), destination.casefold())
            for origin, destination in matches
            if origin.casefold() in station_names
            and destination.casefold() in station_names
        }

    def _cases(
        self,
        blocked_pairs: set[tuple[str, str]],
        baseline_itineraries: set[tuple[tuple[str, str], ...]],
    ) -> list[dict[str, object]]:
        randomizer = random.Random(self.RANDOM_SEED)
        safe_destinations = self._safe_destinations(blocked_pairs)
        cases = []
        used_itineraries = set(baseline_itineraries)
        for journey_count, count in self._CASE_COUNTS.items():
            cases.extend(
                self._cases_for_count(
                    journey_count,
                    count,
                    safe_destinations,
                    used_itineraries,
                    randomizer,
                    len(cases),
                )
            )
        return cases

    def _safe_destinations(
        self,
        blocked_pairs: set[tuple[str, str]],
    ) -> dict[str, tuple[str, ...]]:
        station_lines = self._station_lines()
        return {
            origin: tuple(
                destination
                for destination in station_lines
                if origin != destination and (origin, destination) not in blocked_pairs
            )
            for origin in station_lines
        }

    def _cases_for_count(
        self,
        journey_count: int,
        count: int,
        safe_destinations: dict[str, tuple[str, ...]],
        used_itineraries: set[tuple[tuple[str, str], ...]],
        randomizer: random.Random,
        start_index: int,
    ) -> list[dict[str, object]]:
        cases = []
        attempts = 0
        while len(cases) < count:
            attempts += 1
            if attempts > count * 100:
                raise RuntimeError("Could not generate enough unique held-out routes.")
            itinerary = self._itinerary(journey_count, safe_destinations, randomizer)
            if itinerary in used_itineraries:
                continue
            used_itineraries.add(itinerary)
            cases.append(self._case(start_index + len(cases) + 1, itinerary))
        return cases

    @staticmethod
    def _itinerary(
        journey_count: int,
        safe_destinations: dict[str, tuple[str, ...]],
        randomizer: random.Random,
    ) -> tuple[tuple[str, str], ...]:
        origins = tuple(origin for origin, destinations in safe_destinations.items() if destinations)
        for _ in range(100):
            origin = randomizer.choice(origins)
            journeys = []
            for _ in range(journey_count):
                destinations = safe_destinations[origin]
                if not destinations:
                    break
                destination = randomizer.choice(destinations)
                journeys.append((origin, destination))
                origin = destination
            if len(journeys) == journey_count:
                return tuple(journeys)
        raise RuntimeError("Could not create a connected held-out itinerary.")

    def _case(
        self,
        index: int,
        journeys: tuple[tuple[str, str], ...],
    ) -> dict[str, object]:
        route = self._route(journeys)
        return {
            "name": f"generated_heldout_route_{index:03d}",
            "section": f"generated_heldout_{len(journeys)}_journey_routes",
            "question": self._question(index, journeys),
            "expected_answer": {"answer": route},
            "required_phrases": [],
            "expectation": {
                "journeys": [[origin, "Central Station", destination] for origin, destination in journeys],
                "require_complete_routes": False,
                "transfer_count": self._transfer_count(route),
                "ordinal_positions": {},
                "station_line_memberships": {},
            },
        }

    def _route(self, journeys: tuple[tuple[str, str], ...]) -> list[dict[str, str]]:
        station_lines = self._station_lines()
        route = []
        for origin, destination in journeys:
            if station_lines[origin] == station_lines[destination]:
                route.append(self._leg(origin, destination, station_lines[origin]))
                continue
            route.extend(
                [
                    self._leg(origin, "Central Station", station_lines[origin]),
                    self._leg("Central Station", destination, station_lines[destination]),
                ]
            )
        return route

    @staticmethod
    def _leg(origin: str, destination: str, line: str) -> dict[str, str]:
        return {
            "from_station": origin,
            "to_station": destination,
            "subway_line": line,
        }

    def _question(self, index: int, journeys: tuple[tuple[str, str], ...]) -> str:
        if len(journeys) == 1:
            origin, destination = journeys[0]
            return self._SINGLE_TEMPLATES[index % len(self._SINGLE_TEMPLATES)].format(
                origin=origin,
                destination=destination,
            ) + self._SCHEMA_SUFFIX
        descriptions = ", then ".join(
            f"{self._ORDINALS[position]} {origin} to {destination}"
            for position, (origin, destination) in enumerate(journeys)
        )
        return self._MULTI_TEMPLATES[index % len(self._MULTI_TEMPLATES)].format(
            journeys=descriptions,
        ) + self._SCHEMA_SUFFIX

    @staticmethod
    def _transfer_count(route: list[dict[str, str]]) -> int:
        return sum(
            current["subway_line"] != next_leg["subway_line"]
            for current, next_leg in zip(route, route[1:])
        )

    @staticmethod
    def _station_lines() -> dict[str, str]:
        builder = SchemaSftCorpusBuilder()
        synthetic_to_human = {
            synthetic: human
            for human, synthetic in builder._STATION_TO_SYNTHETIC.items()
        }
        return {
            synthetic_to_human[station]: line
            for line, stations in builder._LINES.items()
            for station in stations
        }

    def _validate(
        self,
        cases: list[dict[str, object]],
        blocked_pairs: set[tuple[str, str]],
    ) -> None:
        if len(cases) != self.CASE_COUNT:
            raise RuntimeError("Generated held-out suite must contain 500 cases.")
        itineraries = [self._journeys(case) for case in cases]
        if len(set(itineraries)) != self.CASE_COUNT:
            raise RuntimeError("Generated held-out suite contains duplicate itineraries.")
        if any(pair in blocked_pairs for itinerary in itineraries for pair in itinerary):
            raise RuntimeError("Generated held-out suite overlaps training or baseline routes.")
        for case in cases:
            route = case["expected_answer"]["answer"]
            if any(
                current["to_station"] != next_leg["from_station"]
                for current, next_leg in zip(route, route[1:])
            ):
                raise RuntimeError("Generated route is not connected.")

    @staticmethod
    def _journeys(case: dict[str, object]) -> tuple[tuple[str, str], ...]:
        return tuple(
            (str(journey[0]), str(journey[2]))
            for journey in case["expectation"]["journeys"]
        )
