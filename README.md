# fastack monorepo

This repository contains three independently deployable services scaffolded from `SPEC.md`:

- `app/`: a hello world FastAPI service managed with `uv`
- `worker/`: a hello world FastAPI service managed with `uv` that validates a MariaDB connection from environment variables
- `mariadb/`: a lightweight MariaDB image wrapper with a simple custom Helm chart

Each service follows the same monorepo shape where applicable:

```text
service-name/
  helm/
    chart/
    values.sample.yaml
  docker-compose.build.yml
  umbrella.yaml
  src/
    app/
  Dockerfile
  pyproject.toml
```

## Service usage

### app

```bash
cd app
uv sync
PYTHONPATH=src uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
docker compose -f docker-compose.build.yml build
helm install app ./helm/chart -f ./helm/values.sample.yaml
```

### worker

```bash
cd worker
uv sync
PYTHONPATH=src DB_HOST=localhost DB_PORT=3306 DB_USER=appuser DB_PASSWORD=apppassword DB_NAME=appdb \
  uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
docker compose -f docker-compose.build.yml build
helm install worker ./helm/chart -f ./helm/values.sample.yaml
```

### mariadb

```bash
cd mariadb
docker compose -f docker-compose.build.yml build
helm install mariadb ./helm/chart -f ./helm/values.sample.yaml
```

## Smoke test the full stack

```bash
docker compose -f umbrella.docker-compose.yml up --build
```

- `app` is available on `http://localhost:8000`
- `worker` is available on `http://localhost:8001`
- MariaDB is exposed on `localhost:33060`

## Umbrella Helm chart

```bash
helm dependency build ./umbrella-test
helm install umbrella-test ./umbrella-test -n umbrella-test --create-namespace
```
