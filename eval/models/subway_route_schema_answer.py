import json
from dataclasses import dataclass


@dataclass(frozen=True)
class SubwayRouteSchemaAnswer:
    legs: tuple[tuple[str, str, str], ...]

    @classmethod
    def deserialize(
        cls,
        payload: str | list[object],
    ) -> "SubwayRouteSchemaAnswer":
        decoded_payload = cls._decode_payload(payload)
        return cls(tuple(cls._leg(leg) for leg in decoded_payload))

    @staticmethod
    def _decode_payload(payload: str | list[object]) -> list[object]:
        if isinstance(payload, list):
            decoded_payload = payload
        else:
            try:
                decoded_payload = json.loads(payload)
            except json.JSONDecodeError as error:
                raise ValueError("Answer is not valid JSON.") from error
        if not isinstance(decoded_payload, list) or not decoded_payload:
            raise ValueError("Answer must be a non-empty JSON array.")
        return decoded_payload

    @classmethod
    def _leg(cls, value: object) -> tuple[str, str, str]:
        if not isinstance(value, dict) or set(value) != {
            "from_station",
            "to_station",
            "subway_line",
        }:
            raise ValueError("Each route leg must match the required schema.")
        if not all(isinstance(property_value, str) for property_value in value.values()):
            raise ValueError("Each route leg property must be a string.")
        return (
            cls._normalize(value["from_station"]),
            cls._normalize(value["to_station"]),
            cls._normalize_line(value["subway_line"]),
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return value.strip().lower()

    @classmethod
    def _normalize_line(cls, value: str) -> str:
        normalized_value = cls._normalize(value).replace("_", " ")
        if normalized_value not in {"blue line", "gold line", "green line"}:
            raise ValueError("subway_line must be Blue Line, Gold Line, or Green Line.")
        return normalized_value
