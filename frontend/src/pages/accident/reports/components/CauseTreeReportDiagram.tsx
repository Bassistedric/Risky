import {
    useCallback,
    useLayoutEffect,
    useRef,
    useState,
} from 'react'

import './CauseTreeReportDiagram.css'
import { rt } from '../i18n/reportI18n'


// ========================================================
// TYPES
// ========================================================

type ReportCauseFact = {
    id: number
    description: string
    fact_type: string
    sort_order: number
    is_terminal: boolean
    level: number | null
}

type ReportCauseRelation = {
    id: number
    cause_fact_id: number
    effect_fact_id: number
}

type GraphLine = {
    relationId: number
    x1: number
    y1: number
    x2: number
    y2: number
}

type CauseTreeReportDiagramProps = {
    facts: ReportCauseFact[]
    relations: ReportCauseRelation[]
}


// ========================================================
// COMPOSANT
// ========================================================

export default function CauseTreeReportDiagram({
    facts,
    relations,
}: CauseTreeReportDiagramProps) {
    const graphRef =
        useRef<HTMLDivElement | null>(null)

    const [lines, setLines] =
        useState<GraphLine[]>([])


    // ========================================================
    // FAITS RATTACHÉS / NON RATTACHÉS
    // ========================================================

    const linkedFacts = facts.filter(
        (fact) => fact.level !== null,
    )

    const unlinkedFacts = facts.filter(
        (fact) => fact.level === null,
    )


    // ========================================================
    // NIVEAUX
    // ========================================================

    const levels = Array.from(
        new Set(
            linkedFacts.map(
                (fact) => fact.level as number,
            ),
        ),
    ).sort((a, b) => b - a)


    // ========================================================
    // ORDRE DES FAITS PAR NIVEAU
    // ========================================================

    const positionByFactId =
        new Map<number, number>()

    const factsByLevel =
        new Map<number, ReportCauseFact[]>()

    levels
        .slice()
        .sort((a, b) => a - b)
        .forEach((level) => {
            const factsAtLevel =
                linkedFacts.filter(
                    (fact) =>
                        fact.level === level,
                )

            const factsWithBarycenter =
                factsAtLevel.map((fact) => {
                    const effects = relations
                        .filter(
                            (relation) =>
                                relation.cause_fact_id ===
                                fact.id,
                        )
                        .map((relation) =>
                            positionByFactId.get(
                                relation.effect_fact_id,
                            ),
                        )
                        .filter(
                            (
                                position,
                            ): position is number =>
                                position !== undefined,
                        )

                    const barycenter =
                        effects.length > 0
                            ? effects.reduce(
                                (
                                    sum,
                                    position,
                                ) =>
                                    sum +
                                    position,
                                0,
                            ) / effects.length
                            : fact.sort_order

                    return {
                        fact,
                        barycenter,
                    }
                })

            factsWithBarycenter.sort(
                (a, b) => {
                    if (
                        a.barycenter !==
                        b.barycenter
                    ) {
                        return (
                            a.barycenter -
                            b.barycenter
                        )
                    }

                    if (
                        a.fact.sort_order !==
                        b.fact.sort_order
                    ) {
                        return (
                            a.fact.sort_order -
                            b.fact.sort_order
                        )
                    }

                    return (
                        a.fact.id -
                        b.fact.id
                    )
                },
            )

            const orderedFacts =
                factsWithBarycenter.map(
                    (item) => item.fact,
                )

            factsByLevel.set(
                level,
                orderedFacts,
            )

            orderedFacts.forEach(
                (fact, index) => {
                    positionByFactId.set(
                        fact.id,
                        index,
                    )
                },
            )
        })


    // ========================================================
    // CALCUL DES CONNEXIONS
    // ========================================================

    const calculateLines =
        useCallback(() => {
            const graph =
                graphRef.current

            if (!graph) {
                return
            }

            const graphRect =
                graph.getBoundingClientRect()

            const nextLines: GraphLine[] = []

            relations.forEach(
                (relation) => {
                    const causeElement =
                        graph.querySelector<HTMLElement>(
                            `[data-report-fact-id="${relation.cause_fact_id}"]`,
                        )

                    const effectElement =
                        graph.querySelector<HTMLElement>(
                            `[data-report-fact-id="${relation.effect_fact_id}"]`,
                        )

                    if (
                        !causeElement ||
                        !effectElement
                    ) {
                        return
                    }

                    const causeRect =
                        causeElement.getBoundingClientRect()

                    const effectRect =
                        effectElement.getBoundingClientRect()

                    /*
                     * L'arbre est présenté de haut en bas :
                     * causes en haut, fait final en bas.
                     *
                     * La ligne part donc du centre bas
                     * de la cause vers le centre haut
                     * de l'effet.
                     */

                    nextLines.push({
                        relationId:
                            relation.id,

                        x1:
                            causeRect.left -
                            graphRect.left +
                            causeRect.width / 2,

                        y1:
                            causeRect.bottom -
                            graphRect.top,

                        x2:
                            effectRect.left -
                            graphRect.left +
                            effectRect.width / 2,

                        y2:
                            effectRect.top -
                            graphRect.top,
                    })
                },
            )

            setLines(nextLines)
        }, [facts, relations])


    // ========================================================
    // RECALCUL APRÈS RENDU
    // ========================================================

    useLayoutEffect(() => {
        calculateLines()

        const handleResize = () => {
            calculateLines()
        }

        window.addEventListener(
            'resize',
            handleResize,
        )

        return () => {
            window.removeEventListener(
                'resize',
                handleResize,
            )
        }
    }, [calculateLines])


    // ========================================================
    // AFFICHAGE
    // ========================================================

    return (
        <div className="report-cause-tree">
            <div
                ref={graphRef}
                className="report-cause-tree__graph"
            >
                {/* =============================================
                    CONNEXIONS
                ============================================= */}

                <svg
                    className="report-cause-tree__lines"
                    aria-hidden="true"
                >
                    <defs>
                        <marker
                            id="report-cause-tree-arrow"
                            viewBox="0 0 10 10"
                            refX="9"
                            refY="5"
                            markerWidth="6"
                            markerHeight="6"
                            orient="auto-start-reverse"
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
                            markerEnd={
                                'url(#report-cause-tree-arrow)'
                            }
                        />
                    ))}
                </svg>


                {/* =============================================
                    NIVEAUX
                ============================================= */}

                {levels.map((level) => {
                    const factsAtLevel =
                        factsByLevel.get(level) ??
                        []

                    return (
                        <div
                            key={level}
                            className="report-cause-tree__row"
                        >
                            {factsAtLevel.map(
                                (fact) => (
                                    <div
                                        key={fact.id}
                                        className={[
                                            'report-cause-tree__fact',
                                            fact.fact_type ===
                                                'FINAL'
                                                ? 'report-cause-tree__fact--final'
                                                : '',
                                            fact.is_terminal
                                                ? 'report-cause-tree__fact--terminal'
                                                : '',
                                        ]
                                            .filter(
                                                Boolean,
                                            )
                                            .join(' ')}
                                        data-report-fact-id={
                                            fact.id
                                        }
                                    >
                                        <div className="report-cause-tree__fact-type">
                                            {fact.fact_type ===
                                                'FINAL'
                                                ? rt(
                                                    'preview.causeTree.finalFact',
                                                )
                                                : fact.is_terminal
                                                    ? rt(
                                                        'preview.causeTree.terminalCause',
                                                    )
                                                    : rt(
                                                        'preview.causeTree.cause',
                                                    )}
                                        </div>

                                        <div className="report-cause-tree__fact-description">
                                            {
                                                fact.description
                                            }
                                        </div>
                                    </div>
                                ),
                            )}
                        </div>
                    )
                })}
            </div>


            {/* =============================================
                ÉLÉMENTS NON RATTACHÉS
            ============================================= */}

            {unlinkedFacts.length > 0 && (
                <div className="report-cause-tree__unlinked">
                    <div className="report-cause-tree__unlinked-title">
                        {rt(
                            'preview.causeTree.unlinked',
                        )}
                    </div>

                    <div className="report-cause-tree__unlinked-list">
                        {unlinkedFacts.map(
                            (fact) => (
                                <div
                                    key={fact.id}
                                    className="report-cause-tree__fact report-cause-tree__fact--unlinked"
                                >
                                    <div className="report-cause-tree__fact-description">
                                        {
                                            fact.description
                                        }
                                    </div>
                                </div>
                            ),
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}