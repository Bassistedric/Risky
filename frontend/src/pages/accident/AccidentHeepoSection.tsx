import { at } from './accidentI18n'
import './AccidentHeepoSection.css'

import {
    useEffect,
    useState,
} from 'react'

import { API_BASE_URL } from './accidentApi'


type AccidentHeepoSectionProps = {
    eventId: number
    onOpen?: () => void
}

type HeepoStatus =
    | 'TODO'
    | 'VALIDATED'


function AccidentHeepoSection({
    eventId,
    onOpen,
}: AccidentHeepoSectionProps) {

    const [status, setStatus] =
        useState<HeepoStatus>('TODO')

    useEffect(() => {
        let cancelled = false

        const loadStatus = async () => {
            try {
                const response = await fetch(
                    `${API_BASE_URL}/events/${eventId}/heepo`,
                )

                if (cancelled) {
                    return
                }

                if (!response.ok) {
                    return
                }

                const data = await response.json()

                setStatus(
                    Array.isArray(data.items) &&
                        data.items.length > 0
                        ? 'VALIDATED'
                        : 'TODO',
                )
            } catch {
                // On conserve le dernier état connu.
            }
        }

        const handleFocus = () => {
            void loadStatus()
        }

        void loadStatus()

        window.addEventListener(
            'focus',
            handleFocus,
        )

        return () => {
            cancelled = true

            window.removeEventListener(
                'focus',
                handleFocus,
            )
        }
    }, [eventId])

    const statusLabel =
        status === 'VALIDATED'
            ? at('analysis.statusValidated')
            : at('analysis.statusTodo')

    return (
        <button
            type="button"
            className="accident-dossier__analysis-card accident-dossier__analysis-card--heepo"
            onClick={onOpen}
        >
            <div className="accident-dossier__analysis-card-header">
                <strong>HEEPO</strong>

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
                {at('analysis.heepoDesc')}
            </span>
        </button>
    )
}

export default AccidentHeepoSection