from dataclasses import dataclass
import os

from fastapi import FastAPI, HTTPException
import pymysql
import uvicorn

app = FastAPI(title="worker")


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    user: str
    password: str
    name: str


def load_database_settings() -> DatabaseSettings:
    raw_port = os.getenv("DB_PORT", "3306")
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError("DB_PORT must be an integer.") from exc

    return DatabaseSettings(
        host=os.getenv("DB_HOST", "mariadb"),
        port=port,
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "apppassword"),
        name=os.getenv("DB_NAME", "appdb"),
    )


def verify_database_connection(settings: DatabaseSettings) -> None:
    connection = pymysql.connect(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password,
        database=settings.name,
        connect_timeout=5,
        read_timeout=5,
        write_timeout=5,
    )
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()


@app.get("/")
def read_root() -> dict[str, object]:
    try:
        settings = load_database_settings()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    try:
        verify_database_connection(settings)
    except (pymysql.MySQLError, OSError) as exc:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {exc}") from exc

    return {
        "message": "hello world",
        "database": {
            "host": settings.host,
            "port": settings.port,
            "user": settings.user,
            "name": settings.name,
        },
    }


def main() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
