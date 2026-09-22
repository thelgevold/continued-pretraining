import json

from schema_training.handlers.schema_sft_corpus_builder import SchemaSftCorpusBuilder


def test_two_transfer_records_cover_32_unique_journey_pairs() -> None:
    candidates = SchemaSftCorpusBuilder()._candidates(set())

    records = SchemaSftCorpusBuilder()._records(candidates, 2, 100)

    unique_pairs = {
        (record["input"], record["output"])
        for record in records
    }
    assert len(unique_pairs) == 32
    assert all(
        all(
            left["to_station"] == right["from_station"]
            for left, right in zip(route[:-1], route[1:])
        )
        for route in (json.loads(str(record["output"])) for record in records)
    )


def test_one_transfer_records_include_same_line_continuations() -> None:
    builder = SchemaSftCorpusBuilder()
    records = builder._records(builder._candidates(set()), 1, 100)

    routes = [json.loads(str(record["output"])) for record in records]

    assert any(len(route) == 3 for route in routes)
    assert {
        route[0]["subway_line"]
        for route in routes
        if len(route) == 3
    } == {"Blue Line", "Gold Line", "Green Line"}
    assert all(
        sum(left["subway_line"] != right["subway_line"] for left, right in zip(route, route[1:])) == 1
        for route in routes
    )
