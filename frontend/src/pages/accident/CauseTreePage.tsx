import { at } from './accidentI18n'
import {
    useCallback,
    useEffect,
    useState,
} from 'react'

import CauseTreeGraph from '../../components/CauseTreeGraph'

import './CauseTreePage.css'


// ============================================================
// CONFIGURATION
// ============================================================

const API_BASE_URL = 'http://127.0.0.1:8000'


// ============================================================
// TYPES
// ============================================================

type EventDetail = {
    id: number
    event_number: string
    event_date: string
    event_type: string
    description: string | null
}

type CauseFact = {
    id: number
    event_id: number
    fact_type: string
    description: string
    sort_order: number
    is_terminal: boolean
}

type CauseRelation = {
    id: number
    event_id: number
    cause_fact_id: number
    effect_fact_id: number
}

type CauseTreeResponse = {
    event_id: number
    facts: CauseFact[]
    relations: CauseRelation[]
}

type CauseLevel = {
    fact_id: number
    level: number
}

type CauseLevelsResponse = {
    event_id: number
    levels: CauseLevel[]
}

type CauseTreePageProps = {
    eventId: number
    onBack: () => void
}


// ============================================================
// OUTILS
// ============================================================

function formatEventType(
    value: string,
): string {
    switch (value) {
        case 'ACCIDENT':
            return at('common.eventType.accident')

        case 'INCIDENT':
            return at('common.eventType.incident')

        case 'NEAR_MISS':
            return at('common.eventType.nearMiss')

        case 'MATERIAL':
            return at('common.eventType.material')

        case 'ENVIRONMENT':
            return at('common.eventType.environment')

        default:
            return value
    }
}


// ============================================================
// COMPONENT
// ============================================================

function CauseTreePage({
    eventId,
    onBack,
}: CauseTreePageProps) {

    // ========================================================
    // STATE
    // ========================================================

    const [event, setEvent] =
        useState<EventDetail | null>(null)

    const [isCreatingFinalFact, setIsCreatingFinalFact] =
        useState(false)

    const [finalFactDescription, setFinalFactDescription] =
        useState('')

    const [isCreatingTree, setIsCreatingTree] =
        useState(false)

    const [tree, setTree] =
        useState<CauseTreeResponse | null>(null)

    const [levels, setLevels] =
        useState<CauseLevelsResponse | null>(null)

    const [error, setError] =
        useState<string | null>(null)


    // ========================================================
    // CHARGEMENT DE L'ÉVÉNEMENT
    // ========================================================

    const loadEvent = useCallback(async () => {
        try {
            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}`,
            )

            if (!response.ok) {
                throw new Error(
                    'Impossible de charger les informations de l’événement.',
                )
            }

            const data: EventDetail =
                await response.json()

            setEvent(data)

        } catch (error) {
            if (error instanceof Error) {
                setError(error.message)
            } else {
                setError(
                    'Impossible de charger les informations de l’événement.',
                )
            }
        }
    }, [eventId])


    // ========================================================
    // CHARGEMENT DE L'ARBRE
    // ========================================================

    const loadCauseTree = useCallback(async () => {
        try {
            setError(null)

            const treeResponse = await fetch(
                `${API_BASE_URL}/events/${eventId}/cause-tree`,
            )

            if (!treeResponse.ok) {
                throw new Error(
                    at('causeTree.loadError'),
                )
            }

            const treeData: CauseTreeResponse =
                await treeResponse.json()

            setTree(treeData)

            if (treeData.facts.length === 0) {
                setLevels({
                    event_id: treeData.event_id,
                    levels: [],
                })

                return
            }

            const levelsResponse = await fetch(
                `${API_BASE_URL}/events/${eventId}/cause-tree/levels`,
            )

            if (!levelsResponse.ok) {
                throw new Error(
                    at('causeTree.levelError'),
                )
            }

            const levelsData: CauseLevelsResponse =
                await levelsResponse.json()

            setLevels(levelsData)

        } catch (error) {
            if (error instanceof Error) {
                setError(error.message)
            } else {
                setError(
                    at('causeTree.loadError'),
                )
            }
        }
    }, [eventId])


    useEffect(() => {
        void Promise.all([
            loadEvent(),
            loadCauseTree(),
        ])
    }, [
        loadEvent,
        loadCauseTree,
    ])


    // ========================================================
    // CRÉATION DU FAIT FINAL
    // ========================================================

    const handleCreateTree = async () => {
        const description =
            finalFactDescription.trim()

        if (!description) {
            return
        }

        const sessionToken =
            sessionStorage.getItem(
                'risky_session_token',
            )

        if (!sessionToken) {
            setError(
                'Session RISKY absente.',
            )
            return
        }

        let createdFactId: number | null = null

        try {
            setIsCreatingTree(true)
            setError(null)

            const createResponse = await fetch(
                `${API_BASE_URL}/events/${eventId}/cause-tree/facts`,
                {
                    method: 'POST',

                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-Token': sessionToken,
                    },

                    body: JSON.stringify({
                        description,
                        sort_order: 0,
                    }),
                },
            )

            if (!createResponse.ok) {
                const errorData =
                    await createResponse.json()

                throw new Error(
                    errorData.detail ??
                    at('causeTree.createFinalError'),
                )
            }

            const createdFact: CauseFact =
                await createResponse.json()

            createdFactId = createdFact.id

            const finalResponse = await fetch(
                `${API_BASE_URL}/events/${eventId}/cause-tree/facts/${createdFact.id}/set-final`,
                {
                    method: 'POST',

                    headers: {
                        'X-Session-Token':
                            sessionToken,
                    },
                },
            )

            if (!finalResponse.ok) {
                const errorData =
                    await finalResponse.json()

                throw new Error(
                    errorData.detail ??
                    at('causeTree.defineFinalError'),
                )
            }

            setFinalFactDescription('')
            setIsCreatingFinalFact(false)

            await loadCauseTree()

        } catch (error) {
            if (createdFactId !== null) {
                try {
                    await fetch(
                        `${API_BASE_URL}/events/${eventId}/cause-tree/facts/${createdFactId}`,
                        {
                            method: 'DELETE',

                            headers: {
                                'X-Session-Token':
                                    sessionToken,
                            },
                        },
                    )
                } catch {
                    // L'erreur principale reste prioritaire.
                }
            }

            if (error instanceof Error) {
                setError(error.message)
            } else {
                setError(
                    'Une erreur est survenue lors de la création de l’arbre.',
                )
            }

        } finally {
            setIsCreatingTree(false)
        }
    }


    // ========================================================
    // DONNÉES MÉTIER
    // ========================================================

    const factsWithLevels =
        tree && levels
            ? tree.facts.map((fact) => {
                const levelInfo =
                    levels.levels.find(
                        (item) =>
                            item.fact_id === fact.id,
                    )

                return {
                    ...fact,
                    level:
                        levelInfo?.level ?? null,
                }
            })
            : []

    const treeExists =
        Boolean(
            tree &&
            levels &&
            tree.facts.length > 0,
        )


    // ========================================================
    // RENDER
    // ========================================================

    return (
        <div className="cause-tree-page">

            {/* ====================================================
                RETOUR
                ==================================================== */}

            <button
                className="cause-tree-page__back risky-back-button"
                type="button"
                onClick={onBack}
            >
                <span aria-hidden="true">
                    ←
                </span>

                {at('causeTree.back')}
            </button>


            {/* ====================================================
                CARTE D'IDENTITÉ DE L'ANALYSE
                ==================================================== */}

            <section className="cause-tree-page__summary">

                <div className="cause-tree-page__summary-main">

                    <div
                        className="cause-tree-page__summary-icon"
                        aria-hidden="true"
                    >
                        <span />
                        <span />
                        <span />
                    </div>

                    <div>
                        <h2>
                            {at('causeTree.title')}
                        </h2>

                        <p>{at('causeTree.intro')}</p>
                    </div>
                </div>

                <div className="cause-tree-page__meta">

                    <div>
                        <span>{at('causeTree.eventNo')}</span>
                        <strong>
                            {event?.event_number ??
                                eventId}
                        </strong>
                    </div>

                    <div>
                        <span>{at('overview.type')}</span>
                        <strong>
                            {event
                                ? formatEventType(
                                    event.event_type,
                                )
                                : '—'}
                        </strong>
                    </div>

                    <div>
                        <span>{at('overview.date')}</span>
                        <strong>
                            {event?.event_date
                                ? new Date(
                                    event.event_date,
                                ).toLocaleDateString(
                                    'fr-BE',
                                )
                                : '—'}
                        </strong>
                    </div>

                    <div>
                        <span>{at('causeTree.status')}</span>

                        <strong
                            className={`
                                cause-tree-page__status
                                ${treeExists
                                    ? 'cause-tree-page__status--started'
                                    : 'cause-tree-page__status--empty'}
                            `}
                        >
                            {treeExists
                                ? 'En construction'
                                : at('causeTree.toBuild')}
                        </strong>
                    </div>
                </div>
            </section>


            {/* ====================================================
                ERREUR
                ==================================================== */}

            {error && (
                <div className="cause-tree-page__error">
                    {error}
                </div>
            )}


            {/* ====================================================
                CHARGEMENT
                ==================================================== */}

            {(!tree || !levels) && !error && (
                <section className="cause-tree-page__workspace">
                    <div className="cause-tree-page__loading">
                        {at('causeTree.loading')}
                    </div>
                </section>
            )}


            {/* ====================================================
                ÉTAT VIDE
                ==================================================== */}

            {tree &&
                levels &&
                tree.facts.length === 0 && (
                    <section className="cause-tree-page__workspace">

                        <div className="cause-tree-page__empty">

                            <div
                                className="cause-tree-page__empty-icon"
                                aria-hidden="true"
                            >
                                ◇
                            </div>

                            <h2>
                                {at('causeTree.emptyTitle')}
                            </h2>

                            <p>{at('causeTree.emptyText')}<br />{at('causeTree.emptyHelp')}</p>
                        </div>


                        {!isCreatingFinalFact && (
                            <div className="cause-tree-page__start">
                                <button
                                    className="cause-tree-page__primary"
                                    type="button"
                                    onClick={() =>
                                        setIsCreatingFinalFact(
                                            true,
                                        )
                                    }
                                >
                                    <span aria-hidden="true">
                                        +
                                    </span>

                                    {at('causeTree.defineFinal')}
                                </button>
                            </div>
                        )}


                        {isCreatingFinalFact && (
                            <div className="cause-tree-page__final-form">

                                <label>
                                    <span>
                                        {at('causeTree.describeFinal')}
                                        <b aria-hidden="true"> *</b>
                                    </span>

                                    <input
                                        type="text"
                                        value={
                                            finalFactDescription
                                        }
                                        onChange={(event) =>
                                            setFinalFactDescription(
                                                event.target.value,
                                            )
                                        }
                                        placeholder={at('causeTree.finalPlaceholder')}
                                        autoFocus
                                        onKeyDown={(event) => {
                                            if (
                                                event.key === 'Enter' &&
                                                finalFactDescription.trim()
                                            ) {
                                                void handleCreateTree()
                                            }
                                        }}
                                    />
                                </label>

                                <div className="cause-tree-page__form-bottom">

                                    <div className="cause-tree-page__actions">

                                        <button
                                            className="cause-tree-page__primary"
                                            type="button"
                                            onClick={() =>
                                                void handleCreateTree()
                                            }
                                            disabled={
                                                isCreatingTree ||
                                                !finalFactDescription.trim()
                                            }
                                        >
                                            <span aria-hidden="true">
                                                +
                                            </span>

                                            {isCreatingTree
                                                ? at('causeTree.creating')
                                                : at('causeTree.defineFinal')}
                                        </button>

                                        <button
                                            className="cause-tree-page__cancel"
                                            type="button"
                                            onClick={() => {
                                                setFinalFactDescription(
                                                    '',
                                                )
                                                setIsCreatingFinalFact(
                                                    false,
                                                )
                                            }}
                                            disabled={
                                                isCreatingTree
                                            }
                                        >
                                            {at('common.cancel')}
                                        </button>

                                    </div>

                                    <div className="cause-tree-page__hint">
                                        <span aria-hidden="true">
                                            i
                                        </span>

                                        <p>{at('causeTree.nextHelp')}</p>
                                    </div>
                                </div>
                            </div>
                        )}


                        <div className="cause-tree-page__knowledge">
                            <strong>
                                {at('causeTree.goodToKnow')}
                            </strong>

                            <span>
                                L’arbre des causes permet d’identifier les
                                causes profondes d’un événement afin de
                                définir des mesures de prévention durables.
                            </span>
                        </div>

                    </section>
                )}


            {/* ====================================================
                ARBRE EXISTANT
                ==================================================== */}

            {tree &&
                levels &&
                tree.facts.length > 0 && (
                    <section className="cause-tree-page__workspace cause-tree-page__workspace--tree">

                        <div className="cause-tree-page__tree-header">
                            <div>
                                <h2>
                                    {at('causeTree.buildTitle')}
                                </h2>

                                <p>{at('causeTree.buildDesc')}</p>
                            </div>

                            <span className="cause-tree-page__tree-count">
                                {at('causeTree.factCount', { count: tree.facts.length })}
                            </span>
                        </div>

                        <CauseTreeGraph
                            eventId={eventId}
                            facts={factsWithLevels}
                            relations={
                                tree.relations
                            }
                            onTreeChanged={
                                loadCauseTree
                            }
                        />
                    </section>
                )}
        </div>
    )
}

export default CauseTreePage
