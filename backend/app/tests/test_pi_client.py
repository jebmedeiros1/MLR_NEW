from app.integrations.pi_client import PIVNodeClient


def test_parse_series_response_filters_missing_values():
    payload = {
        "items": [
            {"timestamp": "2024-01-01T00:00:00Z", "value": 1},
            {"timestamp": "2024-01-01T00:01:00Z", "value": None},
            {"timestamp": None, "value": 2},
        ]
    }

    parsed = PIVNodeClient.parse_series_response(payload)

    assert parsed == [
        {"timestamp": "2024-01-01T00:00:00Z", "value": 1.0},
    ]
