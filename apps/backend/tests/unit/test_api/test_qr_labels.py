import pytest


@pytest.mark.unit
@pytest.mark.api
class TestQrEndpoints:
    def test_hive_qr_svg(self, authenticated_client):
        client, _ = authenticated_client
        apiary = client.post("/api/apiaries", json={"stock_number": "QR", "name": "QR"}).json()
        hive = client.post("/api/hives", json={"name": "QR Volk", "apiary_id": apiary["id"]}).json()

        response = client.get(f"/api/hives/{hive['id']}/qr.svg")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/svg+xml")
        assert f"/stock-card/{hive['id']}" not in response.text  # QR encodes, not embeds, the URL
        assert "<svg" in response.text

    def test_qr_label_sheet_pdf(self, authenticated_client):
        client, _ = authenticated_client
        apiary = client.post("/api/apiaries", json={"stock_number": "QR2", "name": "QR2"}).json()
        for name in ("Volk 1", "Volk 2", "Volk 3"):
            client.post("/api/hives", json={"name": name, "apiary_id": apiary["id"], "stock_number": name[-1]})

        response = client.get("/api/hives/qr-labels.pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content.startswith(b"%PDF")

    def test_qr_sheet_without_hives_returns_404(self, authenticated_client):
        client, _ = authenticated_client

        assert client.get("/api/hives/qr-labels.pdf").status_code == 404

    def test_qr_requires_authentication(self, client):
        assert client.get("/api/hives/qr-labels.pdf").status_code == 401
