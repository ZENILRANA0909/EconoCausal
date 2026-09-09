def test_health_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "FirmSight"


def test_system_info_returns_platform_details(client):
    response = client.get("/api/system-info")
    assert response.status_code == 200
    body = response.json()
    assert "system" in body
    assert "machine" in body


def test_tools_endpoint_lists_expected_tools(client):
    response = client.get("/api/tools")
    assert response.status_code == 200
    body = response.json()
    names = [item["name"] for item in body]
    assert "binwalk" in names
    assert "tcpdump" in names
    assert "python3" in names
