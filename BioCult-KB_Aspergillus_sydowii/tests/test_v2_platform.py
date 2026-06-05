import json

from fastapi.testclient import TestClient

from web_app.core import culture_fluid, reactor_physics
from web_app.db import SessionLocal, init_db
from web_app.main import app
from web_app import models


def test_audit_hash_creation_and_tamper_detection():
    init_db()
    client = TestClient(app)
    response = client.post(
        "/api/audit/log",
        json={
            "user": "operator",
            "session_id": "test-session",
            "action_type": "alert",
            "module": "expert_system",
            "recommendation": "Raise rpm by 20 when pO2 is below 25%.",
            "evidence": {"pO2": 22.5, "kLa": 31.0},
            "confidence": 0.82,
            "decision": "accepted",
        },
    )
    assert response.status_code == 200
    record_id = response.json()["id"]

    verify = client.get(f"/api/audit/verify/{record_id}")
    assert verify.status_code == 200
    assert verify.json()["valid"] is True

    with SessionLocal() as session:
        record = session.query(models.AuditRecord).filter(models.AuditRecord.id == record_id).one()
        record.evidence_json = json.dumps({"pO2": 80.0}, sort_keys=True)
        session.commit()

    tampered = client.get(f"/api/audit/verify/{record_id}")
    assert tampered.status_code == 200
    assert tampered.json()["valid"] is False


def test_dfba_step_and_simulation_endpoints_cover_normal_and_depleted_substrate():
    client = TestClient(app)
    normal = client.post(
        "/api/dfba/step",
        json={"biomass_g_l": 0.8, "molasses_g_l": 18, "do_percent": 60, "dt_h": 6},
    )
    assert normal.status_code == 200
    normal_payload = normal.json()
    assert normal_payload["status"] == "optimal"
    assert normal_payload["dfba_mu_h"] > 0
    assert normal_payload["kLa_h"] > 0

    depleted = client.post(
        "/api/dfba/step",
        json={"biomass_g_l": 2.5, "molasses_g_l": 0, "do_percent": 5, "dt_h": 6},
    )
    assert depleted.status_code == 200
    assert depleted.json()["dfba_mu_h"] == 0

    simulation = client.post("/api/dfba/simulate", json={"duration_h": 48, "step_h": 12})
    assert simulation.status_code == 200
    payload = simulation.json()
    assert len(payload["profile"]) == 5
    assert "OTR_mmol_l_h" in payload["profile"][-1]


def test_transcriptome_eflux_upload_and_fba_fallbacks():
    client = TestClient(app)
    upload = client.post(
        "/api/transcriptome/upload-tpm",
        json={"dataset_id": "test_tpm", "csv_text": "gene_id,TPM\nASPSYDRAFT_1,12\nASPSYDRAFT_2,0\n"},
    )
    assert upload.status_code == 200
    assert upload.json()["gene_count"] == 2

    fba = client.post("/api/transcriptome/fba", json={"dataset_id": "test_tpm"})
    assert fba.status_code == 200
    payload = fba.json()
    assert payload["status"] == "optimal"
    assert "gene_coverage" in payload

    empty = client.post("/api/transcriptome/fba", json={"dataset_id": "missing_tpm"})
    assert empty.status_code == 200
    assert empty.json()["n_reactions_constrained"] == 0


def test_reactor_fluid_scaling_and_doe_contracts():
    fluid = culture_fluid.culture_fluid_state(
        culture_fluid.CultureFluidInput(
            biomass_g_l=2.0,
            molasses_g_l=12.0,
            peptone_g_l=90.0,
            collagen_g_l=5.0,
        )
    )
    reactor = reactor_physics.reactor_state(240, 0.9, fluid["viscosity_mpa_s"], 40)
    assert fluid["viscosity_mpa_s"] > 0
    assert reactor["kla_h"] > 0
    assert reactor["OTR_mmol_l_h"] > 0

    client = TestClient(app)
    scaling = client.post("/api/scaling/predict", json={"target_volume_l": 30, "source_rpm": 220})
    assert scaling.status_code == 200
    assert scaling.json()["recommended_rpm"] > 0

    doe = client.post("/api/doe/generate", json={"n_runs": 8, "seed": 7})
    assert doe.status_code == 200
    doe_payload = doe.json()
    assert doe_payload["n_runs"] == 8
    assert len(doe_payload["runs"]) == 8
