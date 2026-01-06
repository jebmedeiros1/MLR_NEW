from app.db.session import get_db
from app.integrations.pi_client import PIVNodeClient


def get_pi_client() -> PIVNodeClient:
    return PIVNodeClient.from_settings()
