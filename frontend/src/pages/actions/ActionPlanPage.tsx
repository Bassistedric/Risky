import {
    useEffect,
    useState,
} from 'react'

import { getActions } from './actionApi'
import type { RiskyAction } from './actionTypes'
import ActionTable from './components/ActionTable'
import { act } from './i18n/actionI18n'

import './ActionPlanPage.css'


// ========================================================
// TYPES
// ========================================================

type ActionPlanTab =
    | 'overview'
    | 'accidents'
    | 'paa'
    | 'pga'
    | 'cppt'
    | 'quality'

type ActionPlanPageProps = {
    onOpenEvent?: (eventId: number) => void
}
// ========================================================
// ONGLETS
// ========================================================

const ACTION_PLAN_TABS: ActionPlanTab[] = [
    'overview',
    'accidents',
    'paa',
    'pga',
    'cppt',
    'quality',
]


// ========================================================
// COMPOSANT
// ========================================================

function ActionPlanPage({
    onOpenEvent,
}: ActionPlanPageProps) {
    const [activeTab, setActiveTab] =
        useState<ActionPlanTab>('overview')

    const [accidentActions, setAccidentActions] =
        useState<RiskyAction[]>([])

    const [accidentActionsLoading, setAccidentActionsLoading] =
        useState(false)

    const [accidentActionsError, setAccidentActionsError] =
        useState(false)


    // ====================================================
    // CHARGEMENT DES ACTIONS ACCIDENT
    // ====================================================

    useEffect(() => {
        if (activeTab !== 'accidents') {
            return
        }

        let cancelled = false

        async function loadAccidentActions() {
            setAccidentActionsLoading(true)
            setAccidentActionsError(false)

            try {
                const actions =
                    await getActions('ACCIDENT')

                if (!cancelled) {
                    setAccidentActions(actions)
                }
            } catch {
                if (!cancelled) {
                    setAccidentActionsError(true)
                }
            } finally {
                if (!cancelled) {
                    setAccidentActionsLoading(false)
                }
            }
        }

        loadAccidentActions()

        return () => {
            cancelled = true
        }
    }, [activeTab])


    // ====================================================
    // CONTENU DE L'ONGLET ACTIF
    // ====================================================

    function renderTabContent() {
        // ------------------------------------------------
        // ACCIDENTS
        // ------------------------------------------------

        if (activeTab === 'accidents') {
            if (accidentActionsLoading) {
                return (
                    <div className="action-plan__empty">
                        <span>
                            {act('messages.loading')}
                        </span>
                    </div>
                )
            }

            if (accidentActionsError) {
                return (
                    <div className="action-plan__empty">
                        <span>
                            {act('messages.loadError')}
                        </span>
                    </div>
                )
            }

            return (
                <ActionTable
                    actions={accidentActions}
                    showOrigin={false}
                    showStatus={false}
                    onOpenEvent={onOpenEvent}
                />
            )
        }

        // ------------------------------------------------
        // AUTRES ONGLETS
        // ------------------------------------------------

        return (
            <div className="action-plan__empty">
                <strong>
                    {act(`tabs.${activeTab}`)}
                </strong>

                <span>
                    {act('messages.empty')}
                </span>
            </div>
        )
    }


    // ====================================================
    // AFFICHAGE
    // ====================================================

    return (
        <section className="action-plan">

            {/* ====================================================
                EN-TÊTE
                ==================================================== */}

            <div className="action-plan__header">
                <div>
                    <h2>
                        {act('page.title')}
                    </h2>

                    <p>
                        {act('page.description')}
                    </p>
                </div>
            </div>


            {/* ====================================================
                ONGLETS
                ==================================================== */}

            <nav
                className="action-plan__tabs"
                aria-label={act('page.title')}
            >
                {ACTION_PLAN_TABS.map((tab) => (
                    <button
                        key={tab}
                        type="button"
                        className={
                            activeTab === tab
                                ? 'action-plan__tab action-plan__tab--active'
                                : 'action-plan__tab'
                        }
                        onClick={() =>
                            setActiveTab(tab)
                        }
                    >
                        {act(`tabs.${tab}`)}
                    </button>
                ))}
            </nav>


            {/* ====================================================
                CONTENU
                ==================================================== */}

            <div className="action-plan__content">
                {renderTabContent()}
            </div>

        </section>
    )
}

export default ActionPlanPage