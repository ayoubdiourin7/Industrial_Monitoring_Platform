from contextlib import asynccontextmanager
from pathlib import Path
import time

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, Histogram, Counter, generate_latest
from sqlalchemy import desc, distinct, select, text
from sqlalchemy.orm import Session

from .database import Base, engine, get_session
from .models import Reading
from .mqtt_consumer import start_mqtt_consumer
from .schemas import ReadingOut

APP_START_TIME = time.monotonic()
HTTP_REQUESTS_TOTAL = Counter(
    "app_http_requests_total",
    "Total HTTP requests handled by the FastAPI app.",
    ["method", "path", "status"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "app_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "path"],
)
APP_UPTIME_SECONDS = Gauge(
    "app_uptime_seconds",
    "Seconds since the FastAPI app started.",
)
APP_UPTIME_SECONDS.set_function(lambda: time.monotonic() - APP_START_TIME)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_mqtt_consumer()
    yield


app = FastAPI(title="Mini Industrial Monitoring Platform", lifespan=lifespan)
static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.middleware("http")
async def record_metrics(request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        path=path,
        status=str(response.status_code),
    ).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=request.method,
        path=path,
    ).observe(duration)
    return response


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
