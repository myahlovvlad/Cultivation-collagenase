from fastapi.testclient import TestClient

from web_app import system_biology
from web_app.main import app
from web_app.schemas import MediaOptimizationInput


def test_primary_genome_report_uses_refseq_assembly():
    report = system_biology.build_genome_report()
    summary = report["genome_summary"]

    assert report["accession"] == "GCF_001890705.1"
    assert report["assembly_found"] is True
    assert summary["total_bp"] == 34381026
    assert summary["sequence_count"] == 97
    assert summary["n50_bp"] == 2288531
    assert summary["gene_count"] == 13716
    assert summary["protein_count"] == 13578


def test_genome_report_contains_required_potential_categories_and_collagenase_boundary():
    report = system_biology.build_genome_report()
    categories = {item["name"]: item for item in report["categories"]}

    assert {
        "protease_peptidase",
        "secretory_system",
        "transport",
        "carbon_redox_metabolism",
        "secondary_metabolism",
        "cell_cycle",
    } <= set(categories)
    assert categories["protease_peptidase"]["match_count"] > 0
    assert categories["secretory_system"]["match_count"] > 0
    assert report["direct_collagenase_evidence"]["found_direct_annotation"] is False
    assert any("No direct collagenase" in item for item in report["warnings"])


def test_condition_evaluation_responds_to_medium_and_process_inputs():
    limiting = system_biology.evaluate_conditions(
        MediaOptimizationInput(
            molasses_g_l=8,
            peptone_g_l=25,
            collagen_g_l=0,
            pH=5.2,
            aeration_vvm=0.2,
            rpm=120,
        )
    )
    productive = system_biology.evaluate_conditions(
        MediaOptimizationInput(
            molasses_g_l=24,
            peptone_g_l=90,
            collagen_g_l=8,
            pH=7.25,
            aeration_vvm=1.0,
            rpm=260,
        )
    )

    assert productive["projection"]["collagenolytic_potential_index"] > limiting["projection"]["collagenolytic_potential_index"]
    assert productive["projection"]["biomass_potential_index"] > limiting["projection"]["biomass_potential_index"]
    assert productive["projection"]["confidence"] in {"medium", "high"}


def test_system_biology_api_contracts():
    client = TestClient(app)

    model_response = client.get("/api/system-biology-model")
    assert model_response.status_code == 200
    model_payload = model_response.json()
    assert model_payload["model_version"] == "system_biology_v1"
    assert model_payload["primary_accession"] == "GCF_001890705.1"
    assert model_payload["genome_report"]["direct_collagenase_evidence"]["found_direct_annotation"] is False

    evaluation_response = client.post(
        "/api/system-biology-model/evaluate",
        json={
            "molasses_g_l": 24,
            "peptone_g_l": 90,
            "collagen_g_l": 8,
            "mineral_factor": 1,
            "pH": 7.25,
            "aeration_vvm": 1,
            "rpm": 260,
            "cultivation_time_h": 144,
            "temperature_C": 25,
            "working_volume_l": 1.7,
        },
    )
    assert evaluation_response.status_code == 200
    evaluation_payload = evaluation_response.json()
    assert "collagenolytic_potential_index" in evaluation_payload["projection"]
    assert len(evaluation_payload["programs"]) >= 5
