import json
from dataclasses import dataclass


@dataclass(frozen=True)
class StructuredReasoningAnswer:
    operation: str
    serialized_result: str

    @classmethod
    def deserialize(
        cls,
        payload: str | dict[str, object],
    ) -> "StructuredReasoningAnswer":
        decoded_payload = cls._decode_payload(payload)
        return cls._from_decoded_payload(decoded_payload)

    @classmethod
    def _decode_payload(
        cls,
        payload: str | dict[str, object],
    ) -> dict[str, object]:
        if isinstance(payload, dict):
            return payload
        try:
            decoded_payload = json.loads(payload)
        except json.JSONDecodeError as error:
            raise ValueError("Answer is not valid JSON.") from error
        if not isinstance(decoded_payload, dict):
            raise ValueError("Answer must be a JSON object.")
        return decoded_payload

    @classmethod
    def _from_decoded_payload(
        cls,
        payload: dict[str, object],
    ) -> "StructuredReasoningAnswer":
        route_legs = cls._extract_subway_route_legs(payload)
        if route_legs is not None:
            normalized_route = cls._normalize_result({"legs": route_legs})
            return cls(
                "subway_route",
                cls._serialize_result(normalized_route["legs"]),
            )
        if set(payload) != {"answer"} or not isinstance(payload["answer"], dict):
            raise ValueError("Answer requires one answer object.")
        answer = payload["answer"]
        if set(answer) != {"operation", "result"}:
            raise ValueError("Answer payload requires operation and result fields.")
        operation = answer["operation"]
        if not isinstance(operation, str):
            raise ValueError("Answer operation must be a string.")
        result = cls._remove_non_material_historic_route_properties(
            operation,
            answer["result"],
        )
        return cls(
            cls._normalize_string(operation),
            cls._serialize_result(cls._normalize_result(result)),
        )

    @classmethod
    def _extract_subway_route_legs(
        cls,
        payload: dict[str, object],
    ) -> list[dict[str, str]] | None:
        route_legs: list[dict[str, str]] = []
        cls._append_subway_route_legs(payload, route_legs)
        return route_legs or None

    @classmethod
    def _append_subway_route_legs(
        cls,
        value: object,
        route_legs: list[dict[str, str]],
    ) -> None:
        if isinstance(value, dict):
            for property_name in ("legs", "route"):
                legs = cls._canonical_route_legs(value.get(property_name))
                if legs is not None:
                    route_legs.extend(legs)
                    return
            for nested_value in value.values():
                cls._append_subway_route_legs(nested_value, route_legs)
            return
        if isinstance(value, list):
            for nested_value in value:
                cls._append_subway_route_legs(nested_value, route_legs)

    @classmethod
    def _canonical_route_legs(cls, value: object) -> list[dict[str, str]] | None:
        if not isinstance(value, list) or not value:
            return None
        if not all(cls._is_supported_route_leg(leg) for leg in value):
            return None
        return [cls._route_leg(leg) for leg in value]

    @classmethod
    def _is_supported_route_leg(cls, value: object) -> bool:
        return (
            cls._is_subway_route_leg(value)
            or cls._is_simple_route_leg(value)
            or cls._is_detailed_route_leg(value)
            or cls._is_compact_route_leg(value)
        )

    @staticmethod
    def _is_subway_route_leg(value: object) -> bool:
        if not isinstance(value, dict):
            return False
        required_properties = {"subway_line", "from_station", "to_station"}
        return required_properties.issubset(value) and all(
            isinstance(value[property_name], str)
            for property_name in required_properties
        )

    @staticmethod
    def _is_simple_route_leg(value: object) -> bool:
        if not isinstance(value, dict):
            return False
        required_properties = {"line", "from", "to"}
        return required_properties.issubset(value) and all(
            isinstance(value[property_name], str)
            for property_name in required_properties
        )

    @staticmethod
    def _is_detailed_route_leg(value: object) -> bool:
        if not isinstance(value, dict):
            return False
        required_properties = {"line", "board_at", "alight_at", "stations"}
        return required_properties.issubset(value) and all(
            isinstance(value[property_name], str)
            for property_name in {"line", "board_at", "alight_at"}
        )

    @staticmethod
    def _is_compact_route_leg(value: object) -> bool:
        if not isinstance(value, dict):
            return False
        stations = value.get("stations")
        return (
            isinstance(value.get("line") or value.get("subway_line"), str)
            and isinstance(stations, list)
            and len(stations) >= 2
            and all(isinstance(station, str) for station in stations)
        )

    @staticmethod
    def _route_leg(value: object) -> dict[str, str]:
        if not isinstance(value, dict):
            raise ValueError("Subway route leg must be an object.")
        if "stations" in value:
            stations = value["stations"]
            if not isinstance(stations, list):
                raise ValueError("Compact subway route leg must list stations.")
            return {
                "subway_line": str(value.get("subway_line") or value["line"]),
                "from_station": str(value.get("board_at") or stations[0]),
                "to_station": str(value.get("alight_at") or stations[-1]),
            }
        if "subway_line" not in value:
            return {
                "subway_line": str(value["line"]),
                "from_station": str(value["from"]),
                "to_station": str(value["to"]),
            }
        return {
            "subway_line": str(value["subway_line"]),
            "from_station": str(value["from_station"]),
            "to_station": str(value["to_station"]),
        }

    @classmethod
    def _remove_non_material_historic_route_properties(
        cls,
        operation: str,
        result: object,
    ) -> object:
        if cls._normalize_string(operation) != "historic_site_route":
            return result
        if not isinstance(result, dict):
            return result
        normalized_result = {
            property_name: value
            for property_name, value in result.items()
            if property_name not in {
                "access_station",
                "origin_station",
                "site",
                "target_site",
                "transfer_stations",
            }
        }
        return cls._remove_historic_route_target_site(normalized_result)

    @staticmethod
    def _remove_historic_route_target_site(
        result: dict[str, object],
    ) -> dict[str, object]:
        route = result.get("subway_route")
        if not isinstance(route, list):
            return result
        return {
            **result,
            "subway_route": [
                {
                    property_name: value
                    for property_name, value in segment.items()
                    if property_name != "target_site"
                }
                if isinstance(segment, dict)
                else segment
                for segment in route
            ],
        }

    @classmethod
    def _normalize_result(cls, value: object) -> object:
        if isinstance(value, dict):
            return {
                key: cls._normalize_property(key, property_value)
                for key, property_value in value.items()
            }
        if isinstance(value, list):
            return [cls._normalize_result(item) for item in value]
        if isinstance(value, str):
            return cls._normalize_string(value)
        return value

    @classmethod
    def _normalize_property(
        cls,
        name: str,
        value: object,
    ) -> object:
        normalized_value = cls._normalize_result(value)
        if name == "legs" and isinstance(normalized_value, list):
            return cls._merge_contiguous_legs(normalized_value)
        if name == "subway_route" and isinstance(normalized_value, list):
            return cls._merge_contiguous_subway_route(normalized_value)
        if name in {"line", "subway_line"} and isinstance(normalized_value, str):
            return cls._normalize_line_name(normalized_value)
        if name != "lines" or not isinstance(normalized_value, list):
            return normalized_value
        normalized_lines = [
            cls._normalize_line_name(line)
            if isinstance(line, str)
            else line
            for line in normalized_value
        ]
        return sorted(normalized_lines)

    @staticmethod
    def _merge_contiguous_legs(legs: list[object]) -> list[object]:
        if StructuredReasoningAnswer._uses_named_leg_properties(legs):
            return StructuredReasoningAnswer._merge_contiguous_subway_route(legs)
        return StructuredReasoningAnswer._merge_contiguous_line_legs(legs)

    @staticmethod
    def _uses_named_leg_properties(legs: list[object]) -> bool:
        if not legs:
            return False
        first_leg = legs[0]
        return isinstance(first_leg, dict) and set(first_leg) == {
            "subway_line",
            "from_station",
            "to_station",
        }

    @staticmethod
    def _merge_contiguous_line_legs(legs: list[object]) -> list[object]:
        merged_legs: list[object] = []
        for leg in legs:
            if not merged_legs:
                merged_legs.append(leg)
                continue
            previous_leg = merged_legs[-1]
            if not StructuredReasoningAnswer._can_merge_legs(previous_leg, leg):
                merged_legs.append(leg)
                continue
            merged_legs[-1] = {
                "line": previous_leg["line"],
                "from": previous_leg["from"],
                "to": leg["to"],
            }
        return merged_legs

    @staticmethod
    def _can_merge_legs(previous_leg: object, current_leg: object) -> bool:
        if not isinstance(previous_leg, dict) or not isinstance(current_leg, dict):
            return False
        required_properties = {"line", "from", "to"}
        if set(previous_leg) != required_properties or set(current_leg) != required_properties:
            return False
        return (
            previous_leg["line"] == current_leg["line"]
            and previous_leg["to"] == current_leg["from"]
        )

    @staticmethod
    def _merge_contiguous_subway_route(route: list[object]) -> list[object]:
        merged_route: list[object] = []
        for segment in route:
            if not merged_route:
                merged_route.append(segment)
                continue
            previous_segment = merged_route[-1]
            if not StructuredReasoningAnswer._can_merge_subway_route(
                previous_segment,
                segment,
            ):
                merged_route.append(segment)
                continue
            merged_route[-1] = {
                "subway_line": previous_segment["subway_line"],
                "from_station": previous_segment["from_station"],
                "to_station": segment["to_station"],
            }
        return merged_route

    @staticmethod
    def _can_merge_subway_route(
        previous_segment: object,
        current_segment: object,
    ) -> bool:
        if not isinstance(previous_segment, dict) or not isinstance(current_segment, dict):
            return False
        required_properties = {"subway_line", "from_station", "to_station"}
        if (
            set(previous_segment) != required_properties
            or set(current_segment) != required_properties
        ):
            return False
        return (
            previous_segment["subway_line"] == current_segment["subway_line"]
            and previous_segment["to_station"] == current_segment["from_station"]
        )

    @staticmethod
    def _normalize_string(value: str) -> str:
        return value.strip().lower()

    @classmethod
    def _normalize_line_name(cls, value: str) -> str:
        normalized_value = cls._normalize_string(value).replace("_", " ")
        if normalized_value.endswith(" line"):
            return normalized_value
        return f"{normalized_value} line"

    @classmethod
    def _serialize_result(cls, result: object) -> str:
        return json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
