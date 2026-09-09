def test_full_analysis_pipeline(client, uploaded_firmware_id):
    extract_response = client.post(f"/api/firmware/{uploaded_firmware_id}/extract")
    assert extract_response.status_code == 200
    extract_body = extract_response.json()
    assert extract_body["status"] == "completed"
    assert extract_body["file_count"] > 0

    analyze_response = client.post(
        f"/api/firmware/{uploaded_firmware_id}/analyze", json={"force_demo": False}
    )
    assert analyze_response.status_code == 200
    assert analyze_response.json()["findings_count"] > 0

    files_response = client.get(f"/api/firmware/{uploaded_firmware_id}/files")
    assert files_response.status_code == 200
    assert files_response.json()["is_directory"] is True

    findings_response = client.get(f"/api/firmware/{uploaded_firmware_id}/findings")
    assert findings_response.status_code == 200
    assert len(findings_response.json()) > 0

    network_response = client.get(f"/api/firmware/{uploaded_firmware_id}/network")
    assert network_response.status_code == 200
    assert len(network_response.json()) > 0

    threats_response = client.get(f"/api/firmware/{uploaded_firmware_id}/threats")
    assert threats_response.status_code == 200
    threat_body = threats_response.json()
    assert threat_body["level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert len(threat_body["reasons"]) > 0

    report_response = client.get(f"/api/firmware/{uploaded_firmware_id}/report")
    assert report_response.status_code == 200
    report_body = report_response.json()
    assert report_body["sha256"]
    assert report_body["threat_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def test_emulation_lifecycle(client, uploaded_firmware_id):
    client.post(f"/api/firmware/{uploaded_firmware_id}/extract")
    client.post(f"/api/firmware/{uploaded_firmware_id}/analyze", json={"force_demo": False})

    start_response = client.post(
        f"/api/firmware/{uploaded_firmware_id}/emulate", json={"force_demo": False}
    )
    assert start_response.status_code == 200
    session_body = start_response.json()
    assert session_body["status"] == "running"

    stop_response = client.post(f"/api/firmware/{uploaded_firmware_id}/stop")
    assert stop_response.status_code == 200
    assert stop_response.json()["status"] == "stopped"


def test_demo_mode_labels_results_correctly(client, uploaded_firmware_id):
    client.post(f"/api/firmware/{uploaded_firmware_id}/extract")
    client.post(f"/api/firmware/{uploaded_firmware_id}/analyze", json={"force_demo": False})
    report_response = client.get(f"/api/firmware/{uploaded_firmware_id}/report")
    body = report_response.json()
    assert "is_demo" in body


def test_activity_feed_records_events(client, uploaded_firmware_id):
    client.post(f"/api/firmware/{uploaded_firmware_id}/extract")
    response = client.get("/api/activity")
    assert response.status_code == 200
    events = response.json()
    assert any(item["firmware_id"] == uploaded_firmware_id for item in events)


def test_operations_on_nonexistent_firmware_return_404(client):
    assert client.post("/api/firmware/nonexistent/extract").status_code == 404
    assert client.get("/api/firmware/nonexistent/findings").status_code == 404
    assert client.get("/api/firmware/nonexistent/network").status_code == 404
    assert client.get("/api/firmware/nonexistent/threats").status_code == 404
    assert client.get("/api/firmware/nonexistent/report").status_code == 404
