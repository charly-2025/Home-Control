from fastapi import FastAPI

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