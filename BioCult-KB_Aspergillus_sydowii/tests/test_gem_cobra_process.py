from fastapi.testclient import TestClient

from web_app import gem_cobra, process_simulation
from web_app.main import app
from web_app.schemas import GemFbaInput, MediaOptimizationInput, ProcessSimulationInput


def test_gem_lite_exports_and_reloads_sbml():
    path = gem_cobra.export_sbml_model(force=True)
    model = gem_cobra.load_sbml_model()

    assert path.exists()
    assert model.id == gem_cobra.MODEL_ID
    assert len(model.reactions) >= 10
    assert len(model.metabolites) >= 10


def test_fba_objectives_are_feasible_and_medium_sensitive():
    rich = MediaOptimizationInput(molasses_g_l=30, peptone_g_l=95, collagen_g_l=8, aeration_vvm=1.1, rpm=280)
    poor = MediaOptimizationInput(molasses_g_l=5, peptone_g_l=20, collagen_g_l=0, aeration_vvm=0.2, rpm=120)

    for objective in ("biomass", "collagenolytic_product", "balanced"):
        result = gem_cobra.run_fba(GemFbaInput(medium=rich, objective=objective))
        assert result["available"] is True
        assert result["status"] == "optimal"
        assert result["objective_value"] is not None

    rich_result = gem_cobra.run_fba(GemFbaInput(medium=rich, objective="balanced"))
    poor_result = gem_cobra.run_fba(GemFbaInput(medium=poor, objective="balanced"))
    assert rich_result["objective_value"] > poor_result["objective_value"]


def test_process_modes_produce_distinct_profiles_with_fba_capacity():
    results = {
        mode: process_simulation.simulate_process(ProcessSimulationInput(process_mode=mode, duration_h=48, step_h=24))
        for mode in ("batch", "fed_batch", "continuous")
    }

    assert all(result["fba_status"] == "optimal" for result in results.values())
    assert results["fed_batch"]["profile"][-1]["volume_l"] > results["batch"]["profile"][-1]["volume_l"]
    assert results["batch"]["profile"][-1]["molasses_g_l"] != results["continuous"]["profile"][-1]["molasses_g_l"]
    assert results["batch"]["profile"][-1]["fba_mu_capacity_h"] > 0


def test_gem_and_process_api_contracts():
    client = TestClient(app)

    summary = client.get("/api/gem/summary")
    assert summary.status_code == 200
    assert summary.json()["status"] == "ready"

    fba = client.post(
        "/api/gem/fba",
        json={
            "objective": "balanced",
            "medium": {"molasses_g_l": 24, "peptone_g_l": 90, "collagen_g_l": 8, "aeration_vvm": 1.0, "rpm": 260},
        },
    )
    assert fba.status_code == 200
    assert fba.json()["status"] == "optimal"

    simulation = client.post(
        "/api/process-simulation",
        json={
            "process_mode": "fed_batch",
            "medium": {"molasses_g_l": 24, "peptone_g_l": 90, "collagen_g_l": 8, "aeration_vvm": 1.0, "rpm": 260},
        },
    )
    assert simulation.status_code == 200
    payload = simulation.json()
    assert payload["process_mode"] == "fed_batch"
    assert len(payload["profile"]) > 3

    sbml = client.get("/api/gem/sbml")
    assert sbml.status_code == 200
    assert "sbml" in sbml.text[:200].lower()
