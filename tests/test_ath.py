def test_register_success(client):
    """Un nouvel utilisateur peut s'enregistrer."""
    response = client.post("/auth/register", json={
        "email": "yassine@test.com",
        "password": "password123",
        "full_name": "Yassine Test"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "yassine@test.com"
    assert "password" not in data  # le mot de passe ne doit JAMAIS être renvoyé


def test_register_duplicate_email(client):
    """On ne peut pas créer deux comptes avec le même email."""
    payload = {"email": "double@test.com", "password": "abc123", "full_name": "Double"}
    client.post("/auth/register", json=payload)  # premier enregistrement
    response = client.post("/auth/register", json=payload)  # doublon
    assert response.status_code == 400


def test_login_success(client):
    """Un utilisateur enregistré peut se connecter et reçoit un token."""
    # D'abord on crée le compte
    client.post("/auth/register", json={
        "email": "login@test.com",
        "password": "secret123",
        "full_name": "Login User"
    })
    # OAuth2 attend du form-data, pas du JSON
    response = client.post("/auth/token", data={
        "username": "login@test.com",
        "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Mauvais mot de passe → 401."""
    client.post("/auth/register", json={
        "email": "wrong@test.com",
        "password": "correctpass",
        "full_name": "Wrong Pass"
    })
    response = client.post("/auth/token", data={
        "username": "wrong@test.com",
        "password": "MAUVAIS"
    })
    assert response.status_code == 401


def test_get_me_authenticated(client):
    """Avec un token valide, /auth/me retourne le bon utilisateur."""
    # 1. Register
    client.post("/auth/register", json={
        "email": "me@test.com",
        "password": "mepass123",
        "full_name": "Me User"
    })
    # 2. Login → récupère le token
    login = client.post("/auth/token", data={
        "username": "me@test.com",
        "password": "mepass123"
    })
    token = login.json()["access_token"]

    # 3. Appel protégé avec le token dans le header
    response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"


def test_get_me_without_token(client):
    """/auth/me sans token → 401."""
    response = client.get("/auth/me")
    assert response.status_code == 401