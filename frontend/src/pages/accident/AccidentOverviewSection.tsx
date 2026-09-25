import { at } from './accidentI18n'
import './AccidentOverviewSection.css'

import {
    useEffect,
    useState,
} from 'react'

import { API_BASE_URL } from './accidentApi'

import type {
    EventDetail,
    EventEditForm,
    OrganizationOption,
} from './accidentTypes'

type AccidentOverviewSectionProps = {
    event: EventDetail
    onEventUpdated: () => Promise<void>
}

function AccidentOverviewSection({
    event,
    onEventUpdated,
}: AccidentOverviewSectionProps) {
    const [eventEditing, setEventEditing] =
        useState(false)

    const [eventSaving, setEventSaving] =
        useState(false)

    const [eventSaveError, setEventSaveError] =
        useState<string | null>(null)

    const [eventDraft, setEventDraft] =
        useState<EventEditForm | null>(null)

    const [organizations, setOrganizations] =
        useState<OrganizationOption[]>([])

    const [circumstantialRequired, setCircumstantialRequired] =
        useState(false)

    useEffect(() => {
        const loadSeriousAssessment = async () => {
            try {
                const response = await fetch(
                    `${API_BASE_URL}/events/${event.id}/serious-accident-assessment`,
                )
                if (!response.ok) return
                const assessment = await response.json()
                setCircumstantialRequired(
                    Boolean(assessment.circumstantial_report_required),
                )
            } catch {
                setCircumstantialRequired(false)
            }
        }
        void loadSeriousAssessment()
    }, [event.id, event.analysis_type])

    useEffect(() => {
        const refreshSeriousAssessment = async (
            browserEvent: Event,
        ) => {
            const detail = (
                browserEvent as CustomEvent<{ eventId?: number }>
            ).detail

            if (detail?.eventId !== event.id) {
                return
            }

            try {
                const response = await fetch(
                    `${API_BASE_URL}/events/${event.id}/serious-accident-assessment`,
                )
                if (!response.ok) return
                const assessment = await response.json()
                setCircumstantialRequired(
                    Boolean(assessment.circumstantial_report_required),
                )
            } catch {
                setCircumstantialRequired(false)
            }
        }

        window.addEventListener(
            'risky:serious-accident-assessment-changed',
            refreshSeriousAssessment,
        )

        return () => {
            window.removeEventListener(
                'risky:serious-accident-assessment-changed',
                refreshSeriousAssessment,
            )
        }
    }, [event.id])

    useEffect(() => {
        const loadOrganizations = async () => {
            try {
                const response = await fetch(
                    `${API_BASE_URL}/organizations`,
                )

                if (!response.ok) {
                    return
                }

                const data: OrganizationOption[] =
                    await response.json()

                setOrganizations(
                    data.filter(
                        (organization) =>
                            organization.active,
                    ),
                )
            } catch {
                // Le dossier reste utilisable même si
                // le référentiel organisationnel ne charge pas.
            }
        }

        void loadOrganizations()
    }, [])

    const selectedOrganization =
        organizations.find(
            (organization) =>
                organization.id === event.organization?.id,
        )

    const selectedEntity =
        selectedOrganization?.type === 'TRADE'
            ? organizations.find(
                (organization) =>
                    organization.id ===
                    selectedOrganization.parent_id,
            )
            : selectedOrganization?.type === 'ENTITY'
                ? selectedOrganization
                : undefined

    const selectedTrade =
        selectedOrganization?.type === 'TRADE'
            ? selectedOrganization
            : undefined

    const entityOrganizations =
        organizations.filter(
            (organization) =>
                organization.type === 'ENTITY',
        )

    const selectedDraftOrganization =
        organizations.find(
            (organization) =>
                organization.id ===
                Number(eventDraft?.organization_id),
        )

    const draftEntityId =
        selectedDraftOrganization?.type === 'TRADE'
            ? selectedDraftOrganization.parent_id
            : selectedDraftOrganization?.type === 'ENTITY'
                ? selectedDraftOrganization.id
                : null

    const draftTradeId =
        selectedDraftOrganization?.type === 'TRADE'
            ? selectedDraftOrganization.id
            : null

    const availableTrades =
        organizations.filter(
            (organization) =>
                organization.type === 'TRADE' &&
                organization.parent_id === draftEntityId,
        )

    const startEventEditing = () => {
        setEventDraft({
            event_type: event.event_type,
            event_date: event.event_date.slice(0, 10),
            person_category: event.person_category ?? '',
            organization_id:
                event.organization?.id.toString() ?? '',
            victim_last_name:
                event.person?.last_name ??
                event.victim_last_name ??
                '',
            victim_first_name:
                event.person?.first_name ??
                event.victim_first_name ??
                '',
            location: event.location ?? '',
            project_manager: event.project_manager ?? '',
            site_supervisor: event.site_supervisor ?? '',
            material_damage: event.material_damage,
            material_damage_details:
                event.material_damage_details ?? '',
            material_damage_cost:
                event.material_damage_cost?.toString() ?? '',
            environmental_damage:
                event.environmental_damage,
            environmental_damage_type:
                event.environmental_damage_type ?? '',
            environmental_damage_details:
                event.environmental_damage_details ?? '',
            environmental_quantity:
                event.environmental_quantity?.toString() ?? '',
            environmental_unit:
                event.environmental_unit ?? '',
            lost_time: event.lost_time,
            lost_days: event.lost_days.toString(),
            modified_duty: event.modified_duty,
            modified_duty_days:
                event.modified_duty_days.toString(),
            permanent_injury: event.permanent_injury,
            fatal: event.fatal,
            analysis_type: event.analysis_type,
        })

        setEventSaveError(null)
        setEventEditing(true)
    }

    const cancelEventEditing = () => {
        setEventEditing(false)
        setEventDraft(null)
        setEventSaveError(null)
    }

    const updateEventField = <
        K extends keyof EventEditForm,
    >(
        field: K,
        value: EventEditForm[K],
    ) => {
        setEventDraft((current) => {
            if (!current) {
                return current
            }

            return {
                ...current,
                [field]: value,
            }
        })
    }

    const saveEvent = async () => {
        if (!eventDraft) {
            return
        }

        const token = sessionStorage.getItem(
            'risky_session_token',
        )

        if (!token) {
            setEventSaveError(
                'Session utilisateur introuvable.',
            )
            return
        }

        try {
            setEventSaving(true)
            setEventSaveError(null)

            const response = await fetch(
                `${API_BASE_URL}/events/${event.id}`,
                {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-Token': token,
                    },
                    body: JSON.stringify({
                        event_type: eventDraft.event_type,
                        event_date: eventDraft.event_date,
                        person_category:
                            eventDraft.person_category || null,
                        organization_id:
                            eventDraft.organization_id
                                ? Number(eventDraft.organization_id)
                                : null,
                        victim_last_name:
                            eventDraft.victim_last_name || null,
                        victim_first_name:
                            eventDraft.victim_first_name || null,
                        location:
                            eventDraft.location || null,
                        project_manager:
                            eventDraft.project_manager || null,
                        site_supervisor:
                            eventDraft.site_supervisor || null,
                        analysis_type:
                            eventDraft.analysis_type,

                        lost_time: eventDraft.lost_time,
                        lost_days: eventDraft.lost_time
                            ? Number(eventDraft.lost_days || 0)
                            : 0,

                        modified_duty:
                            eventDraft.modified_duty,
                        modified_duty_days:
                            eventDraft.modified_duty
                                ? Number(
                                    eventDraft.modified_duty_days || 0,
                                )
                                : 0,

                        permanent_injury:
                            eventDraft.permanent_injury,
                        fatal: eventDraft.fatal,

                        material_damage:
                            eventDraft.material_damage,
                        material_damage_details:
                            eventDraft.material_damage
                                ? eventDraft.material_damage_details || null
                                : null,
                        material_damage_cost:
                            eventDraft.material_damage &&
                                eventDraft.material_damage_cost !== ''
                                ? Number(eventDraft.material_damage_cost)
                                : null,

                        environmental_damage:
                            eventDraft.environmental_damage,
                        environmental_damage_type:
                            eventDraft.environmental_damage
                                ? eventDraft.environmental_damage_type || null
                                : null,
                        environmental_damage_details:
                            eventDraft.environmental_damage
                                ? eventDraft.environmental_damage_details || null
                                : null,
                        environmental_quantity:
                            eventDraft.environmental_damage &&
                                eventDraft.environmental_quantity !== ''
                                ? Number(eventDraft.environmental_quantity)
                                : null,
                        environmental_unit:
                            eventDraft.environmental_damage
                                ? eventDraft.environmental_unit || null
                                : null,
                    }),
                },
            )

            if (!response.ok) {
                const data = await response.json().catch(
                    () => null,
                )

                throw new Error(
                    data?.detail ||
                    at('overview.modifyError'),
                )
            }

            await onEventUpdated()

            setEventEditing(false)
            setEventDraft(null)
        } catch (error) {
            if (error instanceof Error) {
                setEventSaveError(error.message)
            } else {
                setEventSaveError(
                    at('classification.saveUnexpected'),
                )
            }
        } finally {
            setEventSaving(false)
        }
    }

    return (
        <>
            <div className="accident-dossier__top-edit-bar">
                {!eventEditing && (
                    <button
                        className="risky-button accident-dossier__edit-button"
                        type="button"
                        onClick={startEventEditing}
                    >
                        {at('common.edit')}
                    </button>
                )}
            </div>

            <div className="accident-dossier__top-grid">
                <section className="accident-dossier__section">
                    <h2>{at('overview.summary')}</h2>

                    {!eventEditing && (
                        <div className="accident-dossier__grid">
                            <div>
                                <span>{at('overview.type')}</span>
                                <strong>{event.event_type}</strong>
                            </div>

                            <div>
                                <span>{at('overview.date')}</span>
                                <strong>
                                    {new Date(
                                        event.event_date,
                                    ).toLocaleDateString('fr-BE')}
                                </strong>
                            </div>

                            <div>
                                <span>{at('overview.person')}</span>
                                <strong>
                                    {event.person
                                        ? `${event.person.first_name} ${event.person.last_name}`
                                        : event.victim_first_name ||
                                            event.victim_last_name
                                            ? `${event.victim_first_name ?? ''} ${event.victim_last_name ?? ''}`.trim()
                                            : at('common.notProvidedF')}
                                </strong>
                            </div>

                            <div>
                                <span>{at('overview.category')}</span>
                                <strong>
                                    {event.person_category ??
                                        at('common.notProvidedF')}
                                </strong>
                            </div>

                            <div>
                                <span>{at('overview.organization')}</span>
                                <strong>
                                    {selectedEntity?.name ??
                                        (selectedOrganization?.type !== 'TRADE'
                                            ? event.organization?.name
                                            : null) ??
                                        at('common.notProvidedF')}
                                </strong>
                            </div>

                            <div>
                                <span>Métier</span>
                                <strong>
                                    {selectedTrade?.name ?? '—'}
                                </strong>
                            </div>
                           <div>
                                <span>{at('overview.location')}</span>
                                <strong>
                                    {event.location ??
                                        at('common.notProvided')}
                                </strong>
                            </div>

                            <div>
                                <span>{at('overview.projectManager')}</span>
                                <strong>
                                    {event.project_manager ??
                                        at('common.notProvided')}
                                </strong>
                            </div>

                            <div>
                                <span>{at('create.siteSupervisor')}</span>
                                <strong>
                                    {event.site_supervisor ??
                                        at('common.notProvided')}
                                </strong>
                            </div>

                            <div>
                                <span>{at('overview.materialDamage')}</span>
                                <strong>
                                    {event.material_damage
                                        ? event.material_damage_details ||
                                        at('common.yesWithoutDescription')
                                        : at('common.no')}
                                </strong>
                            </div>

                            <div>
                                <span>{at('overview.environmentalDamage')}</span>
                                <strong>
                                    {event.environmental_damage
                                        ? event.environmental_damage_details ||
                                        at('common.yesWithoutDescription')
                                        : at('common.no')}
                                </strong>
                            </div>

                            <div>
                                <span>{at('overview.analysisType')}</span>
                                <strong>
                                    {circumstantialRequired
                                        ? at('circumstantial.analysisType')
                                        : event.analysis_type === 'ADVANCED'
                                            ? at('overview.inDepth')
                                            : at('overview.normal')}
                                </strong>
                            </div>
                        </div>
                    )}

            {eventEditing && eventDraft && (
                <div className="accident-dossier__facts-grid">
                    <label>
                        <span>{at('overview.type')}</span>
                        <select
                            value={eventDraft.event_type}
                            onChange={(e) =>
                                updateEventField(
                                    'event_type',
                                    e.target.value,
                                )
                            }
                        >
                            <option value="ACCIDENT">{at('common.eventType.accident')}</option>
                            <option value="INCIDENT">{at('common.eventType.incident')}</option>
                            <option value="NEAR_MISS">
                                {at('common.eventType.nearMiss')}
                            </option>
                            <option value="MATERIAL">{at('common.eventType.material')}</option>
                            <option value="ENVIRONMENT">
                                {at('common.eventType.environment')}
                            </option>
                        </select>
                    </label>

                    <label>
                        <span>{at('overview.date')}</span>
                        <input
                            type="date"
                            value={eventDraft.event_date}
                            onChange={(e) =>
                                updateEventField(
                                    'event_date',
                                    e.target.value,
                                )
                            }
                        />
                    </label>

                    <label>
                        <span>{at('create.firstName')}</span>
                        <input
                            value={eventDraft.victim_first_name}
                            onChange={(e) =>
                                updateEventField(
                                    'victim_first_name',
                                    e.target.value,
                                )
                            }
                        />
                    </label>

                    <label>
                        <span>{at('create.lastName')}</span>
                        <input
                            value={eventDraft.victim_last_name}
                            onChange={(e) =>
                                updateEventField(
                                    'victim_last_name',
                                    e.target.value,
                                )
                            }
                        />
                    </label>

                    <label>
                        <span>{at('overview.category')}</span>
                        <select
                            value={eventDraft.person_category}
                            onChange={(e) =>
                                updateEventField(
                                    'person_category',
                                    e.target.value,
                                )
                            }
                        >
                            <option value="">{at('common.notProvidedF')}</option>
                            <option value="WORKER">{at('common.category.worker')}</option>
                            <option value="EMPLOYEE">{at('common.category.employee')}</option>
                            <option value="TEMPORARY">{at('common.category.temp')}</option>
                            <option value="SUBCONTRACTOR">{at('common.category.contractor')}</option>
                            <option value="OTHER">{at('common.category.other')}</option>
                        </select>
                    </label>
                    <label>
                        <span>{at('overview.organization')}</span>

                        <select
                            value={draftEntityId ?? ''}
                            onChange={(e) => {
                                updateEventField(
                                    'organization_id',
                                    e.target.value,
                                )
                            }}
                        >
                            <option value="">
                                {at('common.notProvidedF')}
                            </option>

                            {entityOrganizations.map(
                                (organization) => (
                                    <option
                                        key={organization.id}
                                        value={organization.id}
                                    >
                                        {organization.name}
                                    </option>
                                ),
                            )}
                        </select>
                    </label>

                    <label>
                        <span>Métier</span>

                        <select
                            value={draftTradeId ?? ''}
                            disabled={!draftEntityId}
                            onChange={(e) => {
                                const tradeId = e.target.value

                                updateEventField(
                                    'organization_id',
                                    tradeId ||
                                    draftEntityId?.toString() ||
                                    '',
                                )
                            }}
                        >
                            <option value="">
                                — Transversal / non attribué —
                            </option>

                            {availableTrades.map(
                                (organization) => (
                                    <option
                                        key={organization.id}
                                        value={organization.id}
                                    >
                                        {organization.name}
                                    </option>
                                ),
                            )}
                        </select>
                    </label>
                    <label>
                        <span>{at('overview.location')}</span>
                        <input
                            value={eventDraft.location}
                            onChange={(e) =>
                                updateEventField(
                                    'location',
                                    e.target.value,
                                )
                            }
                        />
                    </label>

                    <label>
                        <span>{at('overview.projectManager')}</span>
                        <input
                            value={eventDraft.project_manager}
                            onChange={(e) =>
                                updateEventField(
                                    'project_manager',
                                    e.target.value,
                                )
                            }
                        />
                    </label>

                    <label>
                        <span>{at('create.siteSupervisor')}</span>
                        <input
                            value={eventDraft.site_supervisor}
                            onChange={(e) =>
                                updateEventField(
                                    'site_supervisor',
                                    e.target.value,
                                )
                            }
                        />
                    </label>

                    <label>
                        <span>{at('overview.materialDamage')}</span>
                        <select
                            value={
                                eventDraft.material_damage
                                    ? 'true'
                                    : 'false'
                            }
                            onChange={(e) =>
                                updateEventField(
                                    'material_damage',
                                    e.target.value === 'true',
                                )
                            }
                        >
                            <option value="false">{at('common.no')}</option>
                            <option value="true">{at('common.yes')}</option>
                        </select>
                    </label>

                    {eventDraft.material_damage && (
                        <label className="accident-dossier__facts-wide">
                            <span>
                                {at('overview.materialDetails')}
                            </span>
                            <textarea
                                rows={3}
                                value={eventDraft.material_damage_details}
                                onChange={(e) =>
                                    updateEventField(
                                        'material_damage_details',
                                        e.target.value,
                                    )
                                }
                            />
                        </label>
                    )}

                    <label>
                        <span>{at('overview.environmentalDamage')}</span>
                        <select
                            value={
                                eventDraft.environmental_damage
                                    ? 'true'
                                    : 'false'
                            }
                            onChange={(e) =>
                                updateEventField(
                                    'environmental_damage',
                                    e.target.value === 'true',
                                )
                            }
                        >
                            <option value="false">{at('common.no')}</option>
                            <option value="true">{at('common.yes')}</option>
                        </select>
                    </label>

                    {eventDraft.environmental_damage && (
                        <>
                            <label>
                                <span>Type d&apos;impact</span>
                                <select
                                    value={eventDraft.environmental_damage_type}
                                    onChange={(e) =>
                                        updateEventField(
                                            'environmental_damage_type',
                                            e.target.value,
                                        )
                                    }
                                >
                                    <option value="">{at('common.notProvided')}</option>
                                    <option value="SPILL">{at('create.spill')}</option>
                                    <option value="LEAK">{at('create.leak')}</option>
                                    <option value="RELEASE">{at('create.release')}</option>
                                    <option value="SOIL">Sol</option>
                                    <option value="WATER">Eau</option>
                                    <option value="AIR">Air</option>
                                    <option value="OTHER">{at('common.category.other')}</option>
                                </select>
                            </label>

                            <label className="accident-dossier__facts-wide">
                                <span>
                                    {at('overview.environmentalDetails')}
                                </span>
                                <textarea
                                    rows={3}
                                    value={eventDraft.environmental_damage_details}
                                    onChange={(e) =>
                                        updateEventField(
                                            'environmental_damage_details',
                                            e.target.value,
                                        )
                                    }
                                />
                            </label>
                        </>
                    )}

                    <label>
                        <span>{at('overview.analysisType')}</span>
                        <select
                            value={eventDraft.analysis_type}
                            disabled={circumstantialRequired}
                            onChange={(e) =>
                                updateEventField(
                                    'analysis_type',
                                    e.target.value,
                                )
                            }
                        >
                            <option value="NORMAL">{at('overview.normal')}</option>
                            <option value="ADVANCED">{at('overview.inDepth')}</option>
                        </select>
                    </label>
                </div>
            )}
        </section >

            <section className="accident-dossier__section">
                <h2>{at('overview.consequences')}</h2>

                {!eventEditing && (
                    <div className="accident-dossier__consequences">
                        <div>
                            <span>{at('create.lostTime')}</span>
                            <strong>
                                {event.lost_time
                                    ? at('overview.lostDaysValue', { count: event.lost_days ?? 0 })
                                    : at('common.no')}
                            </strong>
                        </div>

                        <div>
                            <span>{at('create.modifiedDuty')}</span>
                            <strong>
                                {event.modified_duty
                                    ? at('overview.modifiedDaysValue', { count: event.modified_duty_days ?? 0 })
                                    : at('common.no')}
                            </strong>
                        </div>

                        <div>
                            <span>{at('create.permanentInjury')}</span>
                            <strong>
                                {event.permanent_injury ? at('common.yes') : at('common.no')}
                            </strong>
                        </div>

                        <div>
                            <span>{at('create.death')}</span>
                            <strong>
                                {event.fatal ? at('common.yes') : at('common.no')}
                            </strong>
                        </div>

                        <div>
                            <span>{at('overview.materialCost')}</span>
                            <strong>
                                {event.material_damage
                                    ? event.material_damage_cost !== null
                                        ? event.material_damage_cost.toLocaleString(
                                            'fr-BE',
                                            {
                                                style: 'currency',
                                                currency: 'EUR',
                                            },
                                        )
                                        : at('common.notProvided')
                                    : 'Sans objet'}
                            </strong>
                        </div>
                    </div>
                )}

                {eventEditing && eventDraft && (
                    <div className="accident-dossier__facts-grid">
                        <label>
                            <span>{at('create.lostTime')}</span>
                            <select
                                value={eventDraft.lost_time ? 'true' : 'false'}
                                onChange={(e) =>
                                    updateEventField(
                                        'lost_time',
                                        e.target.value === 'true',
                                    )
                                }
                            >
                                <option value="false">{at('common.no')}</option>
                                <option value="true">{at('common.yes')}</option>
                            </select>
                        </label>

                        {eventDraft.lost_time && (
                            <label>
                                <span>{at('overview.lostDays')}</span>
                                <input
                                    type="number"
                                    min="0"
                                    value={eventDraft.lost_days}
                                    onChange={(e) =>
                                        updateEventField(
                                            'lost_days',
                                            e.target.value,
                                        )
                                    }
                                />
                            </label>
                        )}

                        <label>
                            <span>{at('create.modifiedDuty')}</span>
                            <select
                                value={eventDraft.modified_duty ? 'true' : 'false'}
                                onChange={(e) =>
                                    updateEventField(
                                        'modified_duty',
                                        e.target.value === 'true',
                                    )
                                }
                            >
                                <option value="false">{at('common.no')}</option>
                                <option value="true">{at('common.yes')}</option>
                            </select>
                        </label>

                        {eventDraft.modified_duty && (
                            <label>
                                <span>{at('overview.modifiedDays')}</span>
                                <input
                                    type="number"
                                    min="0"
                                    value={eventDraft.modified_duty_days}
                                    onChange={(e) =>
                                        updateEventField(
                                            'modified_duty_days',
                                            e.target.value,
                                        )
                                    }
                                />
                            </label>
                        )}

                        <label>
                            <span>{at('create.permanentInjury')}</span>
                            <select
                                value={eventDraft.permanent_injury ? 'true' : 'false'}
                                onChange={(e) =>
                                    updateEventField(
                                        'permanent_injury',
                                        e.target.value === 'true',
                                    )
                                }
                            >
                                <option value="false">{at('common.no')}</option>
                                <option value="true">{at('common.yes')}</option>
                            </select>
                        </label>

                        <label>
                            <span>{at('create.death')}</span>
                            <select
                                value={eventDraft.fatal ? 'true' : 'false'}
                                onChange={(e) =>
                                    updateEventField(
                                        'fatal',
                                        e.target.value === 'true',
                                    )
                                }
                            >
                                <option value="false">{at('common.no')}</option>
                                <option value="true">{at('common.yes')}</option>
                            </select>
                        </label>

                        {eventDraft.material_damage && (
                            <label>
                                <span>{at('overview.materialCost')}</span>
                                <input
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    value={eventDraft.material_damage_cost}
                                    onChange={(e) =>
                                        updateEventField(
                                            'material_damage_cost',
                                            e.target.value,
                                        )
                                    }
                                />
                            </label>
                        )}

                        {eventDraft.environmental_damage && (
                            <>
                                <label>
                                    <span>{at('overview.quantity')}</span>
                                    <input
                                        type="number"
                                        min="0"
                                        step="0.01"
                                        value={eventDraft.environmental_quantity}
                                        onChange={(e) =>
                                            updateEventField(
                                                'environmental_quantity',
                                                e.target.value,
                                            )
                                        }
                                    />
                                </label>

                                <label>
                                    <span>{at('overview.unit')}</span>
                                    <input
                                        value={eventDraft.environmental_unit}
                                        onChange={(e) =>
                                            updateEventField(
                                                'environmental_unit',
                                                e.target.value,
                                            )
                                        }
                                    />
                                </label>
                            </>
                        )}
                    </div>
                )}
            </section>
            </div >

        { eventEditing && (
            <>
                {eventSaveError && (
                    <p className="accident-dossier__facts-error">
                        {eventSaveError}
                    </p>
                )}

                <div className="accident-dossier__facts-actions">
                    <button
                        className="risky-button risky-button--cancel"
                        type="button"
                        onClick={cancelEventEditing}
                        disabled={eventSaving}
                    >
                        {at('common.cancel')}
                    </button>

                    <button
                        className="risky-button risky-button--confirm"
                        type="button"
                        onClick={saveEvent}
                        disabled={eventSaving}
                    >
                        {eventSaving
                            ? 'Enregistrement...'
                            : 'Enregistrer'}
                    </button>
                </div>
            </>
        )}

        </>
    )
}

export default AccidentOverviewSection

