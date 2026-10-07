from fastapi import FastAPI

from app.api import auth, runs

app = FastAPI(title="et-al", version="0.1.0")
app.include_router(auth.router)
app.include_router(runs.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
