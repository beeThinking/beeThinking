from unittest.mock import patch

import pytest
import requests


@pytest.fixture
def apiary_with_coords(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={
        "stock_number": "Map Stand",
        "name": "Map Stand",
        "latitude": 48.1374,
        "longitude": 11.5755,
    })
    assert response.status_code == 201
    return response.json()


def _fake_forecast_response():
    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "current": {
                    "temperature_2m": 18.5,
                    "relative_humidity_2m": 55,
                    "precipitation": 0,
                    "weather_code": 1,
                    "wind_speed_10m": 5,
                },
                "daily": {
                    "time": ["2026-07-25", "2026-07-26", "2026-07-27"],
                    "weather_code": [1, 2, 61],
                    "temperature_2m_min": [12.0, 13.0, 11.5],
                    "temperature_2m_max": [22.0, 23.5, 19.0],
                    "precipitation_sum": [0.0, 0.0, 3.2],
                },
            }
    return FakeResponse()


@pytest.mark.unit
class TestMapApiaries:
    def test_list_map_apiaries(self, authenticated_client, apiary_with_coords):
        client, _ = authenticated_client
        response = client.get("/api/map/apiaries")
        assert response.status_code == 200
        markers = response.json()
        assert any(m["id"] == apiary_with_coords["id"] for m in markers)
        marker = next(m for m in markers if m["id"] == apiary_with_coords["id"])
        assert marker["latitude"] == 48.1374

    def test_requires_auth(self, client):
        assert client.get("/api/map/apiaries").status_code == 401


@pytest.mark.unit
class TestMapWeatherForecast:
    def test_forecast_returns_current_and_daily(self, authenticated_client, apiary_with_coords):
        client, _ = authenticated_client
        with patch("app.services.inspection_weather.requests.get", return_value=_fake_forecast_response()):
            response = client.get(f"/api/map/apiaries/{apiary_with_coords['id']}/weather")
        assert response.status_code == 200
        data = response.json()
        assert data["current"]["weather_temperature"] == 18.5
        assert len(data["daily"]) == 3
        assert data["daily"][2]["precipitation_sum"] == 3.2

    def test_forecast_404_for_unknown_apiary(self, authenticated_client):
        client, _ = authenticated_client
        assert client.get("/api/map/apiaries/999999/weather").status_code == 404

    def test_forecast_422_when_no_coordinates(self, authenticated_client):
        client, _ = authenticated_client
        apiary = client.post("/api/apiaries", json={"stock_number": "No Coords"}).json()
        response = client.get(f"/api/map/apiaries/{apiary['id']}/weather")
        assert response.status_code == 422

    def test_forecast_provider_failure_returns_503(self, authenticated_client, apiary_with_coords):
        client, _ = authenticated_client
        with patch("app.services.inspection_weather.requests.get", side_effect=requests.Timeout):
            response = client.get(f"/api/map/apiaries/{apiary_with_coords['id']}/weather")
        assert response.status_code == 503
        assert response.json()["detail"] == "Weather provider is unavailable"


@pytest.mark.unit
class TestForagePlants:
    def test_list_forage_plants_is_public_shaped_but_authenticated(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get("/api/map/forage-plants")
        assert response.status_code == 200
        plants = response.json()
        assert len(plants) > 0
        assert "name_de" in plants[0]

    def test_requires_auth(self, client):
        assert client.get("/api/map/forage-plants").status_code == 401
