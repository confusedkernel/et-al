# et al.

A self-hosted autoresearch agent swarm. You ask a research question; a swarm of LLM agents surveys the literature, writes a cited synthesis, turns the findings into hypotheses, and runs experiments in sandboxes. A web UI shows the swarm working live.

> **Status:** milestone 1 (skeleton). Auth, runs API, worker queue, and a basic UI work; the agent swarm itself is a stub.

## Quickstart

```sh
cp .env.example .env   # set OPENROUTER_API_KEY and SECRET_KEY
docker compose up --build
```

Open http://localhost:8080. The first account you register becomes the admin.

## Development

```sh
# backend (needs Postgres + Redis: `docker compose up postgres redis`, and expose their ports)
cd backend && uv sync && uv run alembic upgrade head && uv run uvicorn app.main:app --reload
uv run arq app.worker.WorkerSettings   # worker, in another shell
uv run pytest                          # tests use in-memory SQLite, no services needed

# frontend (proxies /api to localhost:8000)
cd frontend && pnpm install && pnpm dev
```

## Layout

- `backend/`: FastAPI API, Arq worker, LangGraph swarm (`app/graph`), tools (`app/tools`), SQLAlchemy models and Alembic migrations
- `frontend/`: Next.js app
- `Caddyfile`, `docker-compose.yml`: the self-hosted deployment
