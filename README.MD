# Mini Industrial Monitoring Platform

Starter scaffold for a small industrial AI-style monitoring system:

- Python simulator publishes machine metrics over MQTT
- Mosquitto brokers the messages
- FastAPI consumes MQTT data and stores readings in PostgreSQL
- Docker Compose runs the stack

## Run

```bash
docker compose up --build
```

## API

- `GET /health`
- `GET /machines`
- `GET /latest`
- `GET /readings?machine_id=press-01`
- `GET /anomalies`
