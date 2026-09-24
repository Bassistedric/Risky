import { useState } from 'react'
import type { FormEvent } from 'react'

import { API_BASE_URL } from './accidentApi'
import { at } from './accidentI18n'


// ========================================================
// TYPES
// ========================================================

export type AccidentAction = {
    id: number
    origin_type: string
    event_id: number | null
    description: string
    action_type: string
    scope: string
    process_code: string | null
    responsible_person_id: number | null
    responsible_text: string | null
    due_date: string | null
    priority: string
    status: string
    progress_percent: number | null
    resources: string | null
    follow_up_indicator: string | null
}

type AccidentActionFormProps = {
    eventId: number
    action?: AccidentAction | null
    onSaved: () => void
    onCancel: () => void
}


// ========================================================
// COMPOSANT
// ========================================================

function AccidentActionForm({
    eventId,
    action,
    onSaved,
    onCancel,
}: AccidentActionFormProps) {

    const [description, setDescription] = useState(
        action?.description ?? '',
    )

    const [actionType, setActionType] = useState(
        action?.action_type ?? 'CORRECTIVE',
    )

    const [scope, setScope] = useState(
        action?.scope ?? 'LOCAL',
    )

    const [processCode, setProcessCode] = useState(
        action?.process_code ?? 'PR01',
    )

    const [responsibleText, setResponsibleText] = useState(
        action?.responsible_text ?? '',
    )

    const [dueDate, setDueDate] = useState(
        action?.due_date ?? '',
    )

    const [priority, setPriority] = useState(
        action?.priority ?? 'MEDIUM',
    )

    const [progressPercent, setProgressPercent] = useState(
        action?.progress_percent ?? 0,
    )

    const [resources, setResources] = useState(
        action?.resources ?? '',
    )

    const [followUpIndicator, setFollowUpIndicator] = useState(
        action?.follow_up_indicator ?? '',
    )

    const [saving, setSaving] = useState(false)
    const [error, setError] = useState<string | null>(null)


    // ====================================================
    // ENREGISTREMENT
    // ====================================================

    async function handleSubmit(
        event: FormEvent<HTMLFormElement>,
    ) {
        event.preventDefault()

        if (!description.trim()) {
            setError(
                at('measures.form.actionRequired'),
            )
            return
        }

        setSaving(true)
        setError(null)

        try {
            const token = sessionStorage.getItem(
                'risky_session_token',
            )

            const response = await fetch(
                action
                    ? `${API_BASE_URL}/events/${eventId}/actions/${action.id}`
                    : `${API_BASE_URL}/events/${eventId}/actions`,
                {
                    method: action ? 'PUT' : 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token
                            ? {
                                'X-Session-Token': token,
                            }
                            : {}),
                    },
                    body: JSON.stringify({
                        description: description.trim(),
                        action_type: actionType,
                        scope,
                        process_code:
                            scope === 'GLOBAL'
                                ? processCode
                                : null,
                        responsible_person_id: null,
                        responsible_text:
                            responsibleText.trim() || null,
                        due_date: dueDate || null,
                        priority,
                        progress_percent:
                            scope === 'LOCAL'
                                ? progressPercent
                                : null,
                        resources:
                            resources.trim() || null,
                        follow_up_indicator:
                            followUpIndicator.trim() || null,
                    }),
                },
            )

            if (!response.ok) {
                const data = await response.json()

                throw new Error(
                    data.detail ||
                    at('measures.form.saveError'),
                )
            }

            onSaved()
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : at('measures.form.saveError'),
            )
        } finally {
            setSaving(false)
        }
    }


    // ====================================================
    // AFFICHAGE
    // ====================================================

    return (
        <form
            className="accident-action-form"
            onSubmit={handleSubmit}
        >
            <div className="accident-action-form__heading">
                <strong>
                    {action
                        ? at('measures.editAction')
                        : at('measures.newAction')}
                </strong>
            </div>

            <div className="accident-action-form__field accident-action-form__field--full">
                <label htmlFor="action-description">
                    {at('measures.form.action')} *
                </label>

                <textarea
                    id="action-description"
                    rows={2}
                    value={description}
                    onChange={(event) =>
                        setDescription(event.target.value)
                    }
                    placeholder={at(
                        'measures.form.descriptionPlaceholder',
                    )}
                />
            </div>

            <div className="accident-action-form__grid">
                <div className="accident-action-form__field">
                    <label htmlFor="action-type">
                        {at('measures.form.type')}
                    </label>

                    <select
                        id="action-type"
                        value={actionType}
                        onChange={(event) =>
                            setActionType(event.target.value)
                        }
                    >
                        <option value="CORRECTIVE">
                            {at('measures.types.corrective')}
                        </option>

                        <option value="PREVENTIVE">
                            {at('measures.types.preventive')}
                        </option>
                    </select>
                </div>

                <div className="accident-action-form__field">
                    <label htmlFor="action-scope">
                        {at('measures.form.scope')}
                    </label>

                    <select
                        id="action-scope"
                        value={scope}
                        onChange={(event) =>
                            setScope(event.target.value)
                        }
                    >
                        <option value="LOCAL">
                            {at('measures.scopes.local')}
                        </option>

                        <option value="GLOBAL">
                            {at('measures.scopes.global')}
                        </option>
                    </select>
                </div>

                {scope === 'GLOBAL' && (
                    <div className="accident-action-form__field">
                        <label htmlFor="action-process">
                            {at('measures.form.process')} *
                        </label>

                        <select
                            id="action-process"
                            value={processCode}
                            onChange={(event) =>
                                setProcessCode(event.target.value)
                            }
                        >
                            {Array.from(
                                { length: 8 },
                                (_, index) => {
                                    const code = `PR${String(
                                        index + 1,
                                    ).padStart(2, '0')}`

                                    return (
                                        <option
                                            key={code}
                                            value={code}
                                        >
                                            {code}
                                        </option>
                                    )
                                },
                            )}
                        </select>
                    </div>
                )}

                <div className="accident-action-form__field">
                    <label htmlFor="action-responsible">
                        {at('measures.form.responsible')}
                    </label>

                    <input
                        id="action-responsible"
                        type="text"
                        value={responsibleText}
                        onChange={(event) =>
                            setResponsibleText(
                                event.target.value,
                            )
                        }
                        placeholder={at(
                            'measures.form.responsiblePlaceholder',
                        )}
                    />
                </div>

                <div className="accident-action-form__field">
                    <label htmlFor="action-due-date">
                        {at('measures.form.dueDate')}
                    </label>

                    <input
                        id="action-due-date"
                        type="date"
                        value={dueDate}
                        onChange={(event) =>
                            setDueDate(event.target.value)
                        }
                    />
                </div>

                <div className="accident-action-form__field">
                    <label htmlFor="action-priority">
                        {at('measures.form.priority')}
                    </label>

                    <select
                        id="action-priority"
                        className={
                            `accident-action-form__priority ` +
                            `accident-action-form__priority--${priority.toLowerCase()}`
                        }
                        value={priority}
                        onChange={(event) =>
                            setPriority(event.target.value)
                        }
                    >
                        <option value="LOW">
                            {at('measures.priorities.low')}
                        </option>

                        <option value="MEDIUM">
                            {at('measures.priorities.medium')}
                        </option>

                        <option value="HIGH">
                            {at('measures.priorities.high')}
                        </option>
                    </select>
                </div>

                {scope === 'LOCAL' && (
                    <div className="accident-action-form__field">
                        <label htmlFor="action-progress">
                            {at('measures.form.progress')}
                        </label>

                        <div className="accident-action-form__progress">
                            <input
                                id="action-progress"
                                type="range"
                                min="0"
                                max="100"
                                step="5"
                                value={progressPercent}
                                onChange={(event) =>
                                    setProgressPercent(
                                        Number(
                                            event.target.value,
                                        ),
                                    )
                                }
                            />

                            <strong>
                                {progressPercent} %
                            </strong>
                        </div>
                    </div>
                )}
            </div>

            <details className="accident-action-form__details">
                <summary>
                    {at(
                        'measures.form.additionalInformation',
                    )}
                </summary>

                <div className="accident-action-form__details-grid">
                    <div className="accident-action-form__field">
                        <label htmlFor="action-resources">
                            {at('measures.form.resources')}
                        </label>

                        <textarea
                            id="action-resources"
                            rows={2}
                            value={resources}
                            onChange={(event) =>
                                setResources(event.target.value)
                            }
                        />
                    </div>

                    <div className="accident-action-form__field">
                        <label htmlFor="action-indicator">
                            {at(
                                'measures.form.followUpIndicator',
                            )}
                        </label>

                        <textarea
                            id="action-indicator"
                            rows={2}
                            value={followUpIndicator}
                            onChange={(event) =>
                                setFollowUpIndicator(
                                    event.target.value,
                                )
                            }
                        />
                    </div>
                </div>
            </details>

            {error && (
                <p className="accident-action-form__error">
                    {error}
                </p>
            )}

            <div className="accident-action-form__actions">
                <button
                    type="button"
                    className="accident-action-form__cancel"
                    onClick={onCancel}
                    disabled={saving}
                >
                    {at('common.cancel')}
                </button>

                <button
                    type="submit"
                    className="accident-action-form__save"
                    disabled={saving}
                >
                    {saving
                        ? at('measures.form.saving')
                        : action
                            ? at(
                                'measures.form.saveChanges',
                            )
                            : at('measures.form.save')}
                </button>
            </div>
        </form>
    )
}

export default AccidentActionForm