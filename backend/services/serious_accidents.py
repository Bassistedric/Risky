from .. import models


def numeric_code_key(code: str) -> tuple[int, ...]:
    return tuple(
        int(part)
        for part in code.split(".")
    )


def code_matches(
    code: str | None,
    criterion: models.SeriousAccidentCriterion,
) -> bool:
    if code is None:
        return False

    try:
        code_key = numeric_code_key(code)
        from_key = numeric_code_key(criterion.code_from)

        if criterion.match_type == "EXACT":
            return code_key == from_key

        if criterion.match_type == "RANGE":
            if criterion.code_to is None:
                return False

            to_key = numeric_code_key(criterion.code_to)

            return from_key <= code_key <= to_key

    except ValueError:
        return False

    return False

def find_matching_criteria(
    db,
    criterion_group: str,
    code: str | None,
):
    if code is None:
        return []

    criteria = (
        db.query(models.SeriousAccidentCriterion)
        .filter(
            models.SeriousAccidentCriterion.criterion_group
            == criterion_group,
            models.SeriousAccidentCriterion.active.is_(True),
        )
        .all()
    )

    return [
        criterion
        for criterion in criteria
        if code_matches(code, criterion)
    ]

def evaluate_serious_accident(
    db,
    event: models.Event,
    classification: models.EventClassification | None,
):

    if event.fatal:
        return {
            "serious_accident": True,
            "very_serious_accident": True,
            "circumstantial_report_required": True,
            "immediate_notification_required": True,
            "matched_criteria": [
                {
                    "group": "CONSEQUENCE",
                    "match_type": "FATAL",
                    "code_from": "FATAL",
                    "code_to": None,
                    "label": "Accident mortel",
                }
         ],
        }
    
    if classification is None:
        return {
            "serious_accident": False,
            "very_serious_accident": False,
            "circumstantial_report_required": False,
            "immediate_notification_required": False,
            "matched_criteria": []
        }

    deviation_matches = find_matching_criteria(
        db,
        "DEVIATION_SERIOUS",
        classification.deviation_code,
    )

    material_agent_matches = find_matching_criteria(
        db,
        "MATERIAL_AGENT_SERIOUS",
        classification.material_agent_code,
    )

    injury_matches = find_matching_criteria(
        db,
        "INJURY_TEMPORARY_SERIOUS",
        classification.injury_nature_code,
    )

    valid_injury_matches = []

    for criterion in injury_matches:
        if criterion.requires_multiple_lost_days:
            if not event.lost_days or event.lost_days <= 1:
                continue

        valid_injury_matches.append(criterion)

    triggering_event = bool(
        deviation_matches or material_agent_matches
    )

    serious_consequence = bool(
        event.permanent_injury
        or valid_injury_matches
    )

    serious_accident = (
        triggering_event
        and serious_consequence
    )

    matched_criteria = []

    if event.permanent_injury and triggering_event:
        matched_criteria.append(
        {
            "group": "CONSEQUENCE",
            "match_type": "PERMANENT_INJURY",
            "code_from": "PERMANENT_INJURY",
            "code_to": None,
            "label": "Lésion permanente",
        }
    )

    for criterion in (
        deviation_matches
        + material_agent_matches
        + valid_injury_matches
    ):
        matched_criteria.append(
            {
                "group": criterion.criterion_group,
                "match_type": criterion.match_type,
                "code_from": criterion.code_from,
                "code_to": criterion.code_to,
                "label": criterion.label,
            }
        )

    very_serious_accident = bool(
        serious_accident
        and event.permanent_injury
    )

    return {
        "serious_accident": serious_accident,
        "very_serious_accident": very_serious_accident,
        "circumstantial_report_required": serious_accident,
        "immediate_notification_required": very_serious_accident,
        "matched_criteria": matched_criteria,
    }