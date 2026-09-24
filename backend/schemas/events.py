from datetime import datetime
from typing import Optional


from pydantic import BaseModel, ConfigDict


class EventCreate(BaseModel):

    # ========================================================
    # ÉVÉNEMENT
    # ========================================================

    event_date: datetime

    event_type: str

    organization_id: Optional[int] = None

    location: Optional[str] = None

    description: str

    # ========================================================
    # PERSONNE / VICTIME
    # ========================================================

    person_id: Optional[int] = None

    person_category: Optional[str] = None

    victim_last_name: Optional[str] = None

    victim_first_name: Optional[str] = None

    # ========================================================
    # LIGNE HIÉRARCHIQUE
    # ========================================================

    project_manager: Optional[str] = None

    site_supervisor: Optional[str] = None

    # ========================================================
    # CONSÉQUENCES HUMAINES
    # ========================================================

    lost_time: bool = False

    lost_days: int = 0

    modified_duty: bool = False

    modified_duty_days: int = 0

    fatal: bool = False

    permanent_injury: bool = False

    # ========================================================
    # CONSÉQUENCES MATÉRIELLES
    # ========================================================

    material_damage: bool = False

    material_damage_details: Optional[str] = None

    material_damage_cost: Optional[float] = None

    # ========================================================
    # CONSÉQUENCES ENVIRONNEMENTALES
    # ========================================================

    environmental_damage: bool = False

    environmental_damage_type: Optional[str] = None

    environmental_damage_details: Optional[str] = None

    environmental_quantity: Optional[float] = None

    environmental_unit: Optional[str] = None

# ============================================================
# MODIFICATION D'UN ÉVÉNEMENT
# ============================================================

class EventUpdate(BaseModel):

    # ========================================================
    # ÉVÉNEMENT
    # ========================================================

    event_date: Optional[datetime] = None
    event_type: Optional[str] = None

    organization_id: Optional[int] = None

    location: Optional[str] = None
    description: Optional[str] = None

    analysis_type: Optional[str] = None

    status: Optional[str] = None

    # ========================================================
    # PERSONNE / VICTIME
    # ========================================================

    person_id: Optional[int] = None
    person_category: Optional[str] = None

    victim_last_name: Optional[str] = None
    victim_first_name: Optional[str] = None

    # ========================================================
    # LIGNE HIÉRARCHIQUE
    # ========================================================

    project_manager: Optional[str] = None
    site_supervisor: Optional[str] = None

    # ========================================================
    # CONSÉQUENCES HUMAINES
    # ========================================================

    lost_time: Optional[bool] = None
    lost_days: Optional[int] = None

    modified_duty: Optional[bool] = None
    modified_duty_days: Optional[int] = None

    fatal: Optional[bool] = None
    permanent_injury: Optional[bool] = None

    # ========================================================
    # CONSÉQUENCES MATÉRIELLES
    # ========================================================

    material_damage: Optional[bool] = None
    material_damage_details: Optional[str] = None
    material_damage_cost: Optional[float] = None

    # ========================================================
    # CONSÉQUENCES ENVIRONNEMENTALES
    # ========================================================

    environmental_damage: Optional[bool] = None
    environmental_damage_type: Optional[str] = None
    environmental_damage_details: Optional[str] = None
    environmental_quantity: Optional[float] = None
    environmental_unit: Optional[str] = None    

class EventClassificationUpdate(BaseModel):
    deviation_code: Optional[str] = None
    material_agent_code: Optional[str] = None
    injury_nature_code: Optional[str] = None
    injury_location_code: Optional[str] = None


class EventClassificationResponse(BaseModel):
    id: int
    event_id: int

    deviation_code: Optional[str] = None
    deviation_label_snapshot: Optional[str] = None

    material_agent_code: Optional[str] = None
    material_agent_label_snapshot: Optional[str] = None

    injury_nature_code: Optional[str] = None
    injury_nature_label_snapshot: Optional[str] = None

    injury_location_code: Optional[str] = None
    injury_location_label_snapshot: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SeriousAccidentMatchedCriterion(BaseModel):
    group: str
    match_type: str
    code_from: str
    code_to: Optional[str] = None
    label: str


class EventClassificationUpdateResponse(BaseModel):
    classification: EventClassificationResponse
    serious_accident: bool
    very_serious_accident: bool
    circumstantial_report_required: bool
    immediate_notification_required: bool
    matched_criteria: list[SeriousAccidentMatchedCriterion]

class HeepoFactorResponse(BaseModel):
    id: int
    family: str
    code: str
    label: str
    label_nl: Optional[str] = None
    label_en: Optional[str] = None
    label_pl: Optional[str] = None
    active: bool

    model_config = ConfigDict(from_attributes=True)


class EventHeepoItem(BaseModel):
    family: str
    factor_id: Optional[int] = None
    other_text: Optional[str] = None
    is_na: bool = False


class EventHeepoUpdate(BaseModel):
    items: list[EventHeepoItem]


class EventHeepoFactorResponse(BaseModel):
    id: int
    event_id: int
    heepo_factor_id: Optional[int] = None
    family: str
    factor_code_snapshot: Optional[str] = None
    factor_label_snapshot: Optional[str] = None
    other_text: Optional[str] = None
    is_na: bool

    model_config = ConfigDict(from_attributes=True)


class EventHeepoResponse(BaseModel):
    event_id: int
    items: list[EventHeepoFactorResponse]

class HeepoFactorImportItem(BaseModel):
    family: str
    code: str
    label: str


class HeepoFactorImportPreview(BaseModel):
    source: Optional[str] = None
    source_version: Optional[str] = None
    items: list[HeepoFactorImportItem]

class SeriousAccidentCriterionImportItem(BaseModel):
    criterion_group: str
    match_type: str
    code_from: str
    code_to: Optional[str] = None
    label: str
    requires_multiple_lost_days: bool = False


class SeriousAccidentCriterionImportPreview(BaseModel):
    source: Optional[str] = None
    source_version: Optional[str] = None
    items: list[SeriousAccidentCriterionImportItem]

class EventFactsUpdate(BaseModel):
    client: Optional[str] = None
    worksite: Optional[str] = None
    project_manager: Optional[str] = None
    site_supervisor: Optional[str] = None
    team_leader: Optional[str] = None
    witnesses: Optional[str] = None

    usual_position: Optional[bool] = None
    temporary_worker: Optional[bool] = None
    resumed_same_day: Optional[bool] = None

    activity_before_event: Optional[str] = None
    event_description: Optional[str] = None
    direct_cause: Optional[str] = None

    caused_by_third_party: Optional[bool] = None
    third_party_details: Optional[str] = None
    police_report: Optional[bool] = None

    material_damage: Optional[bool] = None
    material_damage_details: Optional[str] = None
    environmental_damage: Optional[bool] = None
    environmental_damage_details: Optional[str] = None


class EventFactsResponse(EventFactsUpdate):
    id: int
    event_id: int

    model_config = ConfigDict(from_attributes=True)

class EventAnalysisTypeUpdate(BaseModel):
    analysis_type: str

# ============================================================
# RAPPORT CIRCONSTANCIÉ — ACCIDENT GRAVE
# ============================================================

class EventCircumstantialReportUpdate(BaseModel):
    victim_address: Optional[str] = None
    victim_birth_date: Optional[str] = None
    victim_company_seniority: Optional[str] = None
    victim_job_seniority: Optional[str] = None
    employer_name: Optional[str] = None
    employer_address: Optional[str] = None
    insurer_name: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    prevention_advisor: Optional[str] = None
    sipp_manager: Optional[str] = None
    sepp_name: Optional[str] = None
    sepp_contact: Optional[str] = None
    primary_material_factors: bool = False
    primary_collective_protection: bool = False
    primary_personal_protection: bool = False
    primary_environmental_factors: bool = False
    primary_other: bool = False
    primary_details: Optional[str] = None
    secondary_organization: bool = False
    secondary_communication: bool = False
    secondary_human_factors: bool = False
    secondary_other: bool = False
    secondary_details: Optional[str] = None
    tertiary_third_party_material: bool = False
    tertiary_incorrect_advice: bool = False
    tertiary_third_party_organization: bool = False
    tertiary_other: bool = False
    tertiary_details: Optional[str] = None
    report_contributors: Optional[str] = None
    report_recipients: Optional[str] = None
    committee_opinion: Optional[str] = None


class EventCircumstantialReportResponse(EventCircumstantialReportUpdate):
    id: int
    event_id: int
    model_config = ConfigDict(from_attributes=True)
