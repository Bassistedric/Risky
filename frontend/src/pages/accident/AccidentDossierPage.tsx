import { at } from './accidentI18n'
import {
    useCallback,
    useEffect,
    useState,
} from 'react'

import './AccidentDossierPage.css'
import './AccidentShared.css'

import AccidentAnalysisSection from './AccidentAnalysisSection'
import AccidentCircumstantialSection from './AccidentCircumstantialSection'
import AccidentFactsSection from './AccidentFactsSection'
import AccidentMeasuresSection from './AccidentMeasuresSection'
import AccidentOverviewSection from './AccidentOverviewSection'
import { API_BASE_URL } from './accidentApi'
import type { EventDetail } from './accidentTypes'
import AccidentPhotosSection from './photos/AccidentPhotosSection'
import AccidentReportsSection from './reports/AccidentReportsSection'
import AccidentReportPreview from './reports/AccidentReportPreview'

type AccidentDossierPageProps = {
    eventId: number
    onBack?: () => void
    onOpenCauseTree: () => void
    onOpenHeepo: () => void
    onOpenJustCulture: () => void
}

function AccidentDossierPage({
    eventId,
    onBack,
    onOpenCauseTree,
    onOpenHeepo,
    onOpenJustCulture,

}: AccidentDossierPageProps) {
    const [event, setEvent] =
        useState<EventDetail | null>(null)

    const [error, setError] =
        useState<string | null>(null)

    const [isLoading, setIsLoading] =
        useState(true)

    const [showDeleteConfirm, setShowDeleteConfirm] =
        useState(false)

    const [isDeleting, setIsDeleting] =
        useState(false)

    const [deleteError, setDeleteError] =
        useState<string | null>(null)

    const [showFinalDeleteConfirm, setShowFinalDeleteConfirm] =
        useState(false)

    const [isUpdatingStatus, setIsUpdatingStatus] =
        useState(false)

    const [statusError, setStatusError] =
        useState<string | null>(null)

    const [isEditingTitle, setIsEditingTitle] = useState(false)
    const [titleDraft, setTitleDraft] = useState('')
    const [isSavingTitle, setIsSavingTitle] = useState(false)
    const [titleError, setTitleError] = useState<string | null>(null)

    /* ========================================================
   APERÇU RAPPORT
   ======================================================== */

    const [showReportPreview, setShowReportPreview] =
        useState(false)

    const loadEvent = useCallback(async () => {
        try {
            setIsLoading(true)
            setError(null)

            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}`,
            )

            if (!response.ok) {
                throw new Error(
                    at('dossier.loadError'),
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
                    at('dossier.loadUnexpected'),
                )
            }
        } finally {
            setIsLoading(false)
        }
    }, [eventId])

    useEffect(() => {
        void loadEvent()
    }, [loadEvent])

    const deleteEvent = async () => {
        try {
            setIsDeleting(true)
            setDeleteError(null)

            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}`,
                {
                    method: 'DELETE',
                    headers: {
                        'X-Session-Token':
                            sessionStorage.getItem(
                                'risky_session_token',
                            ) ?? '',
                    },
                },
            )

            if (!response.ok) {
                throw new Error(
                    at('dossier.delete.error'),
                )
            }

            setShowDeleteConfirm(false)

            onBack?.()
        } catch {
            setDeleteError(
                at('dossier.delete.error'),
            )
        } finally {
            setIsDeleting(false)
        }
    }

    const updateStatus = async (
        newStatus: string,
    ) => {
        if (!event || newStatus === event.status) {
            return
        }

        const token = sessionStorage.getItem(
            'risky_session_token',
        )

        if (!token) {
            setStatusError(
                at('dossier.status.sessionRequired'),
            )
            return
        }

        try {
            setIsUpdatingStatus(true)
            setStatusError(null)

            const response = await fetch(
                `${API_BASE_URL}/events/${event.id}`,
                {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-Token': token,
                    },
                    body: JSON.stringify({
                        status: newStatus,
                    }),
                },
            )

            if (!response.ok) {
                throw new Error(
                    at('dossier.status.updateError'),
                )
            }

            await loadEvent()
        } catch {
            setStatusError(
                at('dossier.status.updateError'),
            )
        } finally {
            setIsUpdatingStatus(false)
        }
    }
    const saveTitle = async () => {
        if (!event) return
        const description = titleDraft.trim()
        if (!description) {
            setTitleError(at('dossier.editTitle.required'))
            return
        }
        const token = sessionStorage.getItem('risky_session_token')
        if (!token) {
            setTitleError(at('dossier.editTitle.sessionRequired'))
            return
        }
        try {
            setIsSavingTitle(true)
            setTitleError(null)
            const response = await fetch(
                `${API_BASE_URL}/events/${event.id}`,
                {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-Token': token,
                    },
                    body: JSON.stringify({ description }),
                },
            )
            if (!response.ok) throw new Error()
            await loadEvent()
            setIsEditingTitle(false)
        } catch {
            setTitleError(at('dossier.editTitle.updateError'))
        } finally {
            setIsSavingTitle(false)
        }
    }

    /* ========================================================
       APERÇU RAPPORT
       ======================================================== */

    if (showReportPreview) {
        return (
            <AccidentReportPreview
                eventId={eventId}
                onBack={() => {
                    setShowReportPreview(false)
                }}
            />
        )
    }
    if (isLoading) {
        return (
            <div>
                {at('dossier.loading')}
            </div>
        )
    }

    if (error) {
        return (
            <div>
                {error}
            </div>
        )
    }

    if (!event) {
        return (
            <div>
                {at('dossier.notFound')}
            </div>
        )
    }

    return (
        <div>
            {onBack && (
                <button
                    className="accident-dossier-back"
                    type="button"
                    onClick={onBack}
                >
                    <span aria-hidden="true">←</span>
                    {at('create.back')}
                </button>
            )}

            <div className="accident-dossier">
                <div className="accident-dossier__header">
                    <div>
                        <span className="accident-dossier__number">
                            {event.event_number}
                        </span>

                        <h1>{at('dossier.title')}</h1>

                        <div className="accident-dossier__title-row">
                            {isEditingTitle ? (
                                <div className="accident-dossier__title-editor">
                                    <input
                                        value={titleDraft}
                                        autoFocus
                                        disabled={isSavingTitle}
                                        onChange={(e) => setTitleDraft(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter') void saveTitle()
                                            if (e.key === 'Escape') {
                                                setIsEditingTitle(false)
                                                setTitleError(null)
                                            }
                                        }}
                                    />
                                    <button type="button" disabled={isSavingTitle} onClick={() => void saveTitle()}>
                                        {at('dossier.editTitle.save')}
                                    </button>
                                    <button type="button" disabled={isSavingTitle} onClick={() => { setIsEditingTitle(false); setTitleError(null) }}>
                                        {at('dossier.editTitle.cancel')}
                                    </button>
                                </div>
                            ) : (
                                <>
                                    <p className="accident-dossier__title">{event.description}</p>
                                    <button
                                        type="button"
                                        className="accident-dossier__title-edit"
                                        title={at('dossier.editTitle.button')}
                                        aria-label={at('dossier.editTitle.button')}
                                        onClick={() => {
                                            setTitleDraft(event.description ?? '')
                                            setTitleError(null)
                                            setIsEditingTitle(true)
                                        }}
                                    >✎</button>
                                </>
                            )}
                        </div>
                        {titleError && <span className="accident-dossier__title-error">{titleError}</span>}
                    </div>

                    <div className="accident-dossier__status-control">
                        <select
                            className={`accident-dossier__status-select accident-dossier__status-select--${event.status.toLowerCase().replace('_', '-')}`}
                            value={event.status}
                            disabled={isUpdatingStatus}
                            onChange={(e) => {
                                void updateStatus(e.target.value)
                            }}
                            aria-label={at('dossier.status.label')}
                        >
                            <option value="OPEN">
                                {at('dossier.status.open')}
                            </option>

                            {event.event_type === 'ACCIDENT' ? (
                                <>
                                    <option value="IN_PROGRESS">
                                        {at('dossier.status.inProgress')}
                                    </option>

                                    <option value="ACCEPTED">
                                        {at('dossier.status.accepted')}
                                    </option>

                                    <option value="REJECTED">
                                        {at('dossier.status.rejected')}
                                    </option>
                                </>
                            ) : (
                                <option value="CLOSED">
                                    {at('dossier.status.closed')}
                                </option>
                            )}
                        </select>

                        {statusError && (
                            <span className="accident-dossier__status-error">
                                {statusError}
                            </span>
                        )}
                    </div>

                </div>

                <AccidentOverviewSection
                    event={event}
                    onEventUpdated={loadEvent}
                />

                {/* ========================================================
    RELATION DES FAITS
    ======================================================== */}

                <AccidentFactsSection
                    eventId={eventId}
                />


                <AccidentCircumstantialSection eventId={eventId} mode="details" />

                {/* ========================================================
    PHOTOS
    ======================================================== */}

                <AccidentPhotosSection
                    eventId={eventId}
                />


                {/* ========================================================
    ANALYSES DE L'ÉVÉNEMENT
    ======================================================== */}

                <AccidentAnalysisSection
                    eventId={eventId}
                    onOpenCauseTree={onOpenCauseTree}
                    onOpenHeepo={onOpenHeepo}
                    onOpenJustCulture={onOpenJustCulture}
                />

                <AccidentMeasuresSection eventId={eventId} />

                {/* ========================================================
    DOCUMENTS & RAPPORTS
    ======================================================== */}

                <AccidentReportsSection
                    onOpenAnalysisReport={() => {
                        setShowReportPreview(true)
                    }}
                />

                <div className="accident-dossier__danger-zone">
                    {!showDeleteConfirm ? (
                        <button
                            type="button"
                            className="accident-dossier__delete-button"
                            onClick={() => {
                                setDeleteError(null)
                                setShowDeleteConfirm(true)
                            }}
                        >
                            {at('dossier.delete.button')}
                        </button>
                    ) : (
                        <div className="accident-dossier__delete-confirm">
                            <div>
                                <strong>
                                    {at('dossier.delete.title')}
                                </strong>

                                <p>
                                    {at(
                                        'dossier.delete.message',
                                        {
                                            eventNumber:
                                                event.event_number,
                                        },
                                    )}
                                </p>

                                <p className="accident-dossier__delete-warning">
                                    {at('dossier.delete.warning')}
                                </p>

                                {deleteError && (
                                    <p className="accident-dossier__delete-error">
                                        {deleteError}
                                    </p>
                                )}
                            </div>

                            <div className="accident-dossier__delete-actions">
                                <button
                                    type="button"
                                    disabled={isDeleting}
                                    onClick={() => {
                                        setShowDeleteConfirm(false)
                                        setDeleteError(null)
                                    }}
                                >
                                    {at('common.cancel')}
                                </button>

                                <button
                                    type="button"
                                    className="accident-dossier__delete-button"
                                    disabled={isDeleting}
                                    onClick={() => {
                                        setShowFinalDeleteConfirm(true)
                                    }}
                                >
                                    {isDeleting
                                        ? at('dossier.delete.deleting')
                                        : at(
                                            'dossier.delete.confirm',
                                        )}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
            {showFinalDeleteConfirm && (
                <div
                    className="accident-delete-modal__overlay"
                    role="presentation"
                >
                    <div
                        className="accident-delete-modal"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="delete-event-title"
                    >
                        <div className="accident-delete-modal__icon">
                            !
                        </div>

                        <h2 id="delete-event-title">
                            {at('dossier.delete.finalTitle')}
                        </h2>

                        <p>
                            {at(
                                'dossier.delete.finalConfirmation',
                                {
                                    eventNumber:
                                        event.event_number,
                                },
                            )}
                        </p>

                        <div className="accident-delete-modal__number">
                            {event.event_number}
                        </div>

                        <p className="accident-delete-modal__warning">
                            {at('dossier.delete.warning')}
                        </p>

                        <div className="accident-delete-modal__actions">
                            <button
                                type="button"
                                className="accident-delete-modal__cancel"
                                disabled={isDeleting}
                                onClick={() => {
                                    setShowFinalDeleteConfirm(false)
                                }}
                            >
                                {at('common.cancel')}
                            </button>

                            <button
                                type="button"
                                className="accident-delete-modal__confirm"
                                disabled={isDeleting}
                                onClick={() => {
                                    void deleteEvent()
                                }}
                            >
                                {isDeleting
                                    ? at('dossier.delete.deleting')
                                    : at(
                                        'dossier.delete.finalConfirm',
                                    )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default AccidentDossierPage
