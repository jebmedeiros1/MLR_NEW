from app.integrations.pi_client import PIWebAPIClient


def test_parse_series_response_filters_missing_values():
    payload = {
        "Items": [
            {"Timestamp": "2024-01-01T00:00:00Z", "Value": 1},
            {"Timestamp": "2024-01-01T00:01:00Z", "Value": None},
            {"Timestamp": None, "Value": 2},
        ]
    }

    parsed = PIWebAPIClient.parse_series_response(payload)

    assert parsed == [
        {"timestamp": "2024-01-01T00:00:00Z", "value": 1.0},
    ]
