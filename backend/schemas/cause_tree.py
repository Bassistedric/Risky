from pydantic import BaseModel, ConfigDict


class EventCauseFactCreate(BaseModel):
    description: str
    fact_type: str = "CIRCUMSTANCE"
    sort_order: int = 0

class EventCauseFactUpdate(BaseModel):
    description: str
    sort_order: int = 0

class EventCauseFactResponse(BaseModel):
    id: int
    event_id: int
    fact_type: str
    description: str
    sort_order: int
    is_terminal: bool

    model_config = ConfigDict(from_attributes=True)

class EventCauseRelationCreate(BaseModel):
    cause_fact_id: int
    effect_fact_id: int


class EventCauseRelationResponse(BaseModel):
    id: int
    event_id: int
    cause_fact_id: int
    effect_fact_id: int

    model_config = ConfigDict(from_attributes=True)

class EventCauseTreeResponse(BaseModel):
    event_id: int
    facts: list[EventCauseFactResponse]
    relations: list[EventCauseRelationResponse]

class EventCauseFactGuidedCreate(BaseModel):
    description: str
    sort_order: int = 0
    effect_fact_ids: list[int] = []

class EventCauseFactGuidedResponse(BaseModel):
    fact: EventCauseFactResponse
    relations: list[EventCauseRelationResponse]

class EventCauseFactLevelResponse(BaseModel):
    fact_id: int
    level: int


class EventCauseLevelsResponse(BaseModel):
    event_id: int
    levels: list[EventCauseFactLevelResponse]