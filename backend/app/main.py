from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import desc, distinct, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_session
from .models import Reading
from .mqtt_consumer import start_mqtt_consumer
from .schemas import ReadingOut


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_mqtt_consumer()
    yield


app = FastAPI(title="Mini Industrial Monitoring Platform", lifespan=lifespan)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/machines")
def list_machines(session: Session = Depends(get_session)) -> list[str]:
    statement = select(distinct(Reading.machine_id)).order_by(Reading.machine_id)
    return list(session.scalars(statement).all())


@app.get("/latest", response_model=list[ReadingOut])
def latest_readings(session: Session = Depends(get_session)) -> list[Reading]:
    machine_ids = session.scalars(select(distinct(Reading.machine_id))).all()
    results: list[Reading] = []

    for machine_id in machine_ids:
        statement = (
            select(Reading)
            .where(Reading.machine_id == machine_id)
            .order_by(desc(Reading.timestamp))
            .limit(1)
        )
        reading = session.scalar(statement)
        if reading is not None:
            results.append(reading)

    return results


@app.get("/readings", response_model=list[ReadingOut])
def machine_readings(
    machine_id: str,
    limit: int = 50,
    session: Session = Depends(get_session),
) -> list[Reading]:
    statement = (
        select(Reading)
        .where(Reading.machine_id == machine_id)
        .order_by(desc(Reading.timestamp))
        .limit(limit)
    )
    return list(session.scalars(statement).all())


@app.get("/anomalies", response_model=list[ReadingOut])
def anomalies(session: Session = Depends(get_session), limit: int = 50) -> list[Reading]:
    statement = (
        select(Reading)
        .where(Reading.is_anomaly.is_(True))
        .order_by(desc(Reading.timestamp))
        .limit(limit)
    )
    return list(session.scalars(statement).all())
