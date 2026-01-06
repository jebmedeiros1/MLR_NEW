from datetime import datetime
from statistics import mean, stdev
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_pi_client
from app.integrations.pi_client import PIWebAPIClient
from app.models.anomaly_event import AnomalyEvent
from app.models.detection_run import DetectionRun
from app.models.tag import Tag
from app.schemas.anomaly_event import AnomalyEventRead
from app.schemas.detection_run import DetectionRunCreate, DetectionRunRead
from app.schemas.tag import TagCreate, TagRead

app = FastAPI(title="MLR Backend")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tags", response_model=List[TagRead])
def list_tags(db: Session = Depends(get_db)):
    tags = db.execute(select(Tag)).scalars().all()
    return tags


@app.post("/tags", response_model=TagRead, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(Tag).where(Tag.name == payload.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    tag = Tag(name=payload.name, description=payload.description)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@app.post("/series")
def fetch_series(
    request: DetectionRunCreate,
    client: PIWebAPIClient = Depends(get_pi_client),
):
    series = client.get_series(request.tags, request.start_time, request.end_time)
    return {"series": series}


@app.get("/series")
def fetch_series_query(
    tags: str = Query(..., description="Comma-separated tag list"),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    client: PIWebAPIClient = Depends(get_pi_client),
):
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    if not tag_list:
        raise HTTPException(status_code=400, detail="At least one tag must be provided")
    series = client.get_series(tag_list, start_time, end_time)
    return {"series": series}


@app.post("/detect", response_model=DetectionRunRead)
def detect_anomalies(
    request: DetectionRunCreate,
    db: Session = Depends(get_db),
    client: PIWebAPIClient = Depends(get_pi_client),
):
    tags = db.execute(select(Tag).where(Tag.name.in_(request.tags))).scalars().all()
    known_tag_names = {tag.name for tag in tags}
    missing = [tag for tag in request.tags if tag not in known_tag_names]
    if missing:
        # create missing tags automatically to mirror existing Dash behavior
        for name in missing:
            tag = Tag(name=name)
            db.add(tag)
            tags.append(tag)
        db.commit()
        db.refresh(tags[0]) if tags else None
        tags = db.execute(select(Tag).where(Tag.name.in_(request.tags))).scalars().all()

    run = DetectionRun(model_name=request.model_name, parameters=request.parameters, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    series = client.get_series(request.tags, request.start_time, request.end_time)

    anomalies: List[AnomalyEvent] = []
    for tag_name, points in series.items():
        values = [point["value"] for point in points]
        if len(values) < 2:
            continue
        avg = mean(values)
        deviation = stdev(values)
        threshold = avg + 2 * deviation
        for point in points:
            if point["value"] > threshold:
                tag_obj = next((t for t in tags if t.name == tag_name), None)
                if not tag_obj:
                    continue
                anomalies.append(
                    AnomalyEvent(
                        tag_id=tag_obj.id,
                        run_id=run.id,
                        detected_at=datetime.fromisoformat(point["timestamp"]),
                        severity=(point["value"] - threshold) if deviation else 0.0,
                        message="Value exceeded threshold",
                        meta={"threshold": threshold},
                    )
                )

    run.status = "completed"
    db.add_all(anomalies)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@app.get("/anomalies", response_model=List[AnomalyEventRead])
def list_anomalies(
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = select(AnomalyEvent)
    if tag:
        query = query.join(Tag).where(Tag.name == tag)
    return db.execute(query).scalars().all()
