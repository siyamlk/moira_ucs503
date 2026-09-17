from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def record_audit(
    db: Session,
    admin_id: int,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    details: dict | None = None,
) -> None:
    """Adds an AuditLog row to the session. Does not commit — the caller's
    existing db.commit() for the mutation covers this too, so a failed
    commit never leaves an orphaned audit entry for a change that didn't
    actually happen."""
    db.add(
        AuditLog(
            admin_id=admin_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
    )
