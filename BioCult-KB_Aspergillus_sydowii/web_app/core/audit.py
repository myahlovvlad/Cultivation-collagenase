from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from .. import models
from ..schemas import AuditLogInput


def canonical_payload(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def record_payload(record: models.AuditRecord) -> dict[str, Any]:
    return {
        "timestamp": record.timestamp.isoformat() if record.timestamp else None,
        "user": record.user,
        "session_id": record.session_id,
        "batch_id": record.batch_id,
        "action_type": record.action_type,
        "module": record.module,
        "recommendation": record.recommendation,
        "evidence": json.loads(record.evidence_json or "{}"),
        "confidence": record.confidence,
        "decision": record.decision,
        "decision_reason": record.decision_reason,
        "outcome": json.loads(record.outcome_json or "{}") if record.outcome_json else None,
    }


def compute_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_payload(payload).encode("utf-8")).hexdigest()


def log_event(db: Session, input_data: AuditLogInput) -> models.AuditRecord:
    timestamp = datetime.now(timezone.utc).replace(tzinfo=None)
    payload = {
        "timestamp": timestamp.isoformat(),
        "user": input_data.user,
        "session_id": input_data.session_id,
        "batch_id": input_data.batch_id,
        "action_type": input_data.action_type,
        "module": input_data.module,
        "recommendation": input_data.recommendation,
        "evidence": input_data.evidence,
        "confidence": input_data.confidence,
        "decision": input_data.decision,
        "decision_reason": input_data.decision_reason,
        "outcome": input_data.outcome,
    }
    record = models.AuditRecord(
        timestamp=timestamp,
        user=input_data.user,
        session_id=input_data.session_id,
        batch_id=input_data.batch_id,
        action_type=input_data.action_type,
        module=input_data.module,
        recommendation=input_data.recommendation,
        evidence_json=json.dumps(input_data.evidence, ensure_ascii=False, sort_keys=True),
        confidence=input_data.confidence,
        decision=input_data.decision,
        decision_reason=input_data.decision_reason,
        outcome_json=json.dumps(input_data.outcome, ensure_ascii=False, sort_keys=True) if input_data.outcome is not None else None,
        record_hash=compute_hash(payload),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def verify_record(record: models.AuditRecord) -> dict[str, Any]:
    payload = record_payload(record)
    expected = compute_hash(payload)
    return {"record_id": record.id, "valid": expected == record.record_hash, "expected_hash": expected, "record_hash": record.record_hash}

