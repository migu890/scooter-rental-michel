import json
from datetime import datetime, timedelta


def create_user(
    db,
    User,
    username="rider1",
    email="rider1@test.ch",
    role="rider",
    password="Passwort123!",
):
    u = User(username=username, email=email, role=role)
    u.set_password(password)
    # Token wird im Register normalerweise gesetzt – für Tests setzen wir ihn optional später
    db.session.add(u)
    db.session.commit()
    return u


def create_provider_and_scooter(db, User, Scooter):
    provider = create_user(
        db, User, "provider1", "provider1@test.ch", "provider", "Passwort123!"
    )
    scooter = Scooter(
        scooter_code="SC-001",
        battery_percent=90,
        latitude=47.0,
        longitude=8.0,
        status="available",
        provider_id=provider.id,
    )
    db.session.add(scooter)
    db.session.commit()
    return provider, scooter


def test_api_login_invalid(client):
    resp = client.post("/api/login", json={"username": "nope", "password": "nope"})
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "invalid credentials"


def test_api_login_and_token_then_rentals_me_unauthorized(client, app):
    from app.extensions import db
    from app.models import User

    create_user(db, User, "rider2", "rider2@test.ch", "rider", "Passwort123!")
    resp = client.get("/api/rentals/me")
    assert resp.status_code == 401


def test_api_scooters_returns_list(client, app):
    from app.extensions import db
    from app.models import User, Scooter

    create_provider_and_scooter(db, User, Scooter)

    resp = client.get("/api/scooters")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert any(s["code"] == "SC-001" for s in data)


def test_rental_service_start_and_end(app):
    from app.extensions import db
    from app.models import User, Scooter, Rental
    from app.services.rental_service import start_rental, end_rental

    provider, scooter = create_provider_and_scooter(db, User, Scooter)
    rider = create_user(db, User, "rider3", "rider3@test.ch", "rider", "Passwort123!")

    # Start rental
    r = start_rental(rider=rider, scooter_code="SC-001", lat=47.1, lng=8.1)
    assert r.id is not None
    assert r.end_time is None

    # simulate time passing by setting start_time to past
    r.start_time = datetime.utcnow() - timedelta(minutes=10)
    db.session.commit()

    # End rental
    r2 = end_rental(rider=rider, rental_id=r.id, kilometers=1.2, lat=47.2, lng=8.2)
    assert r2.end_time is not None
    assert float(r2.kilometers) == 1.2
    assert r2.total_price_chf is not None

    # Scooter should be available again
    s = Scooter.query.filter_by(scooter_code="SC-001").first()
    assert s.status == "available"
    assert s.latitude == 47.2
    assert s.longitude == 8.2


def test_api_login_then_rentals_me_returns_data(client, app):
    from app.extensions import db
    from app.models import User, Scooter
    from app.services.rental_service import start_rental, end_rental

    # create provider+scooter and rider
    _, scooter = create_provider_and_scooter(db, User, Scooter)
    rider = create_user(db, User, "rider4", "rider4@test.ch", "rider", "Passwort123!")

    # create a rental so rentals/me has something
    r = start_rental(rider=rider, scooter_code="SC-001", lat=47.0, lng=8.0)
    r.start_time = datetime.utcnow() - timedelta(minutes=5)
    db.session.commit()
    end_rental(rider=rider, rental_id=r.id, kilometers=0.5, lat=47.0, lng=8.0)

    # login to get token
    resp_login = client.post(
        "/api/login", json={"username": "rider4", "password": "Passwort123!"}
    )
    assert resp_login.status_code == 200
    token = resp_login.get_json()["token"]
    assert token

    resp = client.get("/api/rentals/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["scooter"] == "SC-001"
