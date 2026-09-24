import json
from typing import Any, Optional

from .. import models


def write_audit_log(
    db,
    session: dict,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    before_data: Optional[Any] = None,
    after_data: Optional[Any] = None,
    details: Optional[str] = None,
):
    audit_log = models.AuditLog(
        actor_person_id=session.get("person_id"),
        actor_initials=session.get("initials"),
        actor_name=session.get("display_name"),
        action=action,
        entity_type=entity_type,
        entity_id=(
            str(entity_id)
            if entity_id is not None
            else None
        ),
        before_data=(
            json.dumps(
                before_data,
                ensure_ascii=False,
                default=str,
            )
            if before_data is not None
            else None
        ),
        after_data=(
            json.dumps(
                after_data,
                ensure_ascii=False,
                default=str,
            )
            if after_data is not None
            else None
        ),
        details=details,
    )

    db.add(audit_log)

    return audit_log