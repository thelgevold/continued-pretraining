from dataclasses import dataclass


@dataclass(frozen=True)
class ReasoningExpectation:
    journeys: tuple[tuple[str, str], ...]
    require_complete_routes: bool
    transfer_count: int | None
    allowed_stations: tuple[str, ...]
    ordinal_positions: tuple[tuple[int, str], ...]
    station_line_memberships: tuple[tuple[str, tuple[str, ...]], ...] = ()
