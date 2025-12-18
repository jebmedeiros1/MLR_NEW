from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional

import requests

from app.core.config import get_settings


class PIWebAPIClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.base_url = base_url
        self.username = username
        self.password = password

    @classmethod
    def from_settings(cls) -> "PIWebAPIClient":
        settings = get_settings()
        return cls(
            base_url=settings.pi_base_url,
            username=settings.pi_username,
            password=settings.pi_password,
        )

    def _build_auth(self):
        if self.username and self.password:
            return (self.username, self.password)
        return None

    def get_series(
        self, tags: Iterable[str], start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> Dict[str, List[Dict[str, float]]]:
        if not self.base_url:
            return self._generate_fake_series(tags, start_time, end_time)

        series: Dict[str, List[Dict[str, float]]] = {}
        for tag in tags:
            url = f"{self.base_url}/streams/{tag}/interpolated"
            params = {
                "startTime": (start_time or datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "endTime": (end_time or datetime.utcnow()).isoformat(),
                "interval": "1m",
            }
            response = requests.get(url, params=params, auth=self._build_auth(), timeout=15)
            response.raise_for_status()
            parsed = self.parse_series_response(response.json())
            series[tag] = parsed
        return series

    @staticmethod
    def parse_series_response(payload: dict) -> List[Dict[str, float]]:
        data = []
        items = payload.get("Items") or []
        for item in items:
            timestamp = item.get("Timestamp")
            value = item.get("Value")
            if timestamp is None or value is None:
                continue
            data.append({"timestamp": timestamp, "value": float(value)})
        return data

    def _generate_fake_series(
        self, tags: Iterable[str], start_time: Optional[datetime], end_time: Optional[datetime]
    ) -> Dict[str, List[Dict[str, float]]]:
        start = start_time or datetime.utcnow() - timedelta(minutes=10)
        end = end_time or datetime.utcnow()
        points = 20
        step = (end - start) / points
        series: Dict[str, List[Dict[str, float]]] = {}
        for tag in tags:
            series[tag] = []
            for idx in range(points):
                timestamp = (start + step * idx).isoformat()
                value = float(idx) + 1.0
                series[tag].append({"timestamp": timestamp, "value": value})
        return series
