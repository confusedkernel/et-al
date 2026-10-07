QUESTION = {"question": "What are current methods for long-context retrieval?"}


async def _signup(client, email="ada@example.com"):
    client.cookies.clear()
    await client.post("/api/auth/register", json={"email": email, "password": "password123"})


async def test_create_run_enqueues_job(client, queue):
    await _signup(client)
    r = await client.post("/api/runs", json=QUESTION)
    assert r.status_code == 201
    run = r.json()
    assert run["status"] == "queued"
    assert queue.jobs == [("execute_run", (run["id"],), {"_job_id": f"run:{run['id']}"})]
    assert [x["id"] for x in (await client.get("/api/runs")).json()] == [run["id"]]


async def test_budget_cap(client):
    await _signup(client)
    r = await client.post("/api/runs", json={**QUESTION, "budget_usd": 50})
    assert r.status_code == 402


async def test_runs_are_private(client):
    await _signup(client)
    run_id = (await client.post("/api/runs", json=QUESTION)).json()["id"]
    await _signup(client, "eve@example.com")
    assert (await client.get(f"/api/runs/{run_id}")).status_code == 404
    assert (await client.get("/api/runs")).json() == []


async def test_cancel(client):
    await _signup(client)
    run_id = (await client.post("/api/runs", json=QUESTION)).json()["id"]
    r = await client.post(f"/api/runs/{run_id}/cancel")
    assert r.json()["status"] == "cancelled"
