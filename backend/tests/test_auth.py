CREDS = {"email": "Ada@example.com", "password": "correct-horse"}


async def test_first_user_is_admin_and_signed_in(client):
    r = await client.post("/api/auth/register", json=CREDS)
    assert r.status_code == 201
    assert r.json()["is_admin"] is True
    assert r.json()["email"] == "ada@example.com"
    me = await client.get("/api/auth/me")
    assert me.status_code == 200


async def test_second_user_not_admin(client):
    await client.post("/api/auth/register", json=CREDS)
    client.cookies.clear()
    r = await client.post("/api/auth/register", json={"email": "bob@example.com", "password": "password123"})
    assert r.json()["is_admin"] is False


async def test_signup_disabled_after_first_user(client, settings):
    settings.allow_signup = False
    assert (await client.post("/api/auth/register", json=CREDS)).status_code == 201
    r = await client.post("/api/auth/register", json={"email": "bob@example.com", "password": "password123"})
    assert r.status_code == 403


async def test_login_logout(client):
    await client.post("/api/auth/register", json=CREDS)
    client.cookies.clear()
    assert (await client.get("/api/auth/me")).status_code == 401
    assert (await client.post("/api/auth/login", json={**CREDS, "password": "wrong-pass"})).status_code == 401
    assert (await client.post("/api/auth/login", json=CREDS)).status_code == 200
    assert (await client.get("/api/auth/me")).status_code == 200
    await client.post("/api/auth/logout")
    assert (await client.get("/api/auth/me")).status_code == 401


async def test_auth_mode_none(client, settings):
    settings.auth_mode = "none"
    r = await client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["is_admin"] is True
