export type EventPerson = {
    id: number
    employee_number: string | null
    last_name: string
    first_name: string
}

export type EventOrganization = {
    id: number
    name: string
}

export type EventDetail = {
    id: number
    event_number: string
    event_date: string
    event_type: string
    analysis_type: string
    person: EventPerson | null
    person_id: number | null
    person_category: string | null
    victim_last_name: string | null
    victim_first_name: string | null
    organization: EventOrganization | null
    project_manager: string | null
    site_supervisor: string | null
    location: string | null
    description: string | null
    lost_time: boolean
    lost_days: number
    modified_duty: boolean
    modified_duty_days: number
    fatal: boolean
    permanent_injury: boolean
    material_damage: boolean
    material_damage_details: string | null
    material_damage_cost: number | null
    environmental_damage: boolean
    environmental_damage_type: string | null
    environmental_damage_details: string | null
    environmental_quantity: number | null
    environmental_unit: string | null
    status: string
    created_at: string
}

export type EventEditForm = {
    event_type: string
    event_date: string
    person_category: string
    victim_last_name: string
    victim_first_name: string
    location: string
    project_manager: string
    site_supervisor: string
    material_damage: boolean
    material_damage_details: string
    material_damage_cost: string
    environmental_damage: boolean
    environmental_damage_type: string
    environmental_damage_details: string
    environmental_quantity: string
    environmental_unit: string
    lost_time: boolean
    lost_days: string
    modified_duty: boolean
    modified_duty_days: string
    permanent_injury: boolean
    fatal: boolean
    analysis_type: string
}

export type EventFacts = {
    id: number
    event_id: number
    client: string | null
    witnesses: string | null
    usual_position: boolean | null
    activity_before_event: string | null
    event_description: string | null
    direct_cause: string | null
    caused_by_third_party: boolean | null
    third_party_details: string | null
    police_report: boolean | null
}

export type EventFactsForm = {
    client: string
    witnesses: string
    usual_position: boolean | null
    activity_before_event: string
    event_description: string
    direct_cause: string
    caused_by_third_party: boolean | null
    third_party_details: string
    police_report: boolean | null
}

export const EMPTY_FACTS_FORM: EventFactsForm = {
    client: '',
    witnesses: '',
    usual_position: null,
    activity_before_event: '',
    event_description: '',
    direct_cause: '',
    caused_by_third_party: null,
    third_party_details: '',
    police_report: null,
}

export type EventCodeReference = {

    id: number

    code: string

    label: string

    label_nl: string | null

    label_en: string | null

    label_pl: string | null

}

export type EventClassification = {
    id: number
    event_id: number
    deviation_code: string | null
    deviation_label_snapshot: string | null
    material_agent_code: string | null
    material_agent_label_snapshot: string | null
    injury_nature_code: string | null
    injury_nature_label_snapshot: string | null
    injury_location_code: string | null
    injury_location_label_snapshot: string | null
}

export type ClassificationDraft = {
    deviation_code: string
    material_agent_code: string
    injury_nature_code: string
    injury_location_code: string
}

export type EventCodeReferenceResponse = {
    status: string
    category: string
    items: EventCodeReference[]
}

export type SeriousAccidentCriterion = {
    group: string
    match_type: string
    code_from: string
    code_to: string | null
    label: string
}

export type SeriousAccidentAssessment = {
    serious_accident: boolean
    very_serious_accident: boolean
    circumstantial_report_required: boolean
    immediate_notification_required: boolean
    matched_criteria: SeriousAccidentCriterion[]
}
