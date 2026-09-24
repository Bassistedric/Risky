/* ========================================================
   RISKY — TYPES RAPPORT D'ANALYSE
   ======================================================== */

export type ReportEvent = {
    id: number
    event_number: string
    event_date: string
    event_type: string
    analysis_type: string | null
    status: string

    description: string | null
    location: string | null

    person_id: number | null
    person_name: string | null
    person_category: string | null

    organization_id: number | null
    organization_name: string | null

    project_manager: string | null
    site_supervisor: string | null

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
}


export type ReportFacts = {
    id: number
    event_id: number

    client: string | null
    worksite: string | null

    project_manager: string | null
    site_supervisor: string | null
    team_leader: string | null

    witnesses: string | null

    usual_position: boolean | null
    temporary_worker: boolean | null
    resumed_same_day: boolean | null

    activity_before_event: string | null
    event_description: string | null
    direct_cause: string | null

    caused_by_third_party: boolean | null
    third_party_details: string | null
    police_report: boolean | null

    material_damage: boolean | null
    material_damage_details: string | null

    environmental_damage: boolean | null
    environmental_damage_details: string | null
}


export type ReportClassification = {
    id: number
    event_id: number

    deviation_code: string | null
    deviation_label_snapshot: string | null
    deviation_label_fr: string | null
    deviation_label_nl: string | null
    deviation_label_en: string | null
    deviation_label_pl: string | null

    material_agent_code: string | null
    material_agent_label_snapshot: string | null
    material_agent_label_fr: string | null
    material_agent_label_nl: string | null
    material_agent_label_en: string | null
    material_agent_label_pl: string | null

    injury_nature_code: string | null
    injury_nature_label_snapshot: string | null
    injury_nature_label_fr: string | null
    injury_nature_label_nl: string | null
    injury_nature_label_en: string | null
    injury_nature_label_pl: string | null

    injury_location_code: string | null
    injury_location_label_snapshot: string | null
    injury_location_label_fr: string | null
    injury_location_label_nl: string | null
    injury_location_label_en: string | null
    injury_location_label_pl: string | null
}


export type ReportHeepoItem = {
    id: number
    family: string
    factor_code: string | null
    factor_label: string | null
    factor_label_fr: string | null
    factor_label_nl: string | null
    factor_label_en: string | null
    factor_label_pl: string | null
    other_text: string | null
    is_na: boolean
}


export type ReportPhoto = {
    id: number
    original_filename: string
    content_type: string
    file_size: number
    caption: string | null
    sort_order: number
}


export type ReportCauseFact = {
    id: number
    fact_type: string
    description: string
    sort_order: number
    is_terminal: boolean
    level: number | null
}


export type ReportCauseRelation = {
    id: number
    cause_fact_id: number
    effect_fact_id: number
}


export type ReportCauseTree = {
    facts: ReportCauseFact[]
    relations: ReportCauseRelation[]
}

export type ReportJustCultureStep = {
    step_order: number
    node_code: string

    question_text: string
    question_text_fr: string | null
    question_text_nl: string | null
    question_text_en: string | null
    question_text_pl: string | null

    answer_label: string
    answer_label_fr: string | null
    answer_label_nl: string | null
    answer_label_en: string | null
    answer_label_pl: string | null

    target_node_code: string
}


export type ReportJustCulture = {
    analysis_id: number
    status: string

    tree_code: string
    tree_version: string

    current_node_code: string | null

    conclusion_code: string | null
    conclusion_label: string | null
    conclusion_label_fr: string | null
    conclusion_label_nl: string | null
    conclusion_label_en: string | null
    conclusion_label_pl: string | null

    recommendation_code: string | null
    recommendation_label: string | null
    recommendation_label_fr: string | null
    recommendation_label_nl: string | null
    recommendation_label_en: string | null
    recommendation_label_pl: string | null

    validated: boolean
    validated_at: string | null
    validated_by_person_id: number | null

    history: ReportJustCultureStep[]
}



export type ReportAction = {
    id: number
    description: string
    action_type: string
    scope: string

    process_code: string | null

    responsible_person_id: number | null
    responsible_text: string | null

    due_date: string | null
    priority: string | null
    progress_percent: number | null

    resources: string | null
    follow_up_indicator: string | null
}


export type ReportSections = {
    facts: boolean
    classification: boolean
    photos: boolean
    heepo: boolean
    cause_tree: boolean
    just_culture: boolean
    actions: boolean
}


export type AccidentReportPreviewData = {
    event_id: number
    event_number: string

    event: ReportEvent
    facts: ReportFacts | null
    classification: ReportClassification | null

    heepo: ReportHeepoItem[]
    photos: ReportPhoto[]

    cause_tree: ReportCauseTree | null
    just_culture: ReportJustCulture | null

    actions: ReportAction[]

    sections: ReportSections
}