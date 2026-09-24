from datetime import datetime
from uuid import uuid4

import pytest

from backend import models
from backend.database import SessionLocal
from backend.services.cause_tree import (
    calculate_event_cause_levels,
    close_event_cause_branch,
    create_event_cause_fact,
    create_event_cause_fact_guided,
    create_event_cause_relation,
    delete_event_cause_fact,
    delete_event_cause_relation,
    set_event_cause_final_fact,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_event(db):
    event = models.Event(
        event_number=f"TEST-{uuid4()}",
        event_date=datetime.now(),
        event_type="ACCIDENT",
        analysis_type="NORMAL",
        description="Événement temporaire de test pytest",
        lost_time=False,
        lost_days=0,
        fatal=False,
        permanent_injury=False,
        status="OPEN",
    )

    db.add(event)
    db.flush()

    return event


# ============================================================
# HELPERS
# ============================================================

def create_fact(
    db,
    event_id: int,
    description: str,
):
    return create_event_cause_fact(
        db=db,
        event_id=event_id,
        description=description,
        sort_order=0,
    )


def create_final_fact(
    db,
    event_id: int,
    description: str = "Lésion finale",
):
    fact = create_fact(
        db=db,
        event_id=event_id,
        description=description,
    )

    final_fact, _ = set_event_cause_final_fact(
        db=db,
        event_id=event_id,
        fact_id=fact.id,
    )

    return final_fact


# ============================================================
# CREATION / STATUTS
# ============================================================

def test_new_fact_is_circumstance(
    db,
    test_event,
):
    fact = create_fact(
        db,
        test_event.id,
        "Condition temporaire",
    )

    assert fact.fact_type == "CIRCUMSTANCE"
    assert fact.is_terminal is False


def test_relation_promotes_source_to_cause(
    db,
    test_event,
):
    cause = create_fact(
        db,
        test_event.id,
        "Cause temporaire",
    )

    effect = create_fact(
        db,
        test_event.id,
        "Effet temporaire",
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=cause.id,
        effect_fact_id=effect.id,
    )

    assert cause.fact_type == "CAUSE"
    assert cause.is_terminal is False


# ============================================================
# SUPPRESSION / DEMOTION
# ============================================================

def test_last_outgoing_relation_removal_demotes_cause(
    db,
    test_event,
):
    cause = create_fact(
        db,
        test_event.id,
        "Cause avec deux effets",
    )

    effect_1 = create_fact(
        db,
        test_event.id,
        "Effet 1",
    )

    effect_2 = create_fact(
        db,
        test_event.id,
        "Effet 2",
    )

    relation_1 = create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=cause.id,
        effect_fact_id=effect_1.id,
    )

    relation_2 = create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=cause.id,
        effect_fact_id=effect_2.id,
    )

    assert cause.fact_type == "CAUSE"

    delete_event_cause_relation(
        db=db,
        event_id=test_event.id,
        relation_id=relation_1.id,
    )

    assert cause.fact_type == "CAUSE"

    delete_event_cause_relation(
        db=db,
        event_id=test_event.id,
        relation_id=relation_2.id,
    )

    assert cause.fact_type == "CIRCUMSTANCE"
    assert cause.is_terminal is False


def test_deleting_fact_recalculates_upstream_source(
    db,
    test_event,
):
    upstream = create_fact(
        db,
        test_event.id,
        "Cause amont",
    )

    middle = create_fact(
        db,
        test_event.id,
        "Cause intermédiaire",
    )

    effect = create_fact(
        db,
        test_event.id,
        "Effet",
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=upstream.id,
        effect_fact_id=middle.id,
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=middle.id,
        effect_fact_id=effect.id,
    )

    assert upstream.fact_type == "CAUSE"
    assert middle.fact_type == "CAUSE"

    delete_event_cause_fact(
        db=db,
        event_id=test_event.id,
        fact_id=middle.id,
    )

    assert upstream.fact_type == "CIRCUMSTANCE"
    assert upstream.is_terminal is False


# ============================================================
# GRAPH / CYCLES
# ============================================================

def test_cycle_is_refused(
    db,
    test_event,
):
    fact_a = create_fact(
        db,
        test_event.id,
        "Fait A",
    )

    fact_b = create_fact(
        db,
        test_event.id,
        "Fait B",
    )

    fact_c = create_fact(
        db,
        test_event.id,
        "Fait C",
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=fact_a.id,
        effect_fact_id=fact_b.id,
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=fact_b.id,
        effect_fact_id=fact_c.id,
    )

    with pytest.raises(ValueError):
        create_event_cause_relation(
            db=db,
            event_id=test_event.id,
            cause_fact_id=fact_c.id,
            effect_fact_id=fact_a.id,
        )


# ============================================================
# FINAL
# ============================================================

def test_only_one_final_fact_is_allowed(
    db,
    test_event,
):
    first = create_fact(
        db,
        test_event.id,
        "Première lésion",
    )

    second = create_fact(
        db,
        test_event.id,
        "Deuxième lésion",
    )

    set_event_cause_final_fact(
        db=db,
        event_id=test_event.id,
        fact_id=first.id,
    )

    assert first.fact_type == "FINAL"

    with pytest.raises(ValueError):
        set_event_cause_final_fact(
            db=db,
            event_id=test_event.id,
            fact_id=second.id,
        )


def test_fact_with_outgoing_relation_cannot_be_final(
    db,
    test_event,
):
    cause = create_fact(
        db,
        test_event.id,
        "Cause",
    )

    effect = create_fact(
        db,
        test_event.id,
        "Effet",
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=cause.id,
        effect_fact_id=effect.id,
    )

    with pytest.raises(ValueError):
        set_event_cause_final_fact(
            db=db,
            event_id=test_event.id,
            fact_id=cause.id,
        )


def test_final_fact_cannot_be_used_as_cause(
    db,
    test_event,
):
    final_fact = create_final_fact(
        db,
        test_event.id,
        "Électrisation",
    )

    other_fact = create_fact(
        db,
        test_event.id,
        "Autre fait",
    )

    with pytest.raises(ValueError):
        create_event_cause_relation(
            db=db,
            event_id=test_event.id,
            cause_fact_id=final_fact.id,
            effect_fact_id=other_fact.id,
        )


# ============================================================
# TERMINAL BRANCHES
# ============================================================

def test_only_cause_can_close_branch(
    db,
    test_event,
):
    circumstance = create_fact(
        db,
        test_event.id,
        "Circonstance isolée",
    )

    with pytest.raises(
        ValueError,
        match="Seule une cause peut terminer",
    ):
        close_event_cause_branch(
            db=db,
            event_id=test_event.id,
            fact_id=circumstance.id,
        )


def test_cause_without_upstream_can_close_branch(
    db,
    test_event,
):
    cause = create_fact(
        db,
        test_event.id,
        "Cause terminale",
    )

    effect = create_fact(
        db,
        test_event.id,
        "Effet",
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=cause.id,
        effect_fact_id=effect.id,
    )

    closed_fact, _ = close_event_cause_branch(
        db=db,
        event_id=test_event.id,
        fact_id=cause.id,
    )

    assert closed_fact.fact_type == "CAUSE"
    assert closed_fact.is_terminal is True


def test_cause_with_upstream_cannot_close_branch(
    db,
    test_event,
):
    upstream = create_fact(
        db,
        test_event.id,
        "Cause amont",
    )

    cause = create_fact(
        db,
        test_event.id,
        "Cause intermédiaire",
    )

    effect = create_fact(
        db,
        test_event.id,
        "Effet",
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=cause.id,
        effect_fact_id=effect.id,
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=upstream.id,
        effect_fact_id=cause.id,
    )

    with pytest.raises(
        ValueError,
        match="possède déjà au moins une cause en amont",
    ):
        close_event_cause_branch(
            db=db,
            event_id=test_event.id,
            fact_id=cause.id,
        )


def test_terminal_fact_resets_when_upstream_cause_is_added(
    db,
    test_event,
):
    terminal_cause = create_fact(
        db,
        test_event.id,
        "Cause terminale",
    )

    effect = create_fact(
        db,
        test_event.id,
        "Effet",
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=terminal_cause.id,
        effect_fact_id=effect.id,
    )

    close_event_cause_branch(
        db=db,
        event_id=test_event.id,
        fact_id=terminal_cause.id,
    )

    assert terminal_cause.is_terminal is True

    upstream = create_fact(
        db,
        test_event.id,
        "Nouvelle cause en amont",
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=upstream.id,
        effect_fact_id=terminal_cause.id,
    )

    assert terminal_cause.is_terminal is False


# ============================================================
# GUIDED CREATE
# ============================================================

def test_guided_create_with_single_target(
    db,
    test_event,
):
    effect = create_fact(
        db,
        test_event.id,
        "Effet cible",
    )

    fact, relations = create_event_cause_fact_guided(
        db=db,
        event_id=test_event.id,
        description="Cause guidée",
        sort_order=0,
        effect_fact_ids=[effect.id],
    )

    assert fact.fact_type == "CAUSE"
    assert len(relations) == 1

    assert relations[0].cause_fact_id == fact.id
    assert relations[0].effect_fact_id == effect.id


def test_guided_create_with_multiple_targets(
    db,
    test_event,
):
    effect_1 = create_fact(
        db,
        test_event.id,
        "Effet cible 1",
    )

    effect_2 = create_fact(
        db,
        test_event.id,
        "Effet cible 2",
    )

    fact, relations = create_event_cause_fact_guided(
        db=db,
        event_id=test_event.id,
        description="Cause multiple",
        sort_order=0,
        effect_fact_ids=[
            effect_1.id,
            effect_2.id,
        ],
    )

    assert fact.fact_type == "CAUSE"
    assert len(relations) == 2

    target_ids = {
        relation.effect_fact_id
        for relation in relations
    }

    assert target_ids == {
        effect_1.id,
        effect_2.id,
    }


# ============================================================
# LEVELS
# ============================================================

def test_levels_are_calculated_from_final_fact(
    db,
    test_event,
):
    final_fact = create_final_fact(
        db,
        test_event.id,
    )

    level_1 = create_fact(
        db,
        test_event.id,
        "Cause niveau 1",
    )

    level_2 = create_fact(
        db,
        test_event.id,
        "Cause niveau 2",
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=level_1.id,
        effect_fact_id=final_fact.id,
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=level_2.id,
        effect_fact_id=level_1.id,
    )

    levels = calculate_event_cause_levels(
        db=db,
        event_id=test_event.id,
    )

    assert levels[final_fact.id] == 0
    assert levels[level_1.id] == 1
    assert levels[level_2.id] == 2


def test_dag_uses_minimum_distance_to_final(
    db,
    test_event,
):
    final_fact = create_final_fact(
        db,
        test_event.id,
    )

    fact_a = create_fact(
        db,
        test_event.id,
        "Cause A",
    )

    fact_b = create_fact(
        db,
        test_event.id,
        "Cause B",
    )

    # --------------------------------------------------------
    # A ─────────────► FINAL
    # │
    # └────► B ──────► FINAL
    #
    # A possède deux chemins vers FINAL :
    # - longueur 1
    # - longueur 2
    #
    # Le niveau attendu de A est donc 1.
    # --------------------------------------------------------

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=fact_a.id,
        effect_fact_id=final_fact.id,
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=fact_a.id,
        effect_fact_id=fact_b.id,
    )

    create_event_cause_relation(
        db=db,
        event_id=test_event.id,
        cause_fact_id=fact_b.id,
        effect_fact_id=final_fact.id,
    )

    levels = calculate_event_cause_levels(
        db=db,
        event_id=test_event.id,
    )

    assert levels[final_fact.id] == 0
    assert levels[fact_b.id] == 1
    assert levels[fact_a.id] == 1