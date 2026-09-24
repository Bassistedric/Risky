from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ========================================================
# JUST CULTURE — IMPORT DE L'ARBRE
# ========================================================

class JustCultureTreeImportData(BaseModel):
    code: str
    name: str
    version: str
    language: str
    root_node_code: str

    description: Optional[str] = None

    # Traductions
    name_nl: Optional[str] = None
    name_en: Optional[str] = None
    name_pl: Optional[str] = None
    description_nl: Optional[str] = None
    description_en: Optional[str] = None
    description_en: Optional[str] = None

    # Références méthodologiques
    source_title: Optional[str] = None
    source_author: Optional[str] = None
    source_organization: Optional[str] = None
    source_reference: Optional[str] = None
    source_url: Optional[str] = None

    active: bool = True


class JustCultureNodeImportData(BaseModel):
    code: str
    text: str
    node_type: str

    # Traductions de la question / du texte
    text_nl: Optional[str] = None
    text_en: Optional[str] = None
    text_pl: Optional[str] = None

    # Conclusion
    conclusion_code: Optional[str] = None
    conclusion_label: Optional[str] = None
    conclusion_label_nl: Optional[str] = None
    conclusion_label_en: Optional[str] = None
    conclusion_label_pl: Optional[str] = None

    # Recommandation
    recommendation_code: Optional[str] = None
    recommendation_label: Optional[str] = None
    recommendation_label_nl: Optional[str] = None
    recommendation_label_en: Optional[str] = None
    recommendation_label_pl: Optional[str] = None

    active: bool = True


class JustCultureTransitionImportData(BaseModel):
    source: str

    # Compatibilité avec l'ancien JSON :
    # "answer" reste le libellé français.
    answer: str

    # Identifiant métier stable : YES / NO / ...
    answer_code: Optional[str] = None

    # Traductions du libellé
    answer_nl: Optional[str] = None
    answer_en: Optional[str] = None
    answer_pl: Optional[str] = None

    target: str
    sort_order: int = 0


class JustCultureTreeImportFile(BaseModel):
    tree: JustCultureTreeImportData
    nodes: list[JustCultureNodeImportData]
    transitions: list[JustCultureTransitionImportData]


# ========================================================
# JUST CULTURE — VALIDATION / APPLICATION IMPORT
# ========================================================

class JustCultureImportIssue(BaseModel):
    level: str
    code: str
    message: str


class JustCultureImportPreview(BaseModel):
    valid: bool

    tree_code: str
    tree_version: str
    root_node_code: str

    node_count: int
    question_count: int
    conclusion_count: int
    transition_count: int

    issues: list[JustCultureImportIssue]

    model_config = ConfigDict(from_attributes=True)


class JustCultureImportApplyResult(BaseModel):
    success: bool
    action: str

    tree_version_id: int
    tree_code: str
    tree_version: str

    nodes_created: int
    transitions_created: int

    message: str


# ========================================================
# JUST CULTURE — RÉPONSES DISPONIBLES
# ========================================================

class EventJustCultureAvailableAnswer(BaseModel):
    code: str

    label: str
    label_nl: Optional[str] = None
    label_en: Optional[str] = None
    label_pl: Optional[str] = None

    target_node_code: str
    sort_order: int


# ========================================================
# JUST CULTURE — DÉMARRAGE DE L'ANALYSE
# ========================================================

class EventJustCultureStartResponse(BaseModel):
    analysis_id: int
    event_id: int

    status: str

    tree_version_id: int
    tree_code: str
    tree_version: str

    current_node_code: str
    current_node_text: str
    current_node_text_nl: Optional[str] = None
    current_node_text_en: Optional[str] = None
    current_node_text_pl: Optional[str] = None
    current_node_type: str

    available_answers: list[EventJustCultureAvailableAnswer] = []


# ========================================================
# JUST CULTURE — RÉPONDRE À UNE QUESTION
# ========================================================

class EventJustCultureAnswerRequest(BaseModel):
    # Code métier stable : YES / NO / ...
    answer_code: str


class EventJustCultureAnswerResponse(BaseModel):
    analysis_id: int
    event_id: int
    status: str

    step_order: int

    answered_node_code: str

    question_text: str
    question_text_nl: Optional[str] = None
    question_text_en: Optional[str] = None
    question_text_pl: Optional[str] = None

    answer_code: str
    answer_label: str
    answer_label_nl: Optional[str] = None
    answer_label_en: Optional[str] = None
    answer_label_pl: Optional[str] = None

    current_node_code: Optional[str] = None
    current_node_text: Optional[str] = None
    current_node_text_nl: Optional[str] = None
    current_node_text_en: Optional[str] = None
    current_node_text_pl: Optional[str] = None
    current_node_type: Optional[str] = None

    available_answers: list[EventJustCultureAvailableAnswer] = []

    conclusion_code: Optional[str] = None
    conclusion_label: Optional[str] = None
    conclusion_label_nl: Optional[str] = None
    conclusion_label_en: Optional[str] = None
    conclusion_label_pl: Optional[str] = None

    recommendation_code: Optional[str] = None
    recommendation_label: Optional[str] = None
    recommendation_label_nl: Optional[str] = None
    recommendation_label_en: Optional[str] = None
    recommendation_label_pl: Optional[str] = None

# ========================================================
# JUST CULTURE — HISTORIQUE
# ========================================================

class EventJustCultureHistoryStep(BaseModel):
    step_order: int
    node_code: str

    # Snapshots historiques enregistrés lors de l'analyse
    question_text: str
    answer_label: str

    target_node_code: str

    question_text_nl: Optional[str] = None
    question_text_en: Optional[str] = None
    question_text_pl: Optional[str] = None

    answer_label_nl: Optional[str] = None
    answer_label_en: Optional[str] = None
    answer_label_pl: Optional[str] = None

# ========================================================
# JUST CULTURE — ÉTAT COMPLET DE L'ANALYSE
# ========================================================

class EventJustCultureDetailResponse(BaseModel):
    analysis_id: int
    event_id: int
    status: str

    tree_version_id: int
    tree_code: str
    tree_version: str

    current_node_code: Optional[str] = None
    current_node_text: Optional[str] = None
    current_node_text_nl: Optional[str] = None
    current_node_text_en: Optional[str] = None
    current_node_text_pl: Optional[str] = None
    current_node_type: Optional[str] = None

    available_answers: list[EventJustCultureAvailableAnswer] = []

    conclusion_code: Optional[str] = None
    conclusion_label: Optional[str] = None
    conclusion_label_nl: Optional[str] = None
    conclusion_label_en: Optional[str] = None
    conclusion_label_pl: Optional[str] = None

    recommendation_code: Optional[str] = None
    recommendation_label: Optional[str] = None
    recommendation_label_nl: Optional[str] = None
    recommendation_label_en: Optional[str] = None
    recommendation_label_pl: Optional[str] = None
    
    completed_at: Optional[datetime] = None

        # Validation finale
    validated: bool = False
    validated_at: Optional[datetime] = None
    validated_by_person_id: Optional[int] = None

    history: list[EventJustCultureHistoryStep]