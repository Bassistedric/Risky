import {
    useCallback,
    useEffect,
    useState,
} from 'react'

import { API_BASE_URL } from './accidentApi'
import { at } from './accidentI18n'
import './AccidentMeasuresSection.css'
import AccidentActionForm from './AccidentActionForm'
import type { AccidentAction } from './AccidentActionForm'


// ========================================================
// TYPES
// ========================================================

type AccidentMeasuresSectionProps = {
    eventId: number
}


// ========================================================
// COMPOSANT
// ========================================================

function AccidentMeasuresSection({
    eventId,
}: AccidentMeasuresSectionProps) {
    const [actions, setActions] = useState<AccidentAction[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [open, setOpen] = useState(true)
    const [adding, setAdding] = useState(false)
    const [editingAction, setEditingAction] =
        useState<AccidentAction | null>(null)


    // ====================================================
    // CHARGEMENT
    // ====================================================

    const loadActions = useCallback(async () => {
        setLoading(true)
        setError(null)

        try {
            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}/actions`,
            )

            if (!response.ok) {
                throw new Error(
                    at('measures.loadError'),
                )
            }

            const data = await response.json()

            setActions(data.actions ?? [])
        } catch {
            setError(
                at('measures.loadError'),
            )
        } finally {
            setLoading(false)
        }
    }, [eventId])

    useEffect(() => {
        void loadActions()
    }, [loadActions])


    // ====================================================
    // AFFICHAGE
    // ====================================================

    return (
        <section className="accident-measures">
            <button
                className="accident-measures__header"
                type="button"
                onClick={() => setOpen((value) => !value)}
            >
                <span className="accident-measures__chevron">
                    {open ? '▾' : '▸'}
                </span>

                <span className="accident-measures__title">
                    {at('measures.title')}
                </span>

                <span className="accident-measures__count">
                    {actions.length}
                </span>
            </button>

            {open && (
                <div className="accident-measures__body">
                    <div className="accident-measures__toolbar">
                        <p>
                            {at('measures.description')}
                        </p>

                        <button
                            className="risky-button"
                            type="button"
                            onClick={() => {
                                setEditingAction(null)
                                setAdding(true)
                            }}
                            disabled={
                                adding ||
                                editingAction !== null
                            }
                        >
                            + {at('measures.addAction')}
                        </button>
                    </div>

                    {(adding || editingAction) && (
                        <AccidentActionForm
                            key={
                                editingAction?.id ?? 'new'
                            }
                            eventId={eventId}
                            action={editingAction}
                            onCancel={() => {
                                setAdding(false)
                                setEditingAction(null)
                            }}
                            onSaved={async () => {
                                setAdding(false)
                                setEditingAction(null)
                                await loadActions()
                            }}
                        />
                    )}

                    {loading && (
                        <p className="accident-measures__message">
                            {at('measures.loading')}
                        </p>
                    )}

                    {!loading && error && (
                        <p className="accident-measures__error">
                            {error}
                        </p>
                    )}

                    {!loading &&
                        !error &&
                        actions.length === 0 && (
                            <p className="accident-measures__message">
                                {at('measures.empty')}
                            </p>
                        )}

                    {!loading &&
                        !error &&
                        actions.length > 0 && (
                            <div className="accident-measures__table-wrap">
                                <table className="accident-measures__table">
                                    <thead>
                                        <tr>
                                            <th>
                                                {at(
                                                    'measures.columns.action',
                                                )}
                                            </th>

                                            <th>
                                                {at(
                                                    'measures.columns.type',
                                                )}
                                            </th>

                                            <th>
                                                {at(
                                                    'measures.columns.scope',
                                                )}
                                            </th>

                                            <th>
                                                {at(
                                                    'measures.columns.responsible',
                                                )}
                                            </th>

                                            <th>
                                                {at(
                                                    'measures.columns.dueDate',
                                                )}
                                            </th>

                                            <th>
                                                {at(
                                                    'measures.columns.priority',
                                                )}
                                            </th>

                                            <th>
                                                {at(
                                                    'measures.columns.followUp',
                                                )}
                                            </th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {actions.map((action) => (
                                            <tr
                                                key={action.id}
                                                className="accident-measures__row"
                                                onClick={() => {
                                                    setAdding(false)
                                                    setEditingAction(
                                                        action,
                                                    )
                                                }}
                                                title={at(
                                                    'measures.editHint',
                                                )}
                                            >
                                                <td>
                                                    {
                                                        action.description
                                                    }
                                                </td>

                                                <td>
                                                    {action.action_type ===
                                                    'CORRECTIVE'
                                                        ? at(
                                                            'measures.types.corrective',
                                                        )
                                                        : at(
                                                            'measures.types.preventive',
                                                        )}
                                                </td>

                                                <td>
                                                    {action.scope ===
                                                    'LOCAL'
                                                        ? at(
                                                            'measures.scopes.local',
                                                        )
                                                        : at(
                                                            'measures.scopes.global',
                                                        )}
                                                </td>

                                                <td>
                                                    {action.responsible_text ||
                                                        '—'}
                                                </td>

                                                <td>
                                                    {action.due_date ||
                                                        '—'}
                                                </td>

                                                <td>
                                                    <span
                                                        className={
                                                            `accident-priority ` +
                                                            `accident-priority--${action.priority.toLowerCase()}`
                                                        }
                                                    >
                                                        <span className="accident-priority__dot" />

                                                        {action.priority ===
                                                        'LOW'
                                                            ? at(
                                                                'measures.priorities.low',
                                                            )
                                                            : action.priority ===
                                                                'HIGH'
                                                              ? at(
                                                                  'measures.priorities.high',
                                                              )
                                                              : at(
                                                                  'measures.priorities.medium',
                                                              )}
                                                    </span>
                                                </td>

                                                <td>
                                                    {action.scope ===
                                                    'GLOBAL'
                                                        ? `${at(
                                                            'measures.followUp9001',
                                                        )} · ${
                                                            action.process_code ??
                                                            '—'
                                                        }`
                                                        : `${
                                                            action.progress_percent ??
                                                            0
                                                        } %`}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                </div>
            )}
        </section>
    )
}

export default AccidentMeasuresSection