import { at } from './accidentI18n'
import './AccidentAnalysisSection.css'

import {
    useEffect,
    useState,
} from 'react'
import { API_BASE_URL } from './accidentApi'

import AccidentClassificationSection from './AccidentClassificationSection'
import AccidentHeepoSection from './AccidentHeepoSection'
import AccidentJustCultureSection from './AccidentJustCultureSection'
import AccidentClassificationCard from './AccidentClassificationCard'


type AccidentAnalysisSectionProps = {
    eventId: number
    onOpenCauseTree: () => void
    onOpenHeepo: () => void
    onOpenJustCulture: () => void
}

function AccidentAnalysisSection({
    eventId,
    onOpenCauseTree,
    onOpenHeepo,
    onOpenJustCulture,
}: AccidentAnalysisSectionProps) {

    // ========================================================
    // ARBRE DES CAUSES — STATUT AUTOMATIQUE
    // ========================================================

    const [causeTreeStatus, setCauseTreeStatus] =
        useState<'TODO' | 'IN_PROGRESS' | 'VALIDATED'>(
            'TODO',
        )

    useEffect(() => {
        let cancelled = false

        const loadCauseTreeStatus = async () => {
            try {
                const response = await fetch(
                    `${API_BASE_URL}/events/${eventId}/cause-tree`,
                )

                if (cancelled) {
                    return
                }

                if (response.status === 404) {
                    setCauseTreeStatus('TODO')
                    return
                }

                if (!response.ok) {
                    return
                }

                const data = await response.json()

                const facts = Array.isArray(data.facts)
                    ? data.facts
                    : []

                const relations = Array.isArray(data.relations)
                    ? data.relations
                    : []

                if (facts.length === 0) {
                    setCauseTreeStatus('TODO')
                    return
                }

                /*
                 * Une extrémité de branche est une CAUSE
                 * qui ne possède aucune cause en amont.
                 */
                const branchEnds = facts.filter(
                    (fact: {
                        id: number
                        fact_type: string
                        is_terminal: boolean
                    }) =>
                        fact.fact_type === 'CAUSE' &&
                        !relations.some(
                            (relation: {
                                effect_fact_id: number
                            }) =>
                                relation.effect_fact_id ===
                                fact.id,
                        ),
                )

                /*
                 * L'arbre est validé uniquement lorsque
                 * toutes ses extrémités sont fermées.
                 */
                const allBranchesClosed =
                    branchEnds.length > 0 &&
                    branchEnds.every(
                        (fact: {
                            is_terminal: boolean
                        }) => fact.is_terminal,
                    )

                setCauseTreeStatus(
                    allBranchesClosed
                        ? 'VALIDATED'
                        : 'IN_PROGRESS',
                )
            } catch {
                // On conserve le dernier état connu.
            }
        }

        void loadCauseTreeStatus()

        return () => {
            cancelled = true
        }
    }, [eventId])

    const [classificationOpen, setClassificationOpen] =
        useState(false)

    return (
        <section className="accident-dossier__section">
            <h2>{at('analysis.title')}</h2>

            <div className="accident-dossier__analysis-grid">

                <AccidentClassificationCard
                    eventId={eventId}
                    onOpen={() =>
                        setClassificationOpen((current) => !current)
                    }
                />
                <AccidentHeepoSection
                    eventId={eventId}
                    onOpen={onOpenHeepo}
                />

                <AccidentJustCultureSection
                    eventId={eventId}
                    onOpen={onOpenJustCulture}
                />

                <button
                    type="button"
                    className="accident-dossier__analysis-card accident-dossier__analysis-card--cause-tree"
                    onClick={onOpenCauseTree}
                >
                    <div className="accident-dossier__analysis-card-header">
                        <strong>{at('causeTree.title')}</strong>

                        <span
                            className={
                                `accident-dossier__analysis-status ` +
                                `accident-dossier__analysis-status--${causeTreeStatus.toLowerCase()}`
                            }
                        >
                            {causeTreeStatus === 'VALIDATED'
                                ? at('analysis.statusValidated')
                                : causeTreeStatus === 'IN_PROGRESS'
                                    ? at('analysis.statusInProgress')
                                    : at('analysis.statusTodo')}
                        </span>
                    </div>

                    <span>
                        {at('analysis.causeTreeDesc')}
                    </span>
                </button>
            </div>

            <AccidentClassificationSection
                eventId={eventId}
                open={classificationOpen}
            />
        </section>
    )
}

export default AccidentAnalysisSection
