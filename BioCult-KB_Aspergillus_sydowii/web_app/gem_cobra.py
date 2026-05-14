from __future__ import annotations

from pathlib import Path
from typing import Any

from . import system_biology
from .schemas import GemFbaInput, MediaOptimizationInput


MODEL_ID = "aspergillus_sydowii_gem_lite_v1"
SBML_FILENAME = "aspergillus_sydowii_gem_lite_v1.xml"


def models_dir() -> Path:
    return Path(__file__).resolve().parent / "data" / "models"


def sbml_path() -> Path:
    return models_dir() / SBML_FILENAME


def cobra_dependency_status() -> dict[str, Any]:
    try:
        import cobra
        import libsbml
        import optlang
        import swiglpk  # noqa: F401

        return {
            "available": True,
            "cobra": cobra.__version__,
            "libsbml": libsbml.getLibSBMLDottedVersion(),
            "optlang": getattr(optlang, "__version__", "installed"),
            "solver": "glpk",
        }
    except Exception as exc:  # noqa: BLE001 - exposed as degraded-mode status.
        return {"available": False, "error": str(exc)}


def _import_cobra():
    import cobra
    from cobra import Metabolite, Model, Reaction

    return cobra, Model, Reaction, Metabolite


def _evidence_notes() -> dict[str, str]:
    report = system_biology.build_genome_report()
    notes: dict[str, str] = {}
    for category in report["categories"]:
        notes[category["name"]] = (
            f"{category['label']}: {category['match_count']} строк доказательств по ключевым словам; "
            f"{category['source_count']} источников; уверенность {category['confidence']}."
        )
    notes["collagenase_boundary"] = (
        "Прямая аннотация collagenase не найдена в GBFF/protein; реакция продукта является прокси коллагенолитического/протеазного пула."
    )
    return notes


def build_gem_lite_model():
    _, Model, Reaction, Metabolite = _import_cobra()
    model = Model(MODEL_ID)
    model.name = "Aspergillus sydowii GEM-lite v1"
    model.compartments = {"e": "extracellular", "c": "cytosol"}
    notes = _evidence_notes()
    model.notes = {
        "description": "GEM-lite proxy model for process decision support, not a curated genome-scale model.",
        "primary_accession": system_biology.PRIMARY_ACCESSION,
        **notes,
    }

    molasses_e = Metabolite("molasses_proxy_e", name="Molasses/glucose carbon proxy", compartment="e")
    molasses_c = Metabolite("molasses_proxy_c", name="Molasses/glucose carbon proxy", compartment="c")
    nitrogen_e = Metabolite("organic_nitrogen_proxy_e", name="Peptone organic nitrogen proxy", compartment="e")
    nitrogen_c = Metabolite("organic_nitrogen_proxy_c", name="Peptone organic nitrogen proxy", compartment="c")
    collagen_e = Metabolite("collagen_substrate_e", name="Collagen substrate proxy", compartment="e")
    collagen_c = Metabolite("collagen_substrate_c", name="Collagen substrate proxy", compartment="c")
    oxygen_e = Metabolite("o2_e", name="Oxygen", compartment="e")
    oxygen_c = Metabolite("o2_c", name="Oxygen", compartment="c")
    co2_c = Metabolite("co2_c", name="Carbon dioxide", compartment="c")
    co2_e = Metabolite("co2_e", name="Carbon dioxide", compartment="e")
    biomass_c = Metabolite("biomass_c", name="Biomass proxy", compartment="c")
    product_c = Metabolite("collagenolytic_product_c", name="Secreted protease/collagenolytic product proxy", compartment="c")
    product_e = Metabolite("collagenolytic_product_e", name="Secreted protease/collagenolytic product proxy", compartment="e")
    stress_c = Metabolite("secondary_metabolism_stress_c", name="Secondary metabolism/stress drain proxy", compartment="c")

    def reaction(rid: str, name: str, stoich: dict[Any, float], lower: float = 0.0, upper: float = 1000.0, note: str = ""):
        rxn = Reaction(rid)
        rxn.name = name
        rxn.lower_bound = lower
        rxn.upper_bound = upper
        rxn.add_metabolites(stoich)
        if note:
            rxn.notes = {"evidence": note}
        model.add_reactions([rxn])
        return rxn

    reaction("EX_molasses_proxy_e", "Molasses/glucose exchange", {molasses_e: -1}, -10, 1000, notes["carbon_redox_metabolism"])
    reaction("EX_organic_nitrogen_proxy_e", "Organic nitrogen exchange", {nitrogen_e: -1}, -10, 1000, notes["transport"])
    reaction("EX_collagen_substrate_e", "Collagen substrate exchange", {collagen_e: -1}, -2, 1000, notes["protease_peptidase"])
    reaction("EX_o2_e", "Oxygen exchange", {oxygen_e: -1}, -20, 1000, notes["carbon_redox_metabolism"])
    reaction("EX_co2_e", "Carbon dioxide exchange", {co2_e: -1}, 0, 1000)
    reaction("EX_collagenolytic_product_e", "Collagenolytic product exchange", {product_e: -1}, 0, 1000, notes["secretory_system"])

    reaction("T_molasses", "Carbon uptake transport", {molasses_e: -1, molasses_c: 1}, 0, 1000, notes["transport"])
    reaction("T_organic_nitrogen", "Organic nitrogen uptake transport", {nitrogen_e: -1, nitrogen_c: 1}, 0, 1000, notes["transport"])
    reaction("T_collagen", "Collagen substrate uptake/proteolysis proxy", {collagen_e: -1, collagen_c: 1}, 0, 1000, notes["protease_peptidase"])
    reaction("T_o2", "Oxygen uptake transport", {oxygen_e: -1, oxygen_c: 1}, 0, 1000)
    reaction("T_co2", "Carbon dioxide transport", {co2_c: -1, co2_e: 1}, 0, 1000)
    reaction("T_product", "Secreted product export", {product_c: -1, product_e: 1}, 0, 1000, notes["secretory_system"])

    biomass = reaction(
        "BIOMASS_ASYD",
        "Biomass synthesis proxy",
        {molasses_c: -1.0, nitrogen_c: -0.35, oxygen_c: -0.85, biomass_c: 1.0, co2_c: 0.45},
        0,
        1000,
        "Proxy biomass equation; coefficients are v1 assumptions pending curation.",
    )
    product = reaction(
        "PRODUCT_COLLAGENOLYTIC_POOL",
        "Secreted collagenolytic/protease product proxy",
        {molasses_c: -0.42, nitrogen_c: -0.45, collagen_c: -0.25, oxygen_c: -0.30, product_c: 1.0, co2_c: 0.20},
        0,
        1000,
        notes["protease_peptidase"],
    )
    reaction("DM_biomass_c", "Biomass demand", {biomass_c: -1}, 0, 1000, notes["cell_cycle"])
    reaction("ATPM_PROXY", "Maintenance/stress carbon and oxygen drain", {molasses_c: -0.18, oxygen_c: -0.08, co2_c: 0.10}, 0, 1000)
    reaction(
        "SECONDARY_METABOLISM_DRAIN",
        "Secondary metabolism/stress drain",
        {molasses_c: -0.22, nitrogen_c: -0.08, oxygen_c: -0.12, stress_c: 1.0, co2_c: 0.08},
        0,
        1000,
        notes["secondary_metabolism"],
    )
    reaction("DM_secondary_stress_c", "Secondary/stress demand", {stress_c: -1}, 0, 1000, notes["secondary_metabolism"])

    model.objective = model.reactions.DM_biomass_c
    model.reactions.ATPM_PROXY.lower_bound = 0.05
    biomass.annotation["sbo"] = "SBO:0000629"
    product.annotation["sbo"] = "SBO:0000176"
    return model


def export_sbml_model(force: bool = False) -> Path:
    cobra, _, _, _ = _import_cobra()
    path = sbml_path()
    if path.exists() and not force:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    model = build_gem_lite_model()
    cobra.io.write_sbml_model(model, str(path))
    return path


def load_sbml_model(force_rebuild: bool = False):
    cobra, _, _, _ = _import_cobra()
    path = export_sbml_model(force=force_rebuild)
    return cobra.io.read_sbml_model(str(path))


def _input_to_medium_bounds(input_data: MediaOptimizationInput) -> dict[str, float]:
    carbon_uptake = max(0.0, min(30.0, input_data.molasses_g_l * 0.45))
    nitrogen_uptake = max(0.0, min(22.0, input_data.peptone_g_l * 0.14))
    collagen_uptake = max(0.0, min(8.0, input_data.collagen_g_l * 0.45))
    oxygen_uptake = max(0.0, min(35.0, input_data.aeration_vvm * 9.0 + max(0.0, input_data.rpm - 120.0) / 22.0))
    return {
        "EX_molasses_proxy_e": -carbon_uptake,
        "EX_organic_nitrogen_proxy_e": -nitrogen_uptake,
        "EX_collagen_substrate_e": -collagen_uptake,
        "EX_o2_e": -oxygen_uptake,
    }


def _set_objective(model, objective: str, growth_floor: float = 0.05) -> None:
    biomass = model.reactions.DM_biomass_c
    product = model.reactions.EX_collagenolytic_product_e
    biomass.lower_bound = 0.0
    if objective == "collagenolytic_product":
        biomass.lower_bound = growth_floor
        model.objective = product
    elif objective == "balanced":
        model.objective = {biomass: 0.65, product: 0.35}
    else:
        model.objective = biomass


def run_fba(input_data: GemFbaInput) -> dict[str, Any]:
    dependency = cobra_dependency_status()
    if not dependency["available"]:
        return {
            "available": False,
            "status": "degraded",
            "objective": input_data.objective,
            "error": dependency.get("error", "COBRApy недоступна."),
        }

    try:
        model = load_sbml_model()
        medium_bounds = _input_to_medium_bounds(input_data.medium)
        for reaction_id, lower_bound in medium_bounds.items():
            model.reactions.get_by_id(reaction_id).lower_bound = lower_bound
        _set_objective(model, input_data.objective, growth_floor=input_data.growth_floor)
        solution = model.optimize()
        key_reactions = [
            "EX_molasses_proxy_e",
            "EX_organic_nitrogen_proxy_e",
            "EX_collagen_substrate_e",
            "EX_o2_e",
            "DM_biomass_c",
            "EX_collagenolytic_product_e",
            "ATPM_PROXY",
            "SECONDARY_METABOLISM_DRAIN",
        ]
        fluxes = {
            reaction_id: round(float(solution.fluxes.get(reaction_id, 0.0)), 6)
            for reaction_id in key_reactions
            if reaction_id in model.reactions
        }
        limiting = []
        for reaction_id, lower_bound in medium_bounds.items():
            flux = fluxes.get(reaction_id)
            if flux is not None and abs(flux - lower_bound) <= 1e-5 and abs(lower_bound) > 0:
                limiting.append(reaction_id)
        return {
            "available": True,
            "status": solution.status,
            "objective": input_data.objective,
            "objective_value": None if solution.objective_value is None else round(float(solution.objective_value), 6),
            "sbml_path": str(sbml_path()),
            "exchange_bounds": {key: abs(value) for key, value in medium_bounds.items()},
            "limiting_exchange_reactions": limiting,
            "fluxes": fluxes,
            "warnings": [
                "GEM-lite: прокси-стехиометрия и прокси-ограничения среды; это не кураторская полноразмерная GEM для Aspergillus.",
                "Поток продукта отражает секретируемый протеазный/коллагенолитический пул, а не доказанную реакцию одной коллагеназы.",
            ],
        }
    except Exception as exc:  # noqa: BLE001 - returned to API as explicit degraded mode.
        return {
            "available": False,
            "status": "degraded",
            "objective": input_data.objective,
            "error": str(exc),
            "warnings": ["Расчёт COBRA/SBML не выполнен; симуляция процесса должна перейти в ограниченный режим."],
        }


def gem_summary() -> dict[str, Any]:
    dependency = cobra_dependency_status()
    if not dependency["available"]:
        return {"available": False, "dependency": dependency, "status": "degraded"}
    try:
        path = export_sbml_model()
        model = load_sbml_model()
        return {
            "available": True,
            "status": "ready",
            "model_id": model.id,
            "sbml_path": str(path),
            "sbml_exists": path.exists(),
            "reaction_count": len(model.reactions),
            "metabolite_count": len(model.metabolites),
            "gene_count": len(model.genes),
            "objective": str(model.objective.expression),
            "dependency": dependency,
            "warnings": [
                "GEM-lite SBML is generated from project assumptions and NCBI evidence categories.",
                "No automated gap-filling or curated biomass equation is included in v1.",
            ],
        }
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "dependency": dependency, "status": "degraded", "error": str(exc)}
