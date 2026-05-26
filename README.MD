# Mini Industrial Monitoring Platform

Starter scaffold for a small industrial AI-style monitoring system:

- Python simulator publishes machine metrics over MQTT
- Mosquitto brokers the messages
- FastAPI consumes MQTT data and stores readings in PostgreSQL
- FastAPI also serves a simple dashboard UI
- Docker Compose runs the stack
- Telemetry model: `vibration`, `acoustic`, `power_draw` for 2 machines

## Run

```bash
docker compose up --build
```

Open:

- Dashboard: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (`admin` / `admin`)

## API

- `GET /health`
- `GET /metrics`
- `GET /machines`
- `GET /latest`
- `GET /readings?machine_id=press-01`

## Monitoring

- Prometheus scrapes the FastAPI app and PostgreSQL exporter every 15 seconds
- Grafana is pre-provisioned with a Prometheus datasource and a starter dashboard
- The dashboard includes:
  - app uptime, request rate, and p95 latency
  - PostgreSQL exporter health, active connections, transactions, and database size

## Current demo machines

- `press-01`
- `motor-02`
