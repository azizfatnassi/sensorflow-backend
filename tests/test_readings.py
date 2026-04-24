def test_ingest_reading(auth_client):
    create = auth_client.post("api/devices", json={
        "name": "Capteur",
        "device_type": "temperature",
        "unit": "°C",
        "location": "Test"
    })
    api_key = create.json()["api_key"]

    response = auth_client.post("api/readings", json={"value": 22.5},
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 201
    assert response.json()["value"] == 22.5


def test_reading_triggers_alert(auth_client):
    create = auth_client.post("api/devices", json={
        "name": "Capteur",
        "device_type": "temperature",
        "unit": "°C",
        "location": "Test",
        "threshold_max": 25.0
    })
    api_key = create.json()["api_key"]
    device_id = create.json()["id"]

    auth_client.post("api/readings", json={"value": 35.0},
        headers={"X-API-Key": api_key}
    )

    alerts = auth_client.get(f"api/alerts?device_id={device_id}")
    assert len(alerts.json()) > 0


def test_readings_history(auth_client):
    create = auth_client.post("api/devices", json={
        "name": "Capteur",
        "device_type": "temperature",
        "unit": "°C",
        "location": "Test"
    })
    api_key = create.json()["api_key"]
    device_id = create.json()["id"]

    for value in [20.0, 21.0, 22.0]:
        auth_client.post("api/readings", json={"value": value},
            headers={"X-API-Key": api_key}
        )

    response = auth_client.get(f"api/devices/{device_id}/readings")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 3