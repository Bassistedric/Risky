from typing import Optional
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# ============================================================
# RÔLES D'ACCÈS
# ============================================================

class AccessRole(Base):
    __tablename__ = "access_roles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


# ============================================================
# ATTRIBUTIONS D'ACCÈS
# ============================================================

class UserAccessGrant(Base):
    __tablename__ = "user_access_grants"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id"),
        nullable=False,
        index=True,
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("access_roles.id"),
        nullable=False,
        index=True,
    )

    organization_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )

    scope_all: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    include_children: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    person: Mapped["Person"] = relationship()
    role: Mapped["AccessRole"] = relationship()
    organization: Mapped[Optional["Organization"]] = relationship()


# ============================================================
# SESSIONS UTILISATEURS
# ============================================================

class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    person: Mapped["Person"] = relationship()
    
class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    entity_type: Mapped[str] = mapped_column(String(50))
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    parent: Mapped[Optional["Organization"]] = relationship(
        remote_side=[id],
        back_populates="children",
    )

    children: Mapped[list["Organization"]] = relationship(
        back_populates="parent",
    )

# ============================================================
# RÉFÉRENTIEL MÉTIERS
# ============================================================

class TradeReference(Base):
    __tablename__ = "trade_references"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


# ============================================================
# RATTACHEMENT ORGANISATION ↔ MÉTIER
# ============================================================

class OrganizationTrade(Base):
    __tablename__ = "organization_trades"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "trade_id",
            name="uq_organization_trade",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    trade_id: Mapped[int] = mapped_column(
        ForeignKey("trade_references.id"),
        nullable=False,
        index=True,
    )

    organization: Mapped["Organization"] = relationship()
    trade: Mapped["TradeReference"] = relationship()


# ============================================================
# HEURES PRESTÉES SÉCURITÉ
# ============================================================

class SafetyWorkHours(Base):
    __tablename__ = "safety_work_hours"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "year",
            "month",
            "dimension_key",
            name="uq_safety_work_hours_period_dimension",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    workforce_category: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    trade_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("trade_references.id"),
        nullable=True,
        index=True,
    )

    dimension_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    worked_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    source: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    organization: Mapped["Organization"] = relationship()
    trade: Mapped[Optional["TradeReference"]] = relationship()


# ============================================================
# OBJECTIFS SÉCURITÉ CFE
# ============================================================

class SafetyTarget(Base):
    __tablename__ = "safety_targets"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "year",
            name="uq_safety_target_organization_year",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    tf_target: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    tg_target: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    source: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    organization: Mapped["Organization"] = relationship()

# ============================================================
# INVALIDITÉS PERMANENTES — STATISTIQUES ANNUELLES
# ============================================================

class SafetyPermanentDisability(Base):
    __tablename__ = "safety_permanent_disabilities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    disability_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    conventional_days: Mapped[float] = mapped_column(
    Float,
    nullable=False,
    default=0,
)

    source: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    organization: Mapped["Organization"] = relationship()

class PersonCategory(Base):
    __tablename__ = "person_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Function(Base):
    __tablename__ = "functions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)

    employee_number: Mapped[Optional[str]] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=True,
    )
    initials: Mapped[Optional[str]] = mapped_column(
        String(10),
        unique=True,
        index=True,
        nullable=True,
    )

    last_name: Mapped[str] = mapped_column(String(100))
    first_name: Mapped[str] = mapped_column(String(100))

    email: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    function_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("functions.id"),
        nullable=True,
    )

    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("person_categories.id"),
        nullable=True,
    )

    organization_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=True,
    )

    # ========================================================
    # LIGNE HIÉRARCHIQUE
    # ========================================================

    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("people.id"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="ACTIVE",
    )

    archive_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )


    function: Mapped[Optional["Function"]] = relationship()

    category: Mapped[Optional["PersonCategory"]] = relationship()

    organization: Mapped[Optional["Organization"]] = relationship()

    manager: Mapped[Optional["Person"]] = relationship(
        remote_side=[id],
    )

class CompetencyCategory(Base):
    __tablename__ = "competency_categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150))

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


class Competency(Base):
    __tablename__ = "competencies"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150))

    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("competency_categories.id"),
        nullable=True,
    )
    validity_rule_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("validity_rules.id"),
        nullable=True,
    )

    validity_months: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )

    requires_expiry: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    category: Mapped[Optional["CompetencyCategory"]] = relationship()
    validity_rule: Mapped[Optional["ValidityRule"]] = relationship()

class PersonCompetency(Base):
    __tablename__ = "person_competencies"

    id: Mapped[int] = mapped_column(primary_key=True)

    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id"),
        nullable=False,
    )

    competency_id: Mapped[int] = mapped_column(
        ForeignKey("competencies.id"),
        nullable=False,
    )

    obtained_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    
    )

    provider: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    certificate_reference: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    document_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    validation_status: Mapped[str] = mapped_column(
        String(20),
        default="VALIDATED",
    )

    comment: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    person: Mapped["Person"] = relationship()

    competency: Mapped["Competency"] = relationship()

class ValidityRule(Base):
    __tablename__ = "validity_rules"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150))

    validity_months: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )

    validity_mode: Mapped[str] = mapped_column(
        String(30),
    )

    automatic_renewal: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

class AuthorizationCycle(Base):
    __tablename__ = "authorization_cycles"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150))

    start_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    end_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    automatic_renewal: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

class Authorization(Base):
    __tablename__ = "authorizations"

    id: Mapped[int] = mapped_column(primary_key=True)

    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id"),
        nullable=False,
    )

    cycle_id: Mapped[int] = mapped_column(
        ForeignKey("authorization_cycles.id"),
        nullable=False,
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="ACTIVE",
    )

    comment: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    person: Mapped["Person"] = relationship()

    cycle: Mapped["AuthorizationCycle"] = relationship()

    competencies: Mapped[list["AuthorizationCompetency"]] = relationship(
        back_populates="authorization",
        cascade="all, delete-orphan",
    )


class AuthorizationCompetency(Base):
    __tablename__ = "authorization_competencies"

    id: Mapped[int] = mapped_column(primary_key=True)

    authorization_id: Mapped[int] = mapped_column(
        ForeignKey("authorizations.id"),
        nullable=False,
    )

    competency_id: Mapped[int] = mapped_column(
        ForeignKey("competencies.id"),
        nullable=False,
    )

    authorization: Mapped["Authorization"] = relationship(
        back_populates="competencies",
    )

    competency: Mapped["Competency"] = relationship()

class PersonCompetencyStatusHistory(Base):
    __tablename__ = "person_competency_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    person_competency_id: Mapped[int] = mapped_column(
        ForeignKey("person_competencies.id"),
        nullable=False,
    )

    previous_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    person_competency: Mapped["PersonCompetency"] = relationship()

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    event_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    event_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    analysis_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="NORMAL",
    )

    person_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("people.id"),
        nullable=True,
    )
    # ========================================================
    # LIGNE HIÉRARCHIQUE
    # ========================================================

    project_manager: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    site_supervisor: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    # ========================================================
    # PERSONNE / VICTIME
    # ========================================================

    person_category: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )

    victim_last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    victim_first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    organization_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=True,
    )

    facts = relationship(
        "EventFacts",
        back_populates="event",
        uselist=False,
        cascade="all, delete-orphan",
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    lost_time: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    default=False,
    )

    lost_days: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    modified_duty: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    modified_duty_days: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    fatal: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    permanent_injury: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    # ========================================================
    # CONSÉQUENCES MATÉRIELLES
    # ========================================================

    material_damage: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    material_damage_details: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    material_damage_cost: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    # ========================================================
    # CONSÉQUENCES ENVIRONNEMENTALES
    # ========================================================

    environmental_damage: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    environmental_damage_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    environmental_damage_details: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    environmental_quantity: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    environmental_unit: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="OPEN",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    person: Mapped[Optional["Person"]] = relationship()

    organization: Mapped[Optional["Organization"]] = relationship()

    classification = relationship(
        "EventClassification",
        back_populates="event",
        uselist=False,
        cascade="all, delete-orphan",
    )

    heepo_factors = relationship(
        "EventHeepoFactor",
        back_populates="event",
        cascade="all, delete-orphan",
    )

class EventFacts(Base):
    __tablename__ = "event_facts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Contexte de l'accident
    client: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    worksite: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    project_manager: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    site_supervisor: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    team_leader: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    witnesses: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    # Situation de la victime
    usual_position: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    temporary_worker: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    resumed_same_day: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    # Relation des faits
    activity_before_event: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    event_description: Mapped[Optional[str]] = mapped_column(
        String(4000),
        nullable=True,
    )

    direct_cause: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    # Tiers / police
    caused_by_third_party: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    third_party_details: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    police_report: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    # Conséquences matérielles / environnementales
    material_damage: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    material_damage_details: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    environmental_damage: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    environmental_damage_details: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    event: Mapped["Event"] = relationship(
        back_populates="facts",
    )

class EventCodeReference(Base):
    __tablename__ = "event_code_references"

    id: Mapped[int] = mapped_column(primary_key=True)

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

        # Libellé français historique
    label: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    # Traductions
    label_nl: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    label_en: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    label_pl: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    source_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    imported_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

class EventClassification(Base):
    __tablename__ = "event_classifications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    deviation_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    deviation_label_snapshot: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    material_agent_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    material_agent_label_snapshot: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    injury_nature_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    injury_nature_label_snapshot: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    injury_location_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    injury_location_label_snapshot: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="classification",
    )

class HeepoFactor(Base):
    __tablename__ = "heepo_factors"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    family: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Libellé français historique
    label: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # Traductions
    label_nl: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    label_en: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )
    label_pl: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )


class EventHeepoFactor(Base): 
    __tablename__ = "event_heepo_factors"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )

    heepo_factor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("heepo_factors.id"),
        nullable=True,
    )

    family: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    factor_code_snapshot: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    factor_label_snapshot: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    other_text: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    is_na: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="heepo_factors",
    )

    factor: Mapped[Optional["HeepoFactor"]] = relationship()

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        index=True,
    )

    actor_person_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("people.id"),
        nullable=True,
        index=True,
    )

    actor_initials: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )

    actor_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    entity_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    before_data: Mapped[Optional[str]] = mapped_column(
        nullable=True,
    )

    after_data: Mapped[Optional[str]] = mapped_column(
        nullable=True,
    )

    details: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    actor: Mapped[Optional["Person"]] = relationship()

class SeriousAccidentRule(Base):
    __tablename__ = "serious_accident_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    deviation_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    material_agent_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    injury_nature_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

class SeriousAccidentCriterion(Base):
    __tablename__ = "serious_accident_criteria"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    criterion_group: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    match_type: Mapped[str] = mapped_column(
    String(20),
    nullable=False,
    )

    code_from: Mapped[str] = mapped_column(
    String(50),
    nullable=False,
    )

    code_to: Mapped[Optional[str]] = mapped_column(
    String(50),
    nullable=True,
    )

    requires_multiple_lost_days: Mapped[bool] = mapped_column(
    nullable=False,
    default=False,
    )

    label: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

# ========================================================
# RAPPORT CIRCONSTANCIÉ — DONNÉES COMPLÉMENTAIRES
# ========================================================

class EventCircumstantialReport(Base):
    __tablename__ = "event_circumstantial_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"), nullable=False, unique=True, index=True
    )

    victim_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    victim_birth_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    victim_company_seniority: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    victim_job_seniority: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    employer_name: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    employer_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    insurer_name: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    insurance_policy_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prevention_advisor: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    sipp_manager: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    sepp_name: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    sepp_contact: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    primary_material_factors: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    primary_collective_protection: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    primary_personal_protection: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    primary_environmental_factors: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    primary_other: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cause_selections_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    secondary_organization: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    secondary_communication: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    secondary_human_factors: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    secondary_other: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    secondary_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tertiary_third_party_material: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tertiary_incorrect_advice: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tertiary_third_party_organization: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tertiary_other: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tertiary_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    report_contributors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_recipients: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    committee_opinion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


# ========================================================
# JUST CULTURE — VERSION DE L'ARBRE
# ========================================================

class JustCultureTreeVersion(Base):
    __tablename__ = "just_culture_tree_versions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="FR",
    )

    root_node_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # Présentation de la méthode utilisée
    description: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    # Traductions
    name_nl: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    name_en: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    description_nl: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    description_en: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    # Référence méthodologique / bibliographique
    source_title: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    source_author: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    source_organization: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    source_reference: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    source_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )


# ========================================================
# JUST CULTURE — NŒUDS
# ========================================================
    
class JustCultureNode(Base):
    __tablename__ = "just_culture_nodes"
    __table_args__ = (
        UniqueConstraint(
            "tree_version_id",
            "code",
            name="uq_just_culture_node_version_code",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    tree_version_id: Mapped[int] = mapped_column(
        ForeignKey("just_culture_tree_versions.id"),
        nullable=False,
        index=True,
    )

    # Identifiant fonctionnel stable provenant de l'arbre source
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Texte affiché à l'utilisateur
    text: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    # Traductions du texte affiché
    text_nl: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    text_en: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )
    text_pl: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )
    # QUESTION ou CONCLUSION
    node_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="QUESTION",
    )

    # Conclusion comportementale éventuelle :
    # NEGLIGENCE, ERREUR_INATTENTION, SABOTAGE, etc.
    conclusion_code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Libellé lisible de la conclusion
    conclusion_label: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    conclusion_label_nl: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    conclusion_label_en: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    conclusion_label_pl: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )   
    

    # Recommandation associée :
    # ACCOMPAGNEMENT, AVERTISSEMENT_VERBAL, etc.
    recommendation_code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    recommendation_label: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    recommendation_label_nl: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    recommendation_label_en: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    recommendation_label_pl: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )    

    active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )


class JustCultureTransition(Base):
    __tablename__ = "just_culture_transitions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    source_node_id: Mapped[int] = mapped_column(
        ForeignKey("just_culture_nodes.id"),
        nullable=False,
        index=True,
    )

        # Identifiant logique stable de la réponse :
    # YES / NO / autre valeur métier éventuelle
    answer_code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Libellé français historique
    answer_label: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    answer_label_nl: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )

    answer_label_en: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )
    answer_label_pl: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True,
    )    

    answer_label: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    target_node_id: Mapped[int] = mapped_column(
        ForeignKey("just_culture_nodes.id"),
        nullable=False,
        index=True,
    )

    sort_order: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

class EventJustCultureAnalysis(Base):
    __tablename__ = "event_just_culture_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    tree_version_id: Mapped[int] = mapped_column(
        ForeignKey("just_culture_tree_versions.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="IN_PROGRESS",
    )

    current_node_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    conclusion_code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    conclusion_label: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    recommendation_code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    recommendation_label: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # ========================================================
    # VALIDATION DE L'ANALYSE
    # ========================================================

    validated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    validated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    validated_by_person_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("people.id"),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

class EventJustCultureAnswer(Base):
    __tablename__ = "event_just_culture_answers"

    __table_args__ = (
        UniqueConstraint(
            "analysis_id",
            "step_order",
            name="uq_event_just_culture_answer_step",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("event_just_culture_analyses.id"),
        nullable=False,
        index=True,
    )

    step_order: Mapped[int] = mapped_column(
        nullable=False,
    )

    node_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    question_text: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    answer_label: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    target_node_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

class EventCauseFact(Base):
    __tablename__ = "event_cause_facts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )

    fact_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="CIRCUMSTANCE",
    )

    description: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    sort_order: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    is_terminal: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

class EventCauseRelation(Base):
    __tablename__ = "event_cause_relations"

    __table_args__ = (
        UniqueConstraint(
            "cause_fact_id",
            "effect_fact_id",
            name="uq_event_cause_relation",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )

    cause_fact_id: Mapped[int] = mapped_column(
        ForeignKey("event_cause_facts.id"),
        nullable=False,
        index=True,
    )

    effect_fact_id: Mapped[int] = mapped_column(
        ForeignKey("event_cause_facts.id"),
        nullable=False,
        index=True,
    )