# Mini Industrial Monitoring Platform

Starter scaffold for a small industrial AI-style monitoring system:

- Python simulator publishes machine metrics over MQTT
- Mosquitto brokers the messages
- FastAPI consumes MQTT data and stores readings in PostgreSQL
- FastAPI also serves a simple dashboard UI
- Docker Compose runs the stack

## Run

```bash
docker compose up --build
```

Open:

- Dashboard: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`

## API

- `GET /health`
- `GET /machines`
- `GET /latest`
- `GET /readings?machine_id=press-01`
- `GET /anomalies`
