from fastapi import FastAPI

from app.core.settings import settings

app = FastAPI(
    title="Home Control API",
    version="0.1.0",
)


@app.get("/api/")
async def root():
    return {
        "name": "Home Control API",
        "version": "0.1.0",
    }


@app.get("/api/config/")
async def config():
    return {
        "database": settings.MYSQL_DATABASE,
        "host": settings.MYSQL_HOST,
        "port": settings.MYSQL_PORT,
    }