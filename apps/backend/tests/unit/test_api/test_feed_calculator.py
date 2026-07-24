import pytest


@pytest.mark.unit
class TestFeedCalculator:
    def test_calculate_without_auth(self, client):
        response = client.post("/api/feed-calculator/calculate", json={
            "colony_count": 3,
            "colony_strength": "medium",
            "season": "winter",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["kg_sugar_per_colony"] == 14.0
        assert data["total_kg_sugar"] == 42.0
        assert "formula_note" in data

    def test_strong_colony_needs_more_than_weak(self, client):
        weak = client.post("/api/feed-calculator/calculate", json={
            "colony_count": 1, "colony_strength": "weak", "season": "winter",
        }).json()
        strong = client.post("/api/feed-calculator/calculate", json={
            "colony_count": 1, "colony_strength": "strong", "season": "winter",
        }).json()
        assert strong["kg_sugar_per_colony"] > weak["kg_sugar_per_colony"]

    def test_spring_buildup_is_smaller_than_winter(self, client):
        winter = client.post("/api/feed-calculator/calculate", json={
            "colony_count": 1, "colony_strength": "medium", "season": "winter",
        }).json()
        spring = client.post("/api/feed-calculator/calculate", json={
            "colony_count": 1, "colony_strength": "medium", "season": "spring_buildup",
        }).json()
        assert spring["kg_sugar_per_colony"] < winter["kg_sugar_per_colony"]

    def test_invalid_colony_count_rejected(self, client):
        response = client.post("/api/feed-calculator/calculate", json={
            "colony_count": 0, "colony_strength": "medium", "season": "winter",
        })
        assert response.status_code == 422

    def test_invalid_strength_rejected(self, client):
        response = client.post("/api/feed-calculator/calculate", json={
            "colony_count": 1, "colony_strength": "gigantic", "season": "winter",
        })
        assert response.status_code == 422
