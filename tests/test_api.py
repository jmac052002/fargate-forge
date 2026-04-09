def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "fargate-forge"
    assert data["status"] == "running"
    assert "version" in data


def test_info_endpoint(client):
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "region" in data
    assert "environment" in data


def test_health_returns_healthy_status(client):
    response = client.get("/health")
    assert response.json()["status"] == "healthy" 