import type {
    ActionPriority,
} from '../actionTypes'

import { act } from '../i18n/actionI18n'


// ========================================================
// PROPRIÉTÉS
// ========================================================

type ActionPriorityBadgeProps = {
    priority: ActionPriority
}


// ========================================================
// LIBELLÉS
// ========================================================

const PRIORITY_KEYS: Record<
    ActionPriority,
    string
> = {
    LOW: 'priority.low',
    MEDIUM: 'priority.medium',
    HIGH: 'priority.high',
}


// ========================================================
// COMPOSANT
// ========================================================

export default function ActionPriorityBadge({
    priority,
}: ActionPriorityBadgeProps) {
    return (
        <span
            className={
                `action-badge action-priority-badge ` +
                `action-priority-badge--${priority.toLowerCase()}`
            }
        >
            {act(PRIORITY_KEYS[priority])}
        </span>
    )
}