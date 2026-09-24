import type {
    ActionStatus,
} from '../actionTypes'

import { act } from '../i18n/actionI18n'


// ========================================================
// PROPRIÉTÉS
// ========================================================

type ActionStatusBadgeProps = {
    status: ActionStatus
}


// ========================================================
// LIBELLÉS
// ========================================================

const STATUS_KEYS: Record<
    ActionStatus,
    string
> = {
    TODO: 'status.todo',
    IN_PROGRESS: 'status.inProgress',
    DONE: 'status.done',
    TO_VALIDATE: 'status.toValidate',
    CLOSED: 'status.closed',
}


// ========================================================
// COMPOSANT
// ========================================================

export default function ActionStatusBadge({
    status,
}: ActionStatusBadgeProps) {
    return (
        <span
            className={
                `action-badge action-status-badge ` +
                `action-status-badge--${status.toLowerCase()}`
            }
        >
            {act(STATUS_KEYS[status])}
        </span>
    )
}