def test_create_device(auth_client):
    response = auth_client.post("api/devices", json={
        "name": "Capteur Salon",
        "device_type": "temperature",
        "unit": "°C",
        "location": "Salon",
        "threshold_min": 15.0,
        "threshold_max": 30.0
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Capteur Salon"
    assert "api_key" in data


def test_list_devices(auth_client):
    auth_client.post("api/devices", json={
        "name": "Capteur 1",
        "device_type": "humidity",
        "unit": "%",
        "location": "Chambre"
    })
    response = auth_client.get("api/devices")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_device(auth_client):
    create = auth_client.post("api/devices", json={
        "name": "Ancien nom",
        "device_type": "co2",
        "unit": "ppm",
        "location": "Bureau"
    })
    device_id = create.json()["id"]

    response = auth_client.put(f"api/devices/{device_id}", json={
        "name": "Nouveau nom"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Nouveau nom"


def test_delete_device(auth_client):
    create = auth_client.post("api/devices", json={
        "name": "A supprimer",
        "device_type": "pressure",
        "unit": "hPa",
        "location": "Cave"
    })
    device_id = create.json()["id"]

    response = auth_client.delete(f"api/devices/{device_id}")
    assert response.status_code == 204

    response = auth_client.get(f"api/devices/{device_id}")
    assert response.status_code == 404