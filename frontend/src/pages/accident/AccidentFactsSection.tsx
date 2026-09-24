import { at } from './accidentI18n'
import './AccidentFactsSection.css'

import { useState } from 'react'

import { API_BASE_URL } from './accidentApi'
import {
    EMPTY_FACTS_FORM,
} from './accidentTypes'
import type {
    EventFacts,
    EventFactsForm,
} from './accidentTypes'

type AccidentFactsSectionProps = {
    eventId: number
}

function AccidentFactsSection({
    eventId,
}: AccidentFactsSectionProps) {
    const [factsOpen, setFactsOpen] =
        useState(false)

    const [facts, setFacts] =
        useState<EventFacts | null>(null)

    const [factsLoading, setFactsLoading] =
        useState(false)

    const [factsError, setFactsError] =
        useState<string | null>(null)

    const [factsEditing, setFactsEditing] =
        useState(false)

    const [factsSaving, setFactsSaving] =
        useState(false)

    const [factsSaveError, setFactsSaveError] =
        useState<string | null>(null)

    const [factsDraft, setFactsDraft] =
        useState<EventFactsForm>({
            ...EMPTY_FACTS_FORM,
        })

    const toggleFacts = async () => {
        if (factsOpen) {
            setFactsOpen(false)
            return
        }

        setFactsOpen(true)

        if (facts !== null) {
            return
        }

        try {
            setFactsLoading(true)
            setFactsError(null)

            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}/facts`,
            )

            if (response.status === 404) {
                setFacts(null)
                return
            }

            if (!response.ok) {
                throw new Error(
                    'Impossible de charger la relation des faits.',
                )
            }

            const data: EventFacts =
                await response.json()

            setFacts(data)
        } catch (error) {
            if (error instanceof Error) {
                setFactsError(error.message)
            } else {
                setFactsError(
                    'Une erreur est survenue.',
                )
            }
        } finally {
            setFactsLoading(false)
        }
    }

    const startFactsEditing = () => {
        if (facts) {
            setFactsDraft({
                client: facts.client ?? '',
                witnesses: facts.witnesses ?? '',
                usual_position: facts.usual_position,
                activity_before_event:
                    facts.activity_before_event ?? '',
                event_description:
                    facts.event_description ?? '',
                direct_cause:
                    facts.direct_cause ?? '',
                caused_by_third_party:
                    facts.caused_by_third_party,
                third_party_details:
                    facts.third_party_details ?? '',
                police_report:
                    facts.police_report,
            })
        } else {
            setFactsDraft({
                ...EMPTY_FACTS_FORM,
            })
        }

        setFactsSaveError(null)
        setFactsEditing(true)
    }

    const cancelFactsEditing = () => {
        setFactsEditing(false)
        setFactsSaveError(null)
    }

    const updateFactsField = <
        K extends keyof EventFactsForm,
    >(
        field: K,
        value: EventFactsForm[K],
    ) => {
        setFactsDraft((current) => ({
            ...current,
            [field]: value,
        }))
    }

    const boolSelectValue = (
        value: boolean | null,
    ) => {
        if (value === true) {
            return 'true'
        }

        if (value === false) {
            return 'false'
        }

        return ''
    }

    const selectValueToBool = (
        value: string,
    ): boolean | null => {
        if (value === 'true') {
            return true
        }

        if (value === 'false') {
            return false
        }

        return null
    }

    const saveFacts = async () => {
        const token = sessionStorage.getItem(
            'risky_session_token',
        )

        if (!token) {
            setFactsSaveError(
                'Session utilisateur introuvable.',
            )
            return
        }

        try {
            setFactsSaving(true)
            setFactsSaveError(null)

            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}/facts`,
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-Token': token,
                    },
                    body: JSON.stringify({
                        ...factsDraft,
                        third_party_details:
                            factsDraft.caused_by_third_party
                                ? factsDraft.third_party_details
                                : null,
                    }),
                },
            )

            if (!response.ok) {
                throw new Error(
                    'Impossible d’enregistrer la relation des faits.',
                )
            }

            const data: EventFacts =
                await response.json()

            setFacts(data)
            setFactsEditing(false)
        } catch (error) {
            if (error instanceof Error) {
                setFactsSaveError(error.message)
            } else {
                setFactsSaveError(
                    at('classification.saveUnexpected'),
                )
            }
        } finally {
            setFactsSaving(false)
        }
    }

    return (
        <section
            className={`
                accident-dossier__section
                accident-dossier__section--clickable
                ${factsOpen
                    ? 'accident-dossier__section--open'
                    : ''}
            `}
        >
            <div
                className="accident-dossier__section-header"
                onClick={toggleFacts}
            >
                <div>
                    <h2>{at('facts.title')}</h2>

                    <p>{at('facts.description')}</p>
                </div>

                <div
                    className={`
                        accident-dossier__expand
                        ${factsOpen
                            ? 'accident-dossier__expand--open'
                            : ''}
                    `}
                    aria-hidden="true"
                >
                    ⌄
                </div>
            </div>

            {factsOpen && (
                <div className="accident-dossier__facts">
                    {factsLoading && (
                        <div className="accident-dossier__facts-empty">
                            {at('common.loading')}
                        </div>
                    )}

                    {factsError && (
                        <div className="accident-dossier__facts-error">
                            {factsError}
                        </div>
                    )}

                    {!factsLoading &&
                        !factsError &&
                        !factsEditing &&
                        facts === null && (
                            <div className="accident-dossier__facts-empty">
                                <p>
                                    {at('facts.empty')}
                                </p>

                                <button
                                    className="risky-button"
                                    type="button"
                                    onClick={startFactsEditing}
                                >
                                    {at('common.complete')}
                                </button>
                            </div>
                        )}

                    {!factsLoading &&
                        !factsEditing &&
                        facts !== null && (
                            <>
                                <div className="accident-dossier__section-header">
                                    <div />

                                    <button
                                        className="risky-button accident-dossier__edit-button"
                                        type="button"
                                        onClick={startFactsEditing}
                                    >
                                        {at('common.edit')}
                                    </button>
                                </div>

                                <div className="accident-dossier__facts-grid">
                                    <div>
                                        <span>{at('facts.client')}</span>
                                        <p>
                                            {facts.client ||
                                                at('common.notProvided')}
                                        </p>
                                    </div>

                                    <div>
                                        <span>{at('facts.witnesses')}</span>
                                        <p>
                                            {facts.witnesses ||
                                                'Aucun renseigné'}
                                        </p>
                                    </div>

                                    <div>
                                        <span>{at('facts.usualPosition')}</span>
                                        <p>
                                            {facts.usual_position === null
                                                ? at('common.notProvided')
                                                : facts.usual_position
                                                    ? at('common.yes')
                                                    : at('common.no')}
                                        </p>
                                    </div>

                                    <div className="accident-dossier__facts-wide">
                                        <span>
                                            Que faisait la victime avant
                                            l&apos;événement ?
                                        </span>
                                        <p>
                                            {facts.activity_before_event ||
                                                at('common.notProvided')}
                                        </p>
                                    </div>

                                    <div className="accident-dossier__facts-wide">
                                        <span>
                                            {at('facts.eventDescription')}
                                        </span>
                                        <p>
                                            {facts.event_description ||
                                                at('common.notProvidedF')}
                                        </p>
                                    </div>

                                    <div className="accident-dossier__facts-wide">
                                        <span>{at('facts.directCause')}</span>
                                        <p>
                                            {facts.direct_cause ||
                                                at('common.notProvidedF')}
                                        </p>
                                    </div>

                                    <div>
                                        <span>{at('facts.thirdParty')}</span>
                                        <p>
                                            {facts.caused_by_third_party === null
                                                ? at('common.notProvided')
                                                : facts.caused_by_third_party
                                                    ? at('common.yes')
                                                    : at('common.no')}
                                        </p>
                                    </div>

                                    <div>
                                        <span>{at('facts.police')}</span>
                                        <p>
                                            {facts.police_report === null
                                                ? at('common.notProvided')
                                                : facts.police_report
                                                    ? at('common.yes')
                                                    : at('common.no')}
                                        </p>
                                    </div>

                                    {facts.caused_by_third_party && (
                                        <div className="accident-dossier__facts-wide">
                                            <span>
                                                {at('facts.thirdPartyInfo')}
                                            </span>
                                            <p>
                                                {facts.third_party_details ||
                                                    'Non renseignées'}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </>
                        )}

                    {factsEditing && (
                        <div className="accident-dossier__facts-form">
                            <div className="accident-dossier__facts-grid">
                                <label>
                                    <span>{at('facts.client')}</span>
                                    <input
                                        value={factsDraft.client}
                                        onChange={(e) =>
                                            updateFactsField(
                                                'client',
                                                e.target.value,
                                            )
                                        }
                                    />
                                </label>

                                <label>
                                    <span>{at('facts.witnesses')}</span>
                                    <input
                                        value={factsDraft.witnesses}
                                        onChange={(e) =>
                                            updateFactsField(
                                                'witnesses',
                                                e.target.value,
                                            )
                                        }
                                    />
                                </label>

                                <label>
                                    <span>{at('facts.usualPosition')}</span>
                                    <select
                                        value={boolSelectValue(
                                            factsDraft.usual_position,
                                        )}
                                        onChange={(e) =>
                                            updateFactsField(
                                                'usual_position',
                                                selectValueToBool(
                                                    e.target.value,
                                                ),
                                            )
                                        }
                                    >
                                        <option value="">{at('common.notProvided')}</option>
                                        <option value="true">{at('common.yes')}</option>
                                        <option value="false">{at('common.no')}</option>
                                    </select>
                                </label>

                                <label className="accident-dossier__facts-wide">
                                    <span>
                                        Que faisait la victime avant
                                        l&apos;événement ?
                                    </span>

                                    <textarea
                                        rows={3}
                                        value={factsDraft.activity_before_event}
                                        onChange={(e) =>
                                            updateFactsField(
                                                'activity_before_event',
                                                e.target.value,
                                            )
                                        }
                                    />
                                </label>

                                <label className="accident-dossier__facts-wide">
                                    <span>
                                        {at('facts.eventDescription')}
                                    </span>

                                    <textarea
                                        rows={4}
                                        value={factsDraft.event_description}
                                        onChange={(e) =>
                                            updateFactsField(
                                                'event_description',
                                                e.target.value,
                                            )
                                        }
                                    />
                                </label>

                                <label className="accident-dossier__facts-wide">
                                    <span>{at('facts.directCause')}</span>

                                    <textarea
                                        rows={3}
                                        value={factsDraft.direct_cause}
                                        onChange={(e) =>
                                            updateFactsField(
                                                'direct_cause',
                                                e.target.value,
                                            )
                                        }
                                    />
                                </label>

                                <label>
                                    <span>{at('facts.thirdParty')}</span>
                                    <select
                                        value={boolSelectValue(
                                            factsDraft.caused_by_third_party,
                                        )}
                                        onChange={(e) =>
                                            updateFactsField(
                                                'caused_by_third_party',
                                                selectValueToBool(
                                                    e.target.value,
                                                ),
                                            )
                                        }
                                    >
                                        <option value="">{at('common.notProvided')}</option>
                                        <option value="true">{at('common.yes')}</option>
                                        <option value="false">{at('common.no')}</option>
                                    </select>
                                </label>

                                <label>
                                    <span>{at('facts.police')}</span>
                                    <select
                                        value={boolSelectValue(
                                            factsDraft.police_report,
                                        )}
                                        onChange={(e) =>
                                            updateFactsField(
                                                'police_report',
                                                selectValueToBool(
                                                    e.target.value,
                                                ),
                                            )
                                        }
                                    >
                                        <option value="">{at('common.notProvided')}</option>
                                        <option value="true">{at('common.yes')}</option>
                                        <option value="false">{at('common.no')}</option>
                                    </select>
                                </label>

                                {factsDraft.caused_by_third_party && (
                                    <label className="accident-dossier__facts-wide">
                                        <span>
                                            {at('facts.thirdPartyInfo')}
                                        </span>

                                        <textarea
                                            rows={3}
                                            value={factsDraft.third_party_details}
                                            onChange={(e) =>
                                                updateFactsField(
                                                    'third_party_details',
                                                    e.target.value,
                                                )
                                            }
                                        />
                                    </label>
                                )}
                            </div>

                            {factsSaveError && (
                                <p className="accident-dossier__facts-error">
                                    {factsSaveError}
                                </p>
                            )}

                            <div className="accident-dossier__facts-actions">
                                <button
                                    className="risky-button risky-button--cancel"
                                    type="button"
                                    onClick={cancelFactsEditing}
                                    disabled={factsSaving}
                                >
                                    {at('common.cancel')}
                                </button>

                                <button
                                    className="risky-button risky-button--confirm"
                                    type="button"
                                    onClick={saveFacts}
                                    disabled={factsSaving}
                                >
                                    {factsSaving
                                        ? 'Enregistrement...'
                                        : 'Enregistrer'}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </section>
    )
}

export default AccidentFactsSection
