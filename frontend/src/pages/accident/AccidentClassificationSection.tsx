import { at } from './accidentI18n'
import './AccidentClassificationSection.css'

import {
    useCallback,
    useEffect,
    useState,
} from 'react'

import { useTranslation } from 'react-i18next'

import { API_BASE_URL } from './accidentApi'
import AccidentSeriousAlert from './AccidentSeriousAlert'
import FedrisCodeSelect from './FedrisCodeSelect'

import type {
    ClassificationDraft,
    EventClassification,
    EventCodeReference,
    EventCodeReferenceResponse,
    SeriousAccidentAssessment,
} from './accidentTypes'

function getReferenceLabel(
    references: EventCodeReference[],
    code: string | null,
    snapshot: string | null,
    language: string,
): string {
    if (!code) {
        return snapshot ?? ''
    }

    const reference =
        references.find(
            (item) => item.code === code,
        )

    if (!reference) {
        return snapshot ?? ''
    }

    if (language === 'nl') {
        return (
            reference.label_nl ||
            reference.label ||
            snapshot ||
            ''
        )
    }

    if (language === 'en') {
        return (
            reference.label_en ||
            reference.label ||
            snapshot ||
            ''
        )
    }

    if (language === 'pl') {
        return (
            reference.label_pl ||
            reference.label ||
            snapshot ||
            ''
        )
    }

    return (
        reference.label ||
        snapshot ||
        ''
    )
}

type AccidentClassificationSectionProps = {
    eventId: number
    open: boolean
}

function AccidentClassificationSection({
    eventId,
    open,
}: AccidentClassificationSectionProps) {
    const { i18n } = useTranslation()

    const language = i18n.language

    const [classification, setClassification] =
        useState<EventClassification | null>(null)

    const [classificationLoading, setClassificationLoading] =
        useState(false)

    const [classificationError, setClassificationError] =
        useState<string | null>(null)

    const [classificationEditing, setClassificationEditing] =
        useState(false)

    const [classificationSaving, setClassificationSaving] =
        useState(false)

    const [classificationSaveError, setClassificationSaveError] =
        useState<string | null>(null)

    const [deviationReferences, setDeviationReferences] =
        useState<EventCodeReference[]>([])

    const [materialAgentReferences, setMaterialAgentReferences] =
        useState<EventCodeReference[]>([])

    const [injuryNatureReferences, setInjuryNatureReferences] =
        useState<EventCodeReference[]>([])

    const [injuryLocationReferences, setInjuryLocationReferences] =
        useState<EventCodeReference[]>([])

    const [classificationDraft, setClassificationDraft] =
        useState<ClassificationDraft>({
            deviation_code: '',
            material_agent_code: '',
            injury_nature_code: '',
            injury_location_code: '',
        })

    const [seriousAccidentAssessment, setSeriousAccidentAssessment] =
        useState<SeriousAccidentAssessment | null>(null)

    const [seriousAccidentLoading, setSeriousAccidentLoading] =
        useState(false)

    const loadClassificationReferences = useCallback(async () => {
        const categories = [
            'DEVIATION',
            'MATERIAL_AGENT',
            'INJURY_NATURE',
            'INJURY_LOCATION',
        ]

        const responses = await Promise.all(
            categories.map((category) =>
                fetch(
                    `${API_BASE_URL}/event-code-references?category=${category}`,
                ),
            ),
        )

        for (const response of responses) {
            if (!response.ok) {
                throw new Error(
                    at('classification.refsError'),
                )
            }
        }

        const [
            deviationData,
            materialAgentData,
            injuryNatureData,
            injuryLocationData,
        ] = await Promise.all(
            responses.map(
                (response) =>
                    response.json() as Promise<EventCodeReferenceResponse>,
            ),
        )

        setDeviationReferences(deviationData.items)
        setMaterialAgentReferences(materialAgentData.items)
        setInjuryNatureReferences(injuryNatureData.items)
        setInjuryLocationReferences(injuryLocationData.items)
    }, [])

    const loadClassification = useCallback(async () => {
        const response = await fetch(
            `${API_BASE_URL}/events/${eventId}/classification`,
        )

        if (response.status === 404) {
            setClassification(null)
            return
        }

        if (!response.ok) {
            throw new Error(
                at('classification.loadError'),
            )
        }

        const data: EventClassification =
            await response.json()

        setClassification(data)
    }, [eventId])

    const loadSeriousAccidentAssessment = useCallback(async () => {
        try {
            setSeriousAccidentLoading(true)

            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}/serious-accident-assessment`,
            )

            if (!response.ok) {
                throw new Error(
                    at('classification.seriousError'),
                )
            }

            const data: SeriousAccidentAssessment =
                await response.json()

            setSeriousAccidentAssessment(data)
        } catch (error) {
            console.error(error)
            setSeriousAccidentAssessment(null)
        } finally {
            setSeriousAccidentLoading(false)
        }
    }, [eventId])

    const loadClassificationSection = useCallback(async () => {
        try {
            setClassificationLoading(true)
            setClassificationError(null)

            await Promise.all([
                loadClassification(),
                loadClassificationReferences(),
                loadSeriousAccidentAssessment(),
            ])
        } catch (error) {
            if (error instanceof Error) {
                setClassificationError(error.message)
            } else {
                setClassificationError(
                    'Une erreur est survenue.',
                )
            }
        } finally {
            setClassificationLoading(false)
        }
    }, [
        loadClassification,
        loadClassificationReferences,
        loadSeriousAccidentAssessment,
    ])

    useEffect(() => {
        if (!open) {
            return
        }

        void loadClassificationSection()
    }, [open, loadClassificationSection])

    const startClassificationEditing = () => {
        setClassificationDraft({
            deviation_code:
                classification?.deviation_code ?? '',
            material_agent_code:
                classification?.material_agent_code ?? '',
            injury_nature_code:
                classification?.injury_nature_code ?? '',
            injury_location_code:
                classification?.injury_location_code ?? '',
        })

        setClassificationSaveError(null)
        setClassificationEditing(true)
    }

    const cancelClassificationEditing = () => {
        setClassificationEditing(false)
        setClassificationSaveError(null)
    }

    const updateClassificationField = <
        K extends keyof ClassificationDraft,
    >(
        field: K,
        value: ClassificationDraft[K],
    ) => {
        setClassificationDraft((current) => ({
            ...current,
            [field]: value,
        }))
    }

    const saveClassification = async () => {
        const token = sessionStorage.getItem(
            'risky_session_token',
        )

        if (!token) {
            setClassificationSaveError(
                'Session utilisateur introuvable.',
            )
            return
        }

        try {
            setClassificationSaving(true)
            setClassificationSaveError(null)

            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}/classification`,
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-Token': token,
                    },
                    body: JSON.stringify({
                        deviation_code:
                            classificationDraft.deviation_code || null,
                        material_agent_code:
                            classificationDraft.material_agent_code || null,
                        injury_nature_code:
                            classificationDraft.injury_nature_code || null,
                        injury_location_code:
                            classificationDraft.injury_location_code || null,
                    }),
                },
            )

            if (!response.ok) {
                const data = await response.json().catch(
                    () => null,
                )

                throw new Error(
                    data?.detail ||
                    at('classification.saveError'),
                )
            }

            await Promise.all([
                loadClassification(),
                loadSeriousAccidentAssessment(),
            ])

            window.dispatchEvent(
                new CustomEvent('risky:serious-accident-assessment-changed', {
                    detail: { eventId },
                }),
            )

            setClassificationEditing(false)
        } catch (error) {
            if (error instanceof Error) {
                setClassificationSaveError(error.message)
            } else {
                setClassificationSaveError(
                    at('classification.saveUnexpected'),
                )
            }
        } finally {
            setClassificationSaving(false)
        }
    }

    if (!open) {
        return null
    }

    return (
        <>
            <div className="accident-dossier__facts">
                {classificationLoading && (
                    <div className="accident-dossier__facts-empty">
                        {at('classification.loading')}
                    </div>
                )}

                {classificationError && (
                    <div className="accident-dossier__facts-error">
                        {classificationError}
                    </div>
                )}

                {!classificationLoading &&
                    !classificationError &&
                    !classificationEditing &&
                    classification === null && (
                        <div className="accident-dossier__facts-empty">
                            <p>
                                {at('classification.empty')}
                            </p>

                            <button
                                className="risky-button"
                                type="button"
                                onClick={startClassificationEditing}
                            >
                                {at('common.complete')}
                            </button>
                        </div>
                    )}

                {!classificationLoading &&
                    !classificationError &&
                    !classificationEditing &&
                    classification !== null && (
                        <>
                            <div className="accident-dossier__section-header">
                                <div>
                                    <h3>
                                        {at('classification.title')}
                                    </h3>
                                </div>

                                <button
                                    className="risky-button accident-dossier__edit-button"
                                    type="button"
                                    onClick={startClassificationEditing}
                                >
                                    {at('common.edit')}
                                </button>
                            </div>

                            <div className="accident-dossier__facts-grid">
                                <div className="accident-dossier__facts-wide">
                                    <span>{at('classification.deviation')}</span>
                                    <p>
                                        {classification.deviation_code
                                            ? `${classification.deviation_code} - ${getReferenceLabel(
                                                deviationReferences,
                                                classification.deviation_code,
                                                classification.deviation_label_snapshot,
                                                language,
                                            )}`
                                            : at('common.notProvidedF')}
                                    </p>
                                </div>

                                <div className="accident-dossier__facts-wide">
                                    <span>
                                        {at('classification.materialAgent')}
                                    </span>
                                    <p>
                                        {classification.material_agent_code
                                            ? `${classification.material_agent_code} - ${getReferenceLabel(
                                                materialAgentReferences,
                                                classification.material_agent_code,
                                                classification.material_agent_label_snapshot,
                                                language,
                                            )}`
                                            : at('common.notProvided')}
                                    </p>
                                </div>

                                <div className="accident-dossier__facts-wide">
                                    <span>
                                        {at('classification.injuryNature')}
                                    </span>
                                    <p>
                                        {classification.injury_nature_code
                                            ? `${classification.injury_nature_code} - ${getReferenceLabel(
                                                injuryNatureReferences,
                                                classification.injury_nature_code,
                                                classification.injury_nature_label_snapshot,
                                                language,
                                            )}`
                                            : at('common.notProvidedF')}
                                    </p>
                                </div>

                                <div className="accident-dossier__facts-wide">
                                    <span>
                                        {at('classification.injuryLocation')}
                                    </span>
                                    <p>
                                        {classification.injury_location_code
                                            ? `${classification.injury_location_code} - ${getReferenceLabel(
                                                injuryLocationReferences,
                                                classification.injury_location_code,
                                                classification.injury_location_label_snapshot,
                                                language,
                                            )}`
                                            : at('common.notProvided')}
                                    </p>
                                </div>
                            </div>
                        </>
                    )}

                {classificationEditing && (
                    <div className="accident-dossier__facts-form">
                        <div className="accident-dossier__facts-grid">
                            <FedrisCodeSelect
                                label={at('classification.deviation')}
                                value={classificationDraft.deviation_code}
                                references={deviationReferences}
                                emptyLabel={at('common.notProvidedF')}
                                onChange={(value) =>
                                    updateClassificationField(
                                        'deviation_code',
                                        value,
                                    )
                                }
                            />

                            <FedrisCodeSelect
                                label={at('classification.materialAgent')}
                                value={classificationDraft.material_agent_code}
                                references={materialAgentReferences}
                                emptyLabel={at('common.notProvided')}
                                onChange={(value) =>
                                    updateClassificationField(
                                        'material_agent_code',
                                        value,
                                    )
                                }
                            />

                            <FedrisCodeSelect
                                label={at('classification.injuryNature')}
                                value={classificationDraft.injury_nature_code}
                                references={injuryNatureReferences}
                                emptyLabel={at('common.notProvidedF')}
                                onChange={(value) =>
                                    updateClassificationField(
                                        'injury_nature_code',
                                        value,
                                    )
                                }
                            />

                            <FedrisCodeSelect
                                label={at('classification.injuryLocation')}
                                value={classificationDraft.injury_location_code}
                                references={injuryLocationReferences}
                                emptyLabel={at('common.notProvided')}
                                onChange={(value) =>
                                    updateClassificationField(
                                        'injury_location_code',
                                        value,
                                    )
                                }
                            />
                        </div>

                        {classificationSaveError && (
                            <p className="accident-dossier__facts-error">
                                {classificationSaveError}
                            </p>
                        )}

                        <div className="accident-dossier__facts-actions">
                            <button
                                className="risky-button risky-button--cancel"
                                type="button"
                                onClick={cancelClassificationEditing}
                                disabled={classificationSaving}
                            >
                                {at('common.cancel')}
                            </button>

                            <button
                                className="risky-button risky-button--confirm"
                                type="button"
                                onClick={saveClassification}
                                disabled={classificationSaving}
                            >
                                {classificationSaving
                                    ? 'Enregistrement...'
                                    : 'Enregistrer'}
                            </button>
                        </div>
                    </div>
                )}
            </div>

            <AccidentSeriousAlert
                assessment={seriousAccidentAssessment}
                loading={seriousAccidentLoading}
                classification={classification}
            />
        </>
    )
}

export default AccidentClassificationSection

