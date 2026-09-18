class SubwayRouteSchema:
    @staticmethod
    def as_dict() -> dict[str, object]:
        return {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["from_station", "to_station", "subway_line"],
                "properties": {
                    "from_station": {"type": "string"},
                    "to_station": {"type": "string"},
                    "subway_line": {
                        "type": "string",
                        "enum": ["Blue Line", "Gold Line", "Green Line"],
                    },
                },
            },
        }
