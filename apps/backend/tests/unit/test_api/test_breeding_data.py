import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Breeding Apiary", "name": "Breeding Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Breeding Hive", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestHiveBreedingCandidateFlag:
    def test_create_hive_defaults_is_breeding_candidate_false(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.post("/api/hives", json={"name": "Alpha", "apiary_id": apiary["id"]})
        assert response.status_code == 201
        assert response.json()["is_breeding_candidate"] is False

    def test_create_hive_with_breeding_candidate_flag(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.post(
            "/api/hives", json={"name": "Alpha", "apiary_id": apiary["id"], "is_breeding_candidate": True}
        )
        assert response.status_code == 201
        assert response.json()["is_breeding_candidate"] is True

    def test_update_hive_breeding_candidate_flag(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.put(f"/api/hives/{hive['id']}", json={"is_breeding_candidate": True})
        assert response.status_code == 200
        assert response.json()["is_breeding_candidate"] is True


@pytest.mark.unit
@pytest.mark.api
class TestQueenBreedingData:
    def test_create_queen_with_breeding_data(self, authenticated_client, hive):
        client, _ = authenticated_client
        payload = {
            "hive_id": hive["id"],
            "year": 2026,
            "rasse": "Carnica",
            "linie": "Sklenar",
            "lebensnummer": "12345",
            "paartyp": "Standbegattet",
            "zuchtbuchnummer_land": "DE",
            "zuchtbuchnummer_lv": "LV12",
            "zuchtbuchnummer_zuechter": "M. Giek",
            "zuchtbuchnummer_nr": "007",
            "zuchtbuchnummer_jahr": 2026,
            "pedigree_pedigree": "AB-123",
            "pedigree_kasten_nr": "K5",
            "pedigree_zuechter": "M. Giek",
            "pedigree_jahr": 2026,
            "belegstelle_land": "DE",
            "belegstelle_verband": "LV",
            "belegstelle_nummer": "42",
            "belegstelle_durchgang": "2",
        }

        response = client.post("/api/queens", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["rasse"] == "Carnica"
        assert data["linie"] == "Sklenar"
        assert data["zuchtbuchnummer_land"] == "DE"
        assert data["zuchtbuchnummer_zuechter"] == "M. Giek"
        assert data["pedigree_pedigree"] == "AB-123"
        assert data["belegstelle_nummer"] == "42"

    def test_update_queen_breeding_data(self, authenticated_client, hive):
        client, _ = authenticated_client
        created = client.post("/api/queens", json={"hive_id": hive["id"], "year": 2026}).json()

        response = client.put(
            f"/api/queens/{created['id']}",
            json={"rasse": "Buckfast", "zuchtbuchnummer_mutter_zuechter": "Zuchtverein"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rasse"] == "Buckfast"
        assert data["zuchtbuchnummer_mutter_zuechter"] == "Zuchtverein"

    def test_breeding_data_defaults_to_null(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.post("/api/queens", json={"hive_id": hive["id"], "year": 2026})

        assert response.status_code == 201
        data = response.json()
        assert data["rasse"] is None
        assert data["zuchtbuchnummer_drohnen_nr"] is None
