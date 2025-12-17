import os
from importlib import reload

from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_detect.db"

import app.core.config as config
import app.db.session as session
import app.main as main
from app.api import deps
from app.db.session import SessionLocal
from app.models import Base

# Reload to ensure settings pick up test database
reload(config)
reload(session)
reload(main)

Base.metadata.create_all(bind=session.engine)


class FakeClient:
    def get_series(self, tags, start_time=None, end_time=None):
        return {tag: [{"timestamp": "2024-01-01T00:00:00", "value": idx + 1} for idx in range(5)] for tag in tags}


client = TestClient(main.app)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_detect_endpoint_runs(fake_client=None):
    main.app.dependency_overrides[deps.get_db] = override_get_db
    main.app.dependency_overrides[deps.get_pi_client] = lambda: FakeClient()

    response = client.post(
        "/detect",
        json={
            "model_name": "test-model",
            "tags": ["T-100"],
            "parameters": {"window": 10},
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "completed"
    assert data["model_name"] == "test-model"
