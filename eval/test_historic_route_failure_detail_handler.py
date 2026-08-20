from eval.handlers.historic_route_failure_detail_handler import (
    HistoricRouteFailureDetailHandler,
)


def test_details_identify_the_missing_destination_side_leg() -> None:
    handler = HistoricRouteFailureDetailHandler()
    expected_answer = {
        "answer": {
            "result": {
                "site": "Founder's Square",
                "origin_station": "Museum District Station",
                "subway_route": [
                    {
                        "subway_line": "Green Line",
                        "from_station": "Museum District Station",
                        "to_station": "Central Station",
                        "target_site": "Founder's Square",
                    },
                    {
                        "subway_line": "Blue Line",
                        "from_station": "Central Station",
                        "to_station": "Founder's Square",
                        "target_site": "Founder's Square",
                    },
                ],
                "transfer_stations": ["Central Station"],
            }
        }
    }
    actual_answer = {
        "answer": {
            "result": {
                "site": "Founder's Square",
                "origin_station": "Museum District Station",
                "subway_route": [
                    {
                        "subway_line": "Green Line",
                        "from_station": "Museum District Station",
                        "to_station": "Central Station",
                        "target_site": "Heritage Theater",
                    }
                ],
                "transfer_stations": ["Central Station"],
            }
        }
    }

    details = handler.create_details(expected_answer, actual_answer)

    assert details == [
        "Missing route leg 2: 'Blue Line' from 'Central Station' "
        "to \"Founder's Square\"."
    ]
