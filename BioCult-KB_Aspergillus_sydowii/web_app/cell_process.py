from __future__ import annotations

from typing import Dict, List

from .schemas import (
    BiosynthesisPotentialPoint,
    CellProgramScore,
    CultivationOptimizationResult,
    MediaOptimizationInput,
    MediaOptimizationResult,
    OptimizationScenario,
    ProcessProjection,
    SystemBiologyModelResult,
)


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _score_to_percent(value: float) -> int:
    return round(_clamp(value) * 100)


def _status(score: float, low_threshold: float = 0.35, high_threshold: float = 0.72) -> str:
    if score < low_threshold:
        return "limiting"
    if score >= high_threshold:
        return "active"
    return "balanced"


def _program_scores(input_data: MediaOptimizationInput) -> List[CellProgramScore]:
    carbon = _clamp(input_data.molasses_g_l / 30)
    nitrogen = _clamp(input_data.peptone_g_l / 90)
    oxygen = _clamp((input_data.aeration_vvm * 0.55) + (input_data.rpm - 160) / 220)
    ph_fit = _clamp(1 - abs(input_data.pH - 7.25) / 0.7)
    collagen_induction = _clamp(input_data.collagen_g_l / 8)
    mineral_balance = _clamp(input_data.mineral_factor)
    stress = _clamp((input_data.molasses_g_l - 22) / 22 + (input_data.peptone_g_l - 85) / 140)
    viscosity_load = _clamp((nitrogen * 0.35) + (carbon * 0.25) + (collagen_induction * 0.28) + stress * 0.2)

    programs = [
        CellProgramScore(
            name="Углеродный поток и гликолиз",
            score=_score_to_percent(carbon * ph_fit),
            status=_status(carbon * ph_fit),
            rationale="Меласса задает доступный углерод; отклонение pH снижает эффективное включение в центральный метаболизм.",
        ),
        CellProgramScore(
            name="Азотный обмен и синтез секреторных белков",
            score=_score_to_percent(nitrogen * mineral_balance),
            status=_status(nitrogen * mineral_balance),
            rationale="Пептон поддерживает аминокислотный пул, минералы ограничивают ферментативные кофакторы и транспорт.",
        ),
        CellProgramScore(
            name="Индукция протеазно-коллагеназного ответа",
            score=_score_to_percent((collagen_induction * 0.55) + (nitrogen * 0.3) + (ph_fit * 0.15)),
            status=_status((collagen_induction * 0.55) + (nitrogen * 0.3) + (ph_fit * 0.15)),
            rationale="Коллагеновый субстрат и богатый азотный фон повышают вероятность включения секреторной программы.",
        ),
        CellProgramScore(
            name="Дыхание и энергетический баланс",
            score=_score_to_percent(oxygen * (0.7 + carbon * 0.3)),
            status=_status(oxygen * (0.7 + carbon * 0.3)),
            rationale="Рост углеродного потока повышает потребность в кислороде; rpm и vvm задают технологический резерв.",
        ),
        CellProgramScore(
            name="Морфология мицелия и вязкостная нагрузка",
            score=_score_to_percent(1 - viscosity_load * 0.58),
            status=_status(1 - viscosity_load * 0.58),
            rationale="Избыток органики и белкового субстрата повышает риск плотной мицелиальной фазы и ухудшения массопереноса.",
        ),
        CellProgramScore(
            name="Стресс и вторичный метаболизм",
            score=_score_to_percent(stress),
            status="watch" if stress >= 0.45 else "baseline",
            rationale="Высокая осмотическая и питательная нагрузка может смещать клетку от роста к стресс-ответам и вторичным метаболитам.",
        ),
    ]
    return programs


def evaluate_media_strategy(input_data: MediaOptimizationInput) -> MediaOptimizationResult:
    carbon = _clamp(input_data.molasses_g_l / 30)
    nitrogen = _clamp(input_data.peptone_g_l / 90)
    oxygen = _clamp((input_data.aeration_vvm * 0.55) + (input_data.rpm - 160) / 220)
    ph_fit = _clamp(1 - abs(input_data.pH - 7.25) / 0.7)
    collagen_induction = _clamp(input_data.collagen_g_l / 8)
    mineral_balance = _clamp(input_data.mineral_factor)
    time_fit = _clamp(1 - abs(input_data.cultivation_time_h - 132) / 108)
    temp_fit = _clamp(1 - abs(input_data.temperature_C - 25) / 6)
    cn_balance = _clamp(1 - abs((input_data.molasses_g_l / max(input_data.peptone_g_l, 1)) - 0.28) / 0.35)
    viscosity_pressure = _clamp((carbon * 0.24) + (nitrogen * 0.34) + (collagen_induction * 0.22) + max(0, input_data.molasses_g_l - 25) / 50)

    biomass_index = _score_to_percent((carbon * 0.32) + (nitrogen * 0.26) + (oxygen * 0.22) + (ph_fit * 0.12) + (mineral_balance * 0.08))
    enzyme_index = _score_to_percent((collagen_induction * 0.28) + (nitrogen * 0.2) + (oxygen * 0.16) + (ph_fit * 0.12) + (cn_balance * 0.1) + (time_fit * 0.08) + (temp_fit * 0.06))
    oxygen_demand = _score_to_percent((carbon * 0.38) + (biomass_index / 100 * 0.34) + (viscosity_pressure * 0.28))
    viscosity_risk = _score_to_percent(viscosity_pressure)

    predicted_biomass = 1.1 + biomass_index / 100 * 3.3
    volume_penalty = _clamp((input_data.working_volume_l - 1.7) / 6, 0, 0.25)
    predicted_activity = 18 + enzyme_index / 100 * 92
    predicted_activity *= 1 - volume_penalty
    predicted_po2 = 72 - oxygen_demand * 0.42 + oxygen * 18
    predicted_pco2 = 0.6 + oxygen_demand / 100 * 4.8
    predicted_viscosity = 1.1 + viscosity_pressure * 2.25
    harvest_time = 120 if enzyme_index >= 78 and viscosity_risk < 65 else 144
    yield_score = _clamp((enzyme_index / 100 * 0.58) + (max(0, predicted_po2) / 100 * 0.14) + ((100 - viscosity_risk) / 100 * 0.18) + (ph_fit * 0.1))

    recommendations: List[str] = []
    if input_data.molasses_g_l < 18:
        recommendations.append("Углеродный поток вероятно ограничен: проверить повышение мелассы до 20-25 г/л.")
    elif input_data.molasses_g_l > 30:
        recommendations.append("Меласса выше 30 г/л повышает осмотическую и кислородную нагрузку; нужен контроль pO2 и вязкости.")
    if input_data.peptone_g_l < 70:
        recommendations.append("Азотный пул может ограничивать секрецию белка; рассмотреть 80-90 г/л пептона.")
    if input_data.collagen_g_l < 2:
        recommendations.append("Слабый индукторный сигнал: для коллагеназного ответа нужен коллагеновый или близкий белковый субстрат.")
    if predicted_po2 < 30:
        recommendations.append("Прогноз pO2 низкий: увеличить aeration/rpm или снизить органическую нагрузку среды.")
    if viscosity_risk > 70:
        recommendations.append("Высокий риск вязкости: усилить мониторинг морфологии, KLA и давления, не повышать питательную нагрузку без DOE.")
    if ph_fit < 0.75:
        recommendations.append("pH смещен от 7.1-7.5; это ухудшает согласование клеточного и технологического уровней.")
    if not recommendations:
        recommendations.append("Сценарий сбалансирован: подтвердить через малый DOE по мелассе, пептону и аэрации.")

    genome_links: Dict[str, str] = {
        "genome_potential": "Аннотация генома задает список возможных ферментов, транспортеров и секреторных белков.",
        "condition_state": "Состав среды и датчики биореактора выбирают, какие клеточные программы вероятно активны.",
        "process_feedback": "pO2, pCO2, вязкость, pH и биомасса возвращаются как ограничения для следующей итерации среды.",
    }

    return MediaOptimizationResult(
        cell_programs=_program_scores(input_data),
        projection=ProcessProjection(
            biomass_index=biomass_index,
            collagenase_activity_index=enzyme_index,
            oxygen_demand_index=oxygen_demand,
            viscosity_risk_index=viscosity_risk,
            predicted_biomass_g_l=round(predicted_biomass, 2),
            predicted_collagenase_u_ml=round(predicted_activity, 1),
            predicted_pO2_percent=round(max(5, predicted_po2), 1),
            predicted_pCO2_percent=round(predicted_pco2, 1),
            predicted_viscosity_mpa_s=round(predicted_viscosity, 2),
            recommended_harvest_time_h=harvest_time,
            predicted_yield_score=round(yield_score * 100, 1),
        ),
        recommendations=recommendations,
        genome_process_links=genome_links,
    )


def _scenario_rationale(input_data: MediaOptimizationInput, result: MediaOptimizationResult) -> List[str]:
    rationale: List[str] = []
    projection = result.projection
    if projection.collagenase_activity_index >= 82:
        rationale.append("Высокий индекс коллагеназной активности за счет индуктора, азотного пула и кислородного резерва.")
    if projection.viscosity_risk_index <= 65:
        rationale.append("Риск вязкости остается в управляемой зоне для лабораторного биореактора.")
    if projection.predicted_pO2_percent >= 35:
        rationale.append("Прогноз pO2 оставляет резерв для аэробного метаболизма и секреции фермента.")
    if 7.1 <= input_data.pH <= 7.5:
        rationale.append("pH согласован с технологическим коридором 7.1-7.5.")
    if input_data.cultivation_time_h >= 120:
        rationale.append("Время культивирования попадает в продуктивное окно 120-144 ч.")
    return rationale or ["Сценарий выбран по суммарной целевой функции выхода коллагеназы."]


def optimize_cultivation_strategy() -> CultivationOptimizationResult:
    search_space = {
        "molasses_g_l": [18.0, 20.0, 24.0, 28.0, 32.0],
        "peptone_g_l": [75.0, 85.0, 95.0],
        "collagen_g_l": [3.0, 5.0, 8.0],
        "mineral_factor": [0.9, 1.0, 1.1],
        "pH": [7.1, 7.25, 7.4],
        "aeration_vvm": [0.7, 0.9, 1.1],
        "rpm": [220.0, 250.0, 280.0],
        "cultivation_time_h": [120.0, 144.0],
        "temperature_C": [24.5, 25.0, 25.5],
    }
    constraints = {
        "min_pO2_percent": 30.0,
        "max_viscosity_risk_index": 78.0,
        "max_pCO2_percent": 5.2,
        "working_volume_l": 1.7,
    }
    candidates: List[OptimizationScenario] = []
    rank = 1

    for molasses in search_space["molasses_g_l"]:
        for peptone in search_space["peptone_g_l"]:
            for collagen in search_space["collagen_g_l"]:
                for mineral in search_space["mineral_factor"]:
                    for pH in search_space["pH"]:
                        for aeration in search_space["aeration_vvm"]:
                            for rpm in search_space["rpm"]:
                                for time_h in search_space["cultivation_time_h"]:
                                    for temp in search_space["temperature_C"]:
                                        input_data = MediaOptimizationInput(
                                            molasses_g_l=molasses,
                                            peptone_g_l=peptone,
                                            collagen_g_l=collagen,
                                            mineral_factor=mineral,
                                            pH=pH,
                                            aeration_vvm=aeration,
                                            rpm=rpm,
                                            cultivation_time_h=time_h,
                                            temperature_C=temp,
                                            working_volume_l=constraints["working_volume_l"],
                                        )
                                        result = evaluate_media_strategy(input_data)
                                        projection = result.projection
                                        penalty = 0.0
                                        if projection.predicted_pO2_percent < constraints["min_pO2_percent"]:
                                            penalty += (constraints["min_pO2_percent"] - projection.predicted_pO2_percent) * 1.5
                                        if projection.viscosity_risk_index > constraints["max_viscosity_risk_index"]:
                                            penalty += (projection.viscosity_risk_index - constraints["max_viscosity_risk_index"]) * 1.1
                                        if projection.predicted_pCO2_percent > constraints["max_pCO2_percent"]:
                                            penalty += (projection.predicted_pCO2_percent - constraints["max_pCO2_percent"]) * 8
                                        objective = (
                                            projection.collagenase_activity_index * 1.35
                                            + (projection.predicted_yield_score or 0) * 0.75
                                            + projection.biomass_index * 0.18
                                            - projection.viscosity_risk_index * 0.35
                                            - projection.oxygen_demand_index * 0.12
                                            - penalty
                                        )
                                        candidates.append(
                                            OptimizationScenario(
                                                rank=rank,
                                                objective_score=round(objective, 2),
                                                input=input_data,
                                                projection=projection,
                                                rationale=_scenario_rationale(input_data, result),
                                            )
                                        )

    sorted_candidates = sorted(candidates, key=lambda item: item.objective_score, reverse=True)[:10]
    ranked = [
        OptimizationScenario(
            rank=index,
            objective_score=item.objective_score,
            input=item.input,
            projection=item.projection,
            rationale=item.rationale,
        )
        for index, item in enumerate(sorted_candidates, start=1)
    ]
    return CultivationOptimizationResult(
        best=ranked[0],
        scenarios=ranked,
        search_space=search_space,
        constraints=constraints,
    )


def build_system_biology_model() -> SystemBiologyModelResult:
    return SystemBiologyModelResult(
        model_layers={
            "genome": "Потенциал генов, секретируемых протеаз, транспортеров, центрального метаболизма и BGC-кластеров.",
            "transcriptome": "Condition-specific слой: RNA-seq ограничивает активные программы, но не заменяет metabolome.",
            "cell_program": "Углерод, азот, индукция протеаз, дыхание, морфология, стресс и вторичный метаболизм.",
            "bioreactor": "pO2, pCO2, pH, вязкость, KLA, температура, rpm и аэрация задают обратную связь.",
        },
        biosynthesis_potential=[
            BiosynthesisPotentialPoint(
                name="Коллагеназа / внеклеточные протеазы",
                potential_score=88,
                evidence_level="genome-supported / process-inducible",
                process_levers=["коллагеновый субстрат", "пептон 85-95 г/л", "pH 7.1-7.5", "pO2 > 35%"],
                risks=["вязкость мицелия", "кислородное ограничение", "избыточный стресс от органической нагрузки"],
            ),
            BiosynthesisPotentialPoint(
                name="Секреторный белковый аппарат",
                potential_score=81,
                evidence_level="inferred from fungal secretion biology",
                process_levers=["азотный пул", "температура 25 °C", "минеральный баланс", "продуктивное окно 120-144 ч"],
                risks=["дефицит аминокислот", "pH вне коридора", "пенообразование"],
            ),
            BiosynthesisPotentialPoint(
                name="Центральный углеродный поток",
                potential_score=76,
                evidence_level="medium-response model",
                process_levers=["меласса 20-28 г/л", "аэрация 0.9-1.1 vvm", "rpm 250-280"],
                risks=["осмотическая нагрузка при мелассе > 30 г/л", "pCO2 накопление"],
            ),
            BiosynthesisPotentialPoint(
                name="Вторичные метаболиты / BGC потенциал",
                potential_score=63,
                evidence_level="candidate metabolomics / requires validation",
                process_levers=["стресс-контроль", "co-culture references", "LC-MS validation"],
                risks=["candidate endpoints не равны raw evidence", "может конкурировать с ростом и секрецией фермента"],
            ),
        ],
        development_points=[
            "Скачать и индексировать все verified genome packages.",
            "Получить RunInfo по PRJNA542911, затем загрузить reads через SRA Toolkit или зафиксированные download_path.",
            "Собрать gene -> protein -> enzyme таблицу из GFF3/GBFF/protein FASTA.",
            "Сопоставить EC/KO/pathway и построить draft GEM.",
            "Использовать RNA-seq как condition-specific ограничения, а metabolomics только после provenance validation.",
            "Связать оптимизатор среды с DOE и фактическими измерениями KLA/активности коллагеназы.",
        ],
        integration_logic={
            "medium_to_cell": "Компоненты среды изменяют углеродный поток, азотный обмен, индукцию протеаз и стресс.",
            "cell_to_process": "Клеточная программа проявляется в биомассе, pO2/pCO2, вязкости, секреции фермента и окне сбора.",
            "process_to_medium": "Датчики биореактора возвращают ограничения для следующей итерации состава среды и режима.",
        },
    )
