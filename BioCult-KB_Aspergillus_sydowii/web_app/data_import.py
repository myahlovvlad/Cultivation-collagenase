from pathlib import Path
from typing import Any, Dict, Hashable, List, Mapping, Tuple

import pandas as pd

from . import models


def _normalize_column_name(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_")


def _normalize_row(row: Mapping[Hashable, Any]) -> Dict[str, Any]:
    return {_normalize_column_name(str(key)): value for key, value in row.items() if isinstance(key, str)}


def load_excel_table(file_path: Path) -> List[Dict[str, Any]]:
    df = pd.read_excel(file_path)
    return [_normalize_row(row) for row in df.to_dict(orient="records")]


def import_media_components(session, root_path: Path) -> Tuple[int, List[str]]:
    warnings: List[str] = []
    file_path = root_path / "02_media" / "media_component_dictionary.xlsx"
    if not file_path.exists():
        warnings.append(f"Файл не найден: {file_path}")
        return 0, warnings

    rows = load_excel_table(file_path)
    imported = 0
    for row in rows:
        medium_name = row.get("medium") or row.get("medium_name") or str(row.get("medium_id", "unknown"))
        if not medium_name:
            warnings.append("Пропущена строка без идентификатора среды.")
            continue

        medium = session.query(models.Medium).filter(models.Medium.name == str(medium_name)).first()
        if not medium:
            medium = models.Medium(name=str(medium_name), purpose="imported", status="imported")
            session.add(medium)
            session.flush()

        raw_concentration = row.get("concentration_g_l")
        if raw_concentration in (None, ""):
            concentration = None
        else:
            try:
                concentration = float(raw_concentration)
            except (TypeError, ValueError):
                concentration = None

        component_name = row.get("component") or row.get("component_name")
        if not component_name:
            warnings.append(f"Среда {medium.name}: компонент не задан.")
            continue

        component = models.MediumComponent(
            medium_id=medium.id,
            component=str(component_name),
            concentration_g_l=concentration,
            hydrate_form=row.get("hydrate_form", ""),
            role=row.get("role", ""),
        )
        session.add(component)
        imported += 1

    session.commit()
    return imported, warnings


def import_all_known_sources(session, root_path: Path) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    imported, warnings = import_media_components(session, root_path)
    results["media_components"] = imported
    results["warnings"] = warnings
    return results
