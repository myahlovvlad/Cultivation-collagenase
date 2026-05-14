from typing import Dict, List, Optional

from .models import Medium


def _extract_melassa_concentration(medium: Medium) -> Optional[float]:
    if not medium or not medium.components:
        return None
    for component in medium.components:
        if component.component and "melass" in component.component.lower():
            try:
                return float(component.concentration_g_l) if component.concentration_g_l is not None else None
            except (TypeError, ValueError):
                return None
    return None


def recommend(input_data: Dict, medium: Optional[Medium] = None) -> List[str]:
    recommendations = []
    last_pO2 = input_data.get("last_pO2_percent")
    controls_present = input_data.get("controls_present", True)
    collection_time = input_data.get("collection_time_h")

    if controls_present is False:
        recommendations.append("Если нет фоновых контролей, считать КЛА ориентировочной.")

    if last_pO2 is not None and last_pO2 < 25:
        recommendations.append(
            "Если pO₂ падает, проверить расход воздуха, rpm, пену, вязкость и морфологию."
        )

    if collection_time is not None:
        if abs(collection_time - 144.0) <= 24:
            recommendations.append(
                "При отсутствии критических отклонений рассматривать 144 ч как основную точку сбора культуральной жидкости."
            )
        elif collection_time < 120:
            recommendations.append("Рассмотреть дополнительные данные после 120 ч для подтверждения динамики ферментной активности.")

    if medium is not None:
        melassa_conc = _extract_melassa_concentration(medium)
        if melassa_conc is not None:
            if melassa_conc == 20:
                recommendations.append(
                    "Провести A/B-тест: 20 г/л мелассы + 85 г/л пептона против 30 г/л мелассы + 85 г/л пептона."
                )
            elif melassa_conc == 30:
                recommendations.append(
                    "Текущий оптимум: 30 г/л мелассы + 85 г/л пептона. Направьте внимание на стабильность KLA и биомассы."
                )

    if not recommendations:
        recommendations.append("Нет явных рекомендаций на основе переданных данных. Попробуйте добавить аналитику или параметры биореактора.")

    return recommendations
