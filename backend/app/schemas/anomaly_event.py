from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class AnomalyEventBase(BaseModel):
    tag_id: int
    run_id: int
    detected_at: Optional[datetime] = None
    severity: float
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AnomalyEventCreate(AnomalyEventBase):
    pass


class AnomalyEventRead(AnomalyEventBase):
    id: int

    class Config:
        orm_mode = True
