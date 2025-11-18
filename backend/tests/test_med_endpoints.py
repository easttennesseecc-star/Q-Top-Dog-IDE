from fastapi.testclient import TestClient
from backend.main import app

def test_fhir_to_omop(test_client):
    resp = test_client.post("/med/interop/fhir/to-omop", json={"resourceType":"Bundle","entry":[{"resource":{"resourceType":"Patient","id":"p1","gender":"male","birthDate":"1990-01-01"}}]})
    assert resp.status_code == 200
    j = resp.json()
    assert j["status"] == "ok"
    assert j["format"] == "omop"


def test_omop_to_fhir(test_client):
    resp = test_client.post("/med/interop/omop/to-fhir", json={"data":{"patient":{"person_source_value":"p1","gender_concept":"male","birth_datetime":"1990-01-01"}}})
    assert resp.status_code == 200
    j = resp.json()
    assert j["status"] == "ok"
    assert j["format"] == "fhir"


def test_narrative(test_client):
    resp = test_client.post("/med/diagnostic/narrative", json={"text":"CBC results: WNL","reading_level":"patient-friendly"})
    assert resp.status_code == 200
    j = resp.json()
    assert j["status"] == "ok"
    assert "narrative" in j


def test_trials_simulate(test_client):
    body = {
        "title":"T",
        "population_size": 10,
        "duration_days": 7,
        "arms": [
            {"name":"c","size":5,"effect_mean":0,"effect_std":1},
            {"name":"t","size":5,"effect_mean":0.5,"effect_std":1}
        ]
    }
    resp = test_client.post("/med/trials/simulate", json=body)
    assert resp.status_code == 200
    j = resp.json()
    assert j["status"] == "ok"
    assert len(j.get("arms", [])) == 2
