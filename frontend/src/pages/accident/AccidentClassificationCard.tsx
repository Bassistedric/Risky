import { at } from './accidentI18n'
import './AccidentAnalysisSection.css'

import {
    useEffect,
    useState,
} from 'react'

import { API_BASE_URL } from './accidentApi'


type AccidentClassificationCardProps = {
    eventId: number
    onOpen: () => void
}

function AccidentClassificationCard({
    eventId,
    onOpen,
}: AccidentClassificationCardProps) {

    const [validated, setValidated] =
        useState(false)

    useEffect(() => {
        let cancelled = false

        const loadStatus = async () => {
            try {
                const response = await fetch(
                    `${API_BASE_URL}/events/${eventId}/classification`,
                )

                if (cancelled) {
                    return
                }

                if (response.status === 404) {
                    setValidated(false)
                    return
                }

                if (!response.ok) {
                    return
                }

                setValidated(true)
            } catch {
                // On conserve le dernier état connu.
            }
        }

        void loadStatus()

        return () => {
            cancelled = true
        }
    }, [eventId])

    return (
        <button
            type="button"
            className="accident-dossier__analysis-card accident-dossier__analysis-card--classification"
            onClick={onOpen}
        >
            <div className="accident-dossier__analysis-card-header">
                <strong>{at('classification.title')}</strong>

                <span
                    className={
                        validated
                            ? 'accident-dossier__analysis-status accident-dossier__analysis-status--validated'
                            : 'accident-dossier__analysis-status accident-dossier__analysis-status--todo'
                    }
                >
                    {validated
                        ? at('analysis.statusValidated')
                        : at('analysis.statusTodo')}
                </span>
            </div>

            <span>
                {at('analysis.classificationDesc')}
            </span>
        </button>
    )
}

export default AccidentClassificationCard