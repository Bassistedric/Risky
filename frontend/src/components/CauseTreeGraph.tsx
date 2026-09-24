import {
    useCallback,
    useEffect,
    useLayoutEffect,
    useRef,
    useState,
} from 'react'

import { useTranslation } from 'react-i18next'

import CauseFactCard from './CauseFactCard'
import './CauseTreeGraph.css'

type GraphFact = {
    id: number
    description: string
    fact_type: string
    is_terminal: boolean
    sort_order: number
    level: number | null
}

type GraphRelation = {
    id: number
    cause_fact_id: number
    effect_fact_id: number
}

type CauseTreeGraphProps = {
    eventId: number
    facts: GraphFact[]
    relations: GraphRelation[]
    onTreeChanged: () => Promise<void>
}

type GraphLine = {
    relationId: number
    x1: number
    y1: number
    x2: number
    y2: number
}

function CauseTreeGraph({
    eventId,
    facts,
    relations,
    onTreeChanged,
}: CauseTreeGraphProps) {

    const { t } = useTranslation()

    // ============================================================
    // STATE
    // ============================================================

    const graphRef = useRef<HTMLDivElement | null>(null)

    const [lines, setLines] = useState<GraphLine[]>([])
    const [selectedFactId, setSelectedFactId] =
        useState<number | null>(null)

    const [isAddingCause, setIsAddingCause] =
        useState(false)

    const [newCauseDescription, setNewCauseDescription] =
        useState('')

    const [isEditingFact, setIsEditingFact] =
        useState(false)

    const [editedDescription, setEditedDescription] =
        useState('')

    // ============================================================
    // GRAPH LAYOUT
    // ============================================================

    const linkedFacts = facts.filter(
        (fact) => fact.level !== null
    )

    const [isConfirmingDelete, setIsConfirmingDelete] =
        useState(false)

    const [isLinkingFact, setIsLinkingFact] =
        useState(false)

    const [isManagingLinks, setIsManagingLinks] =
        useState(false)

    const unlinkedFacts = facts.filter(
        (fact) => fact.level === null
    )

    const levels = Array.from(
        new Set(
            linkedFacts.map(
                (fact) => fact.level as number
            )
        )
    ).sort((a, b) => b - a)

    const positionByFactId = new Map<number, number>()

    const factsByLevel = new Map<number, GraphFact[]>()

    levels
        .slice()
        .sort((a, b) => a - b)
        .forEach((level) => {
            const factsAtLevel = linkedFacts.filter(
                (fact) => fact.level === level
            )

            const factsWithBarycenter = factsAtLevel.map(
                (fact) => {
                    const effects = relations
                        .filter(
                            (relation) =>
                                relation.cause_fact_id === fact.id
                        )
                        .map((relation) =>
                            positionByFactId.get(
                                relation.effect_fact_id
                            )
                        )
                        .filter(
                            (
                                position
                            ): position is number =>
                                position !== undefined
                        )

                    const barycenter =
                        effects.length > 0
                            ? effects.reduce(
                                (sum, position) =>
                                    sum + position,
                                0
                            ) / effects.length
                            : fact.sort_order

                    return {
                        fact,
                        barycenter,
                    }
                }
            )

            factsWithBarycenter.sort((a, b) => {
                if (a.barycenter !== b.barycenter) {
                    return a.barycenter - b.barycenter
                }

                return (
                    a.fact.sort_order -
                    b.fact.sort_order
                )
            })

            const orderedFacts =
                factsWithBarycenter.map(
                    (item) => item.fact
                )

            orderedFacts.forEach(
                (fact, index) => {
                    positionByFactId.set(
                        fact.id,
                        index
                    )
                }
            )

            factsByLevel.set(
                level,
                orderedFacts
            )
        })

    const getConnectorX = (
        rect: DOMRect,
        graphRect: DOMRect,
        index: number,
        total: number
    ) => {
        if (total <= 1) {
            return (
                rect.left -
                graphRect.left +
                rect.width / 2
            )
        }

        const usableWidth = rect.width * 0.6
        const start =
            rect.left -
            graphRect.left +
            (rect.width - usableWidth) / 2

        const step =
            usableWidth / (total - 1)

        return start + step * index
    }

    const calculateLines = useCallback(() => {
        const graphElement = graphRef.current

        if (!graphElement) {
            return
        }

        const graphRect =
            graphElement.getBoundingClientRect()

        const newLines: GraphLine[] = []

        const outgoingByFact =
            new Map<number, GraphRelation[]>()

        const incomingByFact =
            new Map<number, GraphRelation[]>()

        relations.forEach((relation) => {
            const outgoing =
                outgoingByFact.get(
                    relation.cause_fact_id
                ) ?? []

            outgoing.push(relation)

            outgoingByFact.set(
                relation.cause_fact_id,
                outgoing
            )

            const incoming =
                incomingByFact.get(
                    relation.effect_fact_id
                ) ?? []

            incoming.push(relation)

            incomingByFact.set(
                relation.effect_fact_id,
                incoming
            )
        })

        outgoingByFact.forEach(
            (factRelations) => {
                factRelations.sort((a, b) => {
                    const aElement =
                        graphElement.querySelector<HTMLElement>(
                            `[data-fact-id="${a.effect_fact_id}"]`
                        )

                    const bElement =
                        graphElement.querySelector<HTMLElement>(
                            `[data-fact-id="${b.effect_fact_id}"]`
                        )

                    if (!aElement || !bElement) {
                        return 0
                    }

                    return (
                        aElement.getBoundingClientRect().left -
                        bElement.getBoundingClientRect().left
                    )
                })
            }
        )

        incomingByFact.forEach(
            (factRelations) => {
                factRelations.sort((a, b) => {
                    const aElement =
                        graphElement.querySelector<HTMLElement>(
                            `[data-fact-id="${a.cause_fact_id}"]`
                        )

                    const bElement =
                        graphElement.querySelector<HTMLElement>(
                            `[data-fact-id="${b.cause_fact_id}"]`
                        )

                    if (!aElement || !bElement) {
                        return 0
                    }

                    return (
                        aElement.getBoundingClientRect().left -
                        bElement.getBoundingClientRect().left
                    )
                })
            }
        )

        relations.forEach((relation) => {
            const causeElement =
                graphElement.querySelector<HTMLElement>(
                    `[data-fact-id="${relation.cause_fact_id}"]`
                )

            const effectElement =
                graphElement.querySelector<HTMLElement>(
                    `[data-fact-id="${relation.effect_fact_id}"]`
                )

            if (!causeElement || !effectElement) {
                return
            }

            const causeRect =
                causeElement.getBoundingClientRect()

            const effectRect =
                effectElement.getBoundingClientRect()

            const outgoingRelations =
                outgoingByFact.get(
                    relation.cause_fact_id
                ) ?? []

            const incomingRelations =
                incomingByFact.get(
                    relation.effect_fact_id
                ) ?? []

            const outgoingIndex =
                outgoingRelations.findIndex(
                    (item) =>
                        item.id === relation.id
                )

            const incomingIndex =
                incomingRelations.findIndex(
                    (item) =>
                        item.id === relation.id
                )

            newLines.push({
                relationId: relation.id,

                x1: getConnectorX(
                    causeRect,
                    graphRect,
                    outgoingIndex,
                    outgoingRelations.length
                ),

                y1:
                    causeRect.bottom -
                    graphRect.top,

                x2: getConnectorX(
                    effectRect,
                    graphRect,
                    incomingIndex,
                    incomingRelations.length
                ),

                y2:
                    effectRect.top -
                    graphRect.top,
            })
        })

        setLines(newLines)
    }, [relations])

    useLayoutEffect(() => {
        const graphElement = graphRef.current

        if (!graphElement) {
            return
        }

        let frameId: number | null = null

        const scheduleCalculation = () => {
            if (frameId !== null) {
                cancelAnimationFrame(frameId)
            }

            frameId = requestAnimationFrame(() => {
                calculateLines()
                frameId = null
            })
        }

        scheduleCalculation()

        const resizeObserver = new ResizeObserver(() => {
            scheduleCalculation()
        })

        resizeObserver.observe(graphElement)

        return () => {
            resizeObserver.disconnect()

            if (frameId !== null) {
                cancelAnimationFrame(frameId)
            }
        }
    }, [calculateLines, facts])

    useEffect(() => {
        window.addEventListener(
            'resize',
            calculateLines
        )

        return () => {
            window.removeEventListener(
                'resize',
                calculateLines
            )
        }
    }, [calculateLines])

    const handleFactClick = async (
        factId: number
    ) => {
        if (
            isLinkingFact &&
            selectedFactId !== null
        ) {
            if (factId === selectedFactId) {
                return
            }

            const sessionToken = sessionStorage.getItem(
                'risky_session_token'
            )

            if (!sessionToken) {
                alert(t('accident.causeTree.errors.noSession'))
                return
            }

            try {
                const response = await fetch(
                    `http://127.0.0.1:8000/events/${eventId}/cause-tree/relations`,
                    {
                        method: 'POST',

                        headers: {
                            'Content-Type': 'application/json',
                            'X-Session-Token': sessionToken,
                        },

                        body: JSON.stringify({
                            cause_fact_id: selectedFactId,
                            effect_fact_id: factId,
                        }),
                    }
                )

                if (!response.ok) {
                    const errorData = await response.json()

                    throw new Error(
                        errorData.detail ??
                        t('accident.causeTree.errors.createRelation')
                    )
                }

                setIsLinkingFact(false)
                setSelectedFactId(null)

                await onTreeChanged()
            } catch (error) {
                if (error instanceof Error) {
                    alert(error.message)
                } else {
                    alert(
                        t('accident.causeTree.errors.link')
                    )
                }
            }

            return
        }

        setSelectedFactId(
            (currentFactId) =>
                currentFactId === factId
                    ? null
                    : factId
        )
    }

    // ============================================================
    // SELECTION / BUSINESS STATE
    // ============================================================

    const selectedFact = facts.find(
        (fact) => fact.id === selectedFactId
    )

    const selectedFactOutgoingRelations =
        selectedFact
            ? relations.filter(
                (relation) =>
                    relation.cause_fact_id ===
                    selectedFact.id
            )
            : []

    const selectedFactHasUpstreamCause =
        selectedFact
            ? relations.some(
                (relation) =>
                    relation.effect_fact_id === selectedFact.id
            )
            : false

    const canCloseSelectedBranch =
        selectedFact?.fact_type === 'CAUSE' &&
        !selectedFact.is_terminal &&
        !selectedFactHasUpstreamCause

    // ============================================================
    // ACTION HANDLERS
    // ============================================================

    const handleCloseBranch = async () => {
        if (!selectedFact || !canCloseSelectedBranch) {
            return
        }

        const sessionToken = sessionStorage.getItem(
            'risky_session_token'
        )

        if (!sessionToken) {
            alert(t('accident.causeTree.errors.noSession'))
            return
        }

        try {
            const response = await fetch(
                `http://127.0.0.1:8000/events/${eventId}/cause-tree/facts/${selectedFact.id}/close-branch`,
                {
                    method: 'POST',

                    headers: {
                        'X-Session-Token': sessionToken,
                    },
                }
            )

            if (!response.ok) {
                const errorData = await response.json()

                throw new Error(
                    errorData.detail ??
                    t('accident.causeTree.errors.closeBranch')
                )
            }

            setSelectedFactId(null)

            await onTreeChanged()
        } catch (error) {
            if (error instanceof Error) {
                alert(error.message)
            } else {
                alert(
                    t('accident.causeTree.errors.generic')
                )
            }
        }
    }

    const handleReopenBranch = async () => {
        if (
            !selectedFact ||
            selectedFact.fact_type !== 'CAUSE' ||
            !selectedFact.is_terminal
        ) {
            return
        }

        const sessionToken = sessionStorage.getItem(
            'risky_session_token'
        )

        if (!sessionToken) {
            alert(t('accident.causeTree.errors.noSession'))
            return
        }

        try {
            const response = await fetch(
                `http://127.0.0.1:8000/events/${eventId}/cause-tree/facts/${selectedFact.id}/reopen-branch`,
                {
                    method: 'POST',

                    headers: {
                        'X-Session-Token': sessionToken,
                    },
                }
            )

            if (!response.ok) {
                const errorData = await response.json()

                throw new Error(
                    errorData.detail ??
                    t('accident.causeTree.errors.reopenBranch')
                )
            }

            setSelectedFactId(null)

            await onTreeChanged()
        } catch (error) {
            if (error instanceof Error) {
                alert(error.message)
            } else {
                alert(
                    t('accident.causeTree.errors.generic')
                )
            }
        }
    }

    const handleDeleteRelation = async (
        relationId: number
    ) => {
        const sessionToken = sessionStorage.getItem(
            'risky_session_token'
        )

        if (!sessionToken) {
            alert(t('accident.causeTree.errors.noSession'))
            return
        }

        try {
            const response = await fetch(
                `http://127.0.0.1:8000/events/${eventId}/cause-tree/relations/${relationId}`,
                {
                    method: 'DELETE',

                    headers: {
                        'X-Session-Token': sessionToken,
                    },
                }
            )

            if (!response.ok) {
                const errorData = await response.json()

                throw new Error(
                    errorData.detail ??
                    t('accident.causeTree.errors.deleteRelation')
                )
            }

            await onTreeChanged()
        } catch (error) {
            if (error instanceof Error) {
                alert(error.message)
            } else {
                alert(
                    t('accident.causeTree.errors.deleteLink')
                )
            }
        }
    }

    const handleDeleteFact = async () => {

        if (
            !selectedFact ||
            selectedFact.fact_type === 'FINAL'
        ) {
            return
        }

        const sessionToken = sessionStorage.getItem(
            'risky_session_token'
        )

        if (!sessionToken) {
            alert(t('accident.causeTree.errors.noSession'))
            return
        }

        try {

            const response = await fetch(
                `http://127.0.0.1:8000/events/${eventId}/cause-tree/facts/${selectedFact.id}`,
                {
                    method: 'DELETE',

                    headers: {
                        'X-Session-Token': sessionToken,
                    },
                }
            )

            if (!response.ok) {
                const errorData = await response.json()

                throw new Error(
                    errorData.detail ??
                    t('accident.causeTree.errors.deleteFact')
                )
            }

            setIsConfirmingDelete(false)
            setSelectedFactId(null)

            await onTreeChanged()
        } catch (error) {
            if (error instanceof Error) {
                alert(error.message)
            } else {
                alert(
                    t('accident.causeTree.errors.delete')
                )
            }
        }
    }

    const handleEditFact = async () => {
        if (!selectedFact) {
            return
        }

        const description = editedDescription.trim()

        if (!description) {
            return
        }

        const sessionToken = sessionStorage.getItem(
            'risky_session_token'
        )

        if (!sessionToken) {
            alert(t('accident.causeTree.errors.noSession'))
            return
        }

        try {
            const response = await fetch(
                `http://127.0.0.1:8000/events/${eventId}/cause-tree/facts/${selectedFact.id}`,
                {
                    method: 'PUT',

                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-Token': sessionToken,
                    },

                    body: JSON.stringify({
                        description,
                    }),
                }
            )

            if (!response.ok) {
                const errorData = await response.json()

                throw new Error(
                    errorData.detail ??
                    t('accident.causeTree.errors.editFact')
                )
            }

            setEditedDescription('')
            setIsEditingFact(false)
            setSelectedFactId(null)

            await onTreeChanged()
        } catch (error) {
            if (error instanceof Error) {
                alert(error.message)
            } else {
                alert(
                    t('accident.causeTree.errors.edit')
                )
            }
        }
    }

    const handleAddCause = async () => {
        if (!selectedFact) {
            return
        }

        const description = newCauseDescription.trim()

        if (!description) {
            return
        }

        const sessionToken = sessionStorage.getItem(
            'risky_session_token'
        )

        if (!sessionToken) {
            alert(t('accident.causeTree.errors.noSession'))
            return
        }

        try {
            const response = await fetch(
                `http://127.0.0.1:8000/events/${eventId}/cause-tree/guided-facts`,
                {
                    method: 'POST',

                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-Token': sessionToken,
                    },

                    body: JSON.stringify({
                        description,
                        sort_order: 0,
                        effect_fact_ids: [
                            selectedFact.id,
                        ],
                    }),
                }
            )

            if (!response.ok) {
                const errorData = await response.json()

                throw new Error(
                    errorData.detail ??
                    t('accident.causeTree.errors.addCause')
                )
            }

            setNewCauseDescription('')
            setIsAddingCause(false)
            setSelectedFactId(null)

            await onTreeChanged()

        } catch (error) {
            if (error instanceof Error) {
                alert(error.message)
            } else {
                alert(
                    t('accident.causeTree.errors.add')
                )
            }
        }
    }

    // ============================================================
    // RENDER
    // ============================================================

    return (
        <div
            ref={graphRef}
            className="cause-tree-graph"
        >
            {selectedFact && (
                <div className="cause-tree-graph__actions">
                    {!isAddingCause &&
                        !isEditingFact &&
                        !isConfirmingDelete &&
                        !isLinkingFact &&
                        !isManagingLinks && (
                            <>
                                <span>
                                    {t('accident.causeTree.selection', { description: selectedFact.description })}
                                </span>

                                <button
                                    className="risky-button risky-button--action"
                                    type="button"
                                    onClick={() => setIsAddingCause(true)}
                                >
                                    {t('accident.causeTree.addCause')}
                                </button>

                                <button
                                    className="risky-button risky-button--action"
                                    type="button"
                                    onClick={() => {
                                        setEditedDescription(
                                            selectedFact.description
                                        )
                                        setIsEditingFact(true)
                                    }}
                                >
                                    {t('accident.causeTree.edit')}
                                </button>

                                {selectedFact.fact_type !== 'FINAL' && (
                                    <button
                                        className="risky-button risky-button--action"
                                        type="button"
                                        onClick={() =>
                                            setIsLinkingFact(true)
                                        }
                                    >
                                        {t('accident.causeTree.linkAnotherFact')}
                                    </button>
                                )}

                                {selectedFact.fact_type !== 'FINAL' &&
                                    selectedFactOutgoingRelations.length > 0 && (
                                        <button
                                            className="risky-button risky-button--action"
                                            type="button"
                                            onClick={() =>
                                                setIsManagingLinks(true)
                                            }
                                        >
                                            {t('accident.causeTree.manageLinks')}
                                        </button>
                                    )}

                                {selectedFact.fact_type !== 'FINAL' && (
                                    <button
                                        className="risky-button risky-button--cancel"
                                        type="button"
                                        onClick={() =>
                                            setIsConfirmingDelete(true)
                                        }
                                    >
                                        {t('accident.causeTree.delete')}
                                    </button>
                                )}

                                {canCloseSelectedBranch && (
                                    <button
                                        className="risky-button risky-button--validate"
                                        type="button"
                                        onClick={handleCloseBranch}
                                    >
                                        {t('accident.causeTree.closeBranch')}
                                    </button>
                                )}
                            </>
                        )}

                    {selectedFact.fact_type === 'CAUSE' &&
                        selectedFact.is_terminal && (
                            <button
                                className="risky-button risky-button--action"
                                type="button"
                                onClick={handleReopenBranch}
                            >
                                {t('accident.causeTree.reopenBranch')}
                            </button>
                        )}

                    {isAddingCause && (
                        <div className="cause-tree-graph__add-cause">
                            <span>
                                {t('accident.causeTree.why', { description: selectedFact.description })}
                            </span>

                            <input
                                type="text"
                                value={newCauseDescription}
                                onChange={(event) =>
                                    setNewCauseDescription(
                                        event.target.value
                                    )
                                }
                                placeholder={t('accident.causeTree.causePlaceholder')}
                                autoFocus
                            />

                            <button
                                className="risky-button risky-button--cancel"
                                type="button"
                                onClick={() => {
                                    setIsAddingCause(false)
                                    setNewCauseDescription('')
                                }}
                            >
                                {t('common.cancel')}
                            </button>

                            <button
                                className="risky-button risky-button--validate"
                                type="button"
                                disabled={!newCauseDescription.trim()}
                                onClick={handleAddCause}
                            >
                                {t('accident.causeTree.add')}
                            </button>
                        </div>
                    )}

                    {isEditingFact && (
                        <div className="cause-tree-graph__add-cause">
                            <span>{t('accident.causeTree.editFact')}</span>

                            <input
                                type="text"
                                value={editedDescription}
                                onChange={(event) =>
                                    setEditedDescription(
                                        event.target.value
                                    )
                                }
                                autoFocus
                            />

                            <button
                                className="risky-button risky-button--cancel"
                                type="button"
                                onClick={() => {
                                    setIsEditingFact(false)
                                    setEditedDescription('')
                                }}
                            >
                                {t('common.cancel')}
                            </button>

                            <button
                                className="risky-button risky-button--validate"
                                type="button"
                                disabled={
                                    !editedDescription.trim() ||
                                    editedDescription.trim() ===
                                    selectedFact.description
                                }
                                onClick={handleEditFact}
                            >
                                {t('common.save')}
                            </button>
                        </div>
                    )}

                    {isLinkingFact && (
                        <div className="cause-tree-graph__add-cause">
                            <span>
                                {t('accident.causeTree.chooseAlsoExplainedBy', { description: selectedFact.description })}
                            </span>

                            <button
                                className="risky-button risky-button--cancel"
                                type="button"
                                onClick={() =>
                                    setIsLinkingFact(false)
                                }
                            >
                                {t('common.cancel')}
                            </button>
                        </div>
                    )}

                    {/* ============================================================
            LINK MANAGER
            ============================================================ */}

                    {isManagingLinks && (
                        <div className="cause-tree-graph__link-manager">
                            <strong>
                                {t('accident.causeTree.explains', { description: selectedFact.description })}
                            </strong>

                            {selectedFactOutgoingRelations.map(
                                (relation) => {
                                    const effectFact = facts.find(
                                        (fact) =>
                                            fact.id ===
                                            relation.effect_fact_id
                                    )

                                    if (!effectFact) {
                                        return null
                                    }

                                    return (
                                        <div
                                            key={relation.id}
                                            className="cause-tree-graph__link-manager-row"
                                        >
                                            <span>
                                                {effectFact.description}
                                            </span>

                                            <button
                                                className="risky-button risky-button--cancel"
                                                type="button"
                                                onClick={() =>
                                                    handleDeleteRelation(
                                                        relation.id
                                                    )
                                                }
                                            >
                                                {t('accident.causeTree.removeLink')}
                                            </button>
                                        </div>
                                    )
                                }
                            )}

                            <button
                                className="risky-button risky-button--neutral"
                                type="button"
                                onClick={() =>
                                    setIsManagingLinks(false)
                                }
                            >
                                {t('common.back')}
                            </button>
                        </div>
                    )}

                    {isConfirmingDelete && (
                        <div className="cause-tree-graph__delete-confirmation">
                            <div>
                                <strong>
                                    {t('accident.causeTree.deleteQuestion', { description: selectedFact.description })}
                                </strong>

                                <p>{t('accident.causeTree.deleteHelp')}</p>
                            </div>

                            <button
                                className="risky-button risky-button--cancel"
                                type="button"
                                onClick={() =>
                                    setIsConfirmingDelete(false)
                                }
                            >
                                {t('common.cancel')}
                            </button>

                            <button
                                className="risky-button risky-button--validate"
                                type="button"
                                onClick={handleDeleteFact}
                            >
                                {t('accident.causeTree.confirmDelete')}
                            </button>
                        </div>
                    )}
                </div>
            )}

            <svg
                className="cause-tree-graph__connections"
                aria-hidden="true"
            >
                <defs>
                    <marker
                        id="cause-tree-arrow"
                        viewBox="0 0 10 10"
                        refX="10"
                        refY="5"
                        markerWidth="7"
                        markerHeight="7"
                        orient="auto"
                        markerUnits="strokeWidth"
                    >
                        <path
                            d="M 0 0 L 10 5 L 0 10 z"
                            fill="currentColor"
                        />
                    </marker>
                </defs>

                {lines.map((line) => (
                    <line
                        key={line.relationId}
                        x1={line.x1}
                        y1={line.y1}
                        x2={line.x2}
                        y2={line.y2}
                        stroke="currentColor"
                        strokeWidth="2"
                        markerEnd="url(#cause-tree-arrow)"
                    />
                ))}
            </svg>

            {
                levels.map((level) => {
                    const factsAtLevel =
                        factsByLevel.get(level) ?? []

                    return (
                        <div
                            key={level}
                            className="cause-tree-graph__row"
                        >
                            {factsAtLevel.map((fact) => (
                                <div
                                    key={fact.id}
                                    className="cause-tree-graph__fact"
                                    data-fact-id={fact.id}
                                >
                                    <CauseFactCard
                                        description={fact.description}
                                        factType={fact.fact_type}
                                        isTerminal={fact.is_terminal}
                                        level={fact.level}
                                        isSelected={
                                            selectedFactId === fact.id
                                        }
                                        onClick={() =>
                                            handleFactClick(fact.id)
                                        }
                                    />
                                </div>
                            ))}
                        </div>
                    )
                })
            }

            {
                unlinkedFacts.length > 0 && (
                    <div className="cause-tree-graph__unlinked">
                        <h3>
                            {t('accident.causeTree.unlinkedTitle')}
                        </h3>

                        <div className="cause-tree-graph__unlinked-list">
                            {unlinkedFacts.map((fact) => (
                                <div
                                    key={fact.id}
                                    data-fact-id={fact.id}
                                >
                                    <CauseFactCard
                                        description={fact.description}
                                        factType={fact.fact_type}
                                        isTerminal={fact.is_terminal}
                                        level={null}
                                        isSelected={
                                            selectedFactId === fact.id
                                        }
                                        onClick={() =>
                                            handleFactClick(fact.id)
                                        }
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                )
            }
        </div>
    )
}


export default CauseTreeGraph