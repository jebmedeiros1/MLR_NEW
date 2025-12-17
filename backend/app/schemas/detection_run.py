from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.schemas.tag import TagRead


class DetectionRunBase(BaseModel):
    model_name: str
    parameters: Optional[Dict[str, Any]] = None


class DetectionRunCreate(DetectionRunBase):
    tags: List[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class DetectionRunRead(DetectionRunBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
