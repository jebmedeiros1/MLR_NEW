from app.db.session import get_db
from app.integrations.pi_client import PIWebAPIClient


def get_pi_client() -> PIWebAPIClient:
    return PIWebAPIClient.from_settings()
