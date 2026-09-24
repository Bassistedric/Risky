import { at } from './accidentI18n'

import {
    useEffect,
    useState,
} from 'react'

import { API_BASE_URL } from './accidentApi'


type AccidentJustCultureSectionProps = {
    eventId: number
    onOpen: () => void
}

type JustCultureStatus =
    | 'TODO'
    | 'IN_PROGRESS'
    | 'VALIDATED'


function AccidentJustCultureSection({
    eventId,
    onOpen,
}: AccidentJustCultureSectionProps) {

    const [status, setStatus] =
        useState<JustCultureStatus>('TODO')

    useEffect(() => {
        let cancelled = false

        const loadStatus = async () => {
            try {
                const response = await fetch(
                    `${API_BASE_URL}/just-culture/events/${eventId}`,
                )

                if (cancelled) {
                    return
                }

                if (response.status === 404) {
                    setStatus('TODO')
                    return
                }

                if (!response.ok) {
                    return
                }

                const data = await response.json()

                setStatus(
                    data.validated
                        ? 'VALIDATED'
                        : 'IN_PROGRESS',
                )
            } catch {
                /*
                 * En cas d'erreur réseau, on conserve
                 * simplement le dernier état connu.
                 */
            }
        }

        void loadStatus()

        return () => {
            cancelled = true
        }
    }, [eventId])

    const statusLabel =
        status === 'VALIDATED'
            ? at('analysis.statusValidated')
            : status === 'IN_PROGRESS'
                ? at('analysis.statusInProgress')
                : at('analysis.statusTodo')

    return (
        <button
            type="button"
            className="accident-dossier__analysis-card accident-dossier__analysis-card--just-culture"
            onClick={onOpen}
        >
            <div className="accident-dossier__analysis-card-header">
                <strong>Just Culture</strong>

                <span
                    className={
                        `accident-dossier__analysis-status ` +
                        `accident-dossier__analysis-status--${status.toLowerCase()}`
                    }
                >
                    {statusLabel}
                </span>
            </div>

            <span>
                {at('analysis.justCultureDesc')}
            </span>
        </button>
    )
}

export default AccidentJustCultureSection