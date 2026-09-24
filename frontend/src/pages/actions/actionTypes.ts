// ========================================================
// CODES MÉTIER
// ========================================================

export type ActionOriginType =
    | 'ACCIDENT'
    | 'INCIDENT'
    | 'NEAR_MISS'
    | 'ILT'
    | 'STOP'
    | 'CPPT'
    | 'PAA'
    | 'PGA'
    | 'QUALITY'
    | 'OTHER'

export type ActionScope =
    | 'LOCAL'
    | 'GLOBAL'

export type ActionType =
    | 'CORRECTIVE'
    | 'PREVENTIVE'

export type ActionPriority =
    | 'LOW'
    | 'MEDIUM'
    | 'HIGH'

export type ActionStatus =
    | 'TODO'
    | 'IN_PROGRESS'
    | 'DONE'
    | 'TO_VALIDATE'
    | 'CLOSED'

export type ActionProcessCode =
    | 'PR01'
    | 'PR02'
    | 'PR03'
    | 'PR04'
    | 'PR05'
    | 'PR06'
    | 'PR07'
    | 'PR08'


// ========================================================
// ACTION
// ========================================================

export type RiskyAction = {
    id: number

    origin_type: ActionOriginType
    event_id: number | null
    origin_reference: string | null

    description: string
    action_type: ActionType

    scope: ActionScope
    process_code: ActionProcessCode | null

    responsible_person_id: number | null
    responsible_text: string | null

    due_date: string | null

    priority: ActionPriority
    status: ActionStatus

    progress_percent: number | null

    resources: string | null
    follow_up_indicator: string | null

    created_by_person_id: number | null
    created_at: string | null
    updated_at: string | null
}


// ========================================================
// RÉPONSES API
// ========================================================

export type ActionListResponse = {
    actions: RiskyAction[]
}