import type {
    RiskyAction,
} from '../actionTypes'

import { act } from '../i18n/actionI18n'

import ActionPriorityBadge from './ActionPriorityBadge'
import ActionStatusBadge from './ActionStatusBadge'


// ========================================================
// PROPRIÉTÉS
// ========================================================

type ActionTableProps = {
    actions: RiskyAction[]
    showOrigin?: boolean
    showStatus?: boolean
    onOpenEvent?: (eventId: number) => void
}


// ========================================================
// LIBELLÉS
// ========================================================

function getScopeLabel(
    scope: RiskyAction['scope'],
): string {
    return act(
        scope === 'GLOBAL'
            ? 'scope.global'
            : 'scope.local',
    )
}


function getOriginLabel(
    origin: RiskyAction['origin_type'],
): string {
    const keys = {
        ACCIDENT: 'origin.accident',
        INCIDENT: 'origin.incident',
        NEAR_MISS: 'origin.nearMiss',
        ILT: 'origin.ilt',
        STOP: 'origin.stop',
        CPPT: 'origin.cppt',
        PAA: 'origin.paa',
        PGA: 'origin.pga',
        QUALITY: 'origin.quality',
        OTHER: 'origin.other',
    } as const

    return act(keys[origin])
}


// ========================================================
// TABLEAU DES ACTIONS
// ========================================================

export default function ActionTable({
    actions,
    showOrigin = true,
    showStatus = true,
    onOpenEvent,
}: ActionTableProps) {

    if (actions.length === 0) {
        return (
            <div className="action-table__empty">
                {act('messages.empty')}
            </div>
        )
    }

    return (
        <div className="action-table__wrapper">
            <table className="action-table">

                {/* =================================================
                    EN-TÊTE
                    ================================================= */}

                <thead>
                    <tr>
                        <th className="action-table__action">
                            {act('columns.action')}
                        </th>

                        <th className="action-table__reference">
                            {act('columns.reference')}
                        </th>

                        {showOrigin && (
                            <th className="action-table__origin">
                                {act('columns.origin')}
                            </th>
                        )}

                        <th className="action-table__scope">
                            {act('columns.scope')}
                        </th>

                        <th className="action-table__responsible">
                            {act('columns.responsible')}
                        </th>

                        <th className="action-table__due-date">
                            {act('columns.dueDate')}
                        </th>

                        <th className="action-table__priority">
                            {act('columns.priority')}
                        </th>

                        {showStatus && (
                            <th className="action-table__status">
                                {act('columns.status')}
                            </th>
                        )}

                        <th className="action-table__progress">
                            {act('columns.progress')}
                        </th>
                    </tr>
                </thead>


                {/* =================================================
                    ACTIONS
                    ================================================= */}

                <tbody>
                    {actions.map((action) => (
                        <tr key={action.id}>

                            <td className="action-table__action action-table__description">
                                {action.description}
                            </td>

                            <td className="action-table__reference">
                                {action.origin_reference &&
                                    action.event_id !== null &&
                                    onOpenEvent ? (
                                    <button
                                        type="button"
                                        className="action-table__reference-button"
                                        onClick={() =>
                                            onOpenEvent(action.event_id!)
                                        }
                                    >
                                        {action.origin_reference}
                                    </button>
                                ) : (
                                    action.origin_reference ?? '—'
                                )}
                            </td>

                            {showOrigin && (
                                <td className="action-table__origin">
                                    {getOriginLabel(
                                        action.origin_type,
                                    )}
                                </td>
                            )}

                            <td className="action-table__scope">
                                {getScopeLabel(
                                    action.scope,
                                )}
                            </td>

                            <td className="action-table__responsible">
                                {action.responsible_text ?? '—'}
                            </td>

                            <td className="action-table__due-date">
                                {action.due_date ?? '—'}
                            </td>

                            <td className="action-table__priority">
                                <ActionPriorityBadge
                                    priority={action.priority}
                                />
                            </td>

                            {showStatus && (
                                <td className="action-table__status">
                                    <ActionStatusBadge
                                        status={action.status}
                                    />
                                </td>
                            )}

                            <td className="action-table__progress">
                                {action.progress_percent !== null
                                    ? `${action.progress_percent}%`
                                    : action.scope === 'GLOBAL'
                                        ? act(
                                            'progress.qualityFollowUp',
                                        )
                                        : '—'}
                            </td>

                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}