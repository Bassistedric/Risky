import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

import { API_BASE_URL } from './accidentApi'
import './JustCulturePage.css'


// ========================================================
// JUST CULTURE — TYPES
// ========================================================

type AvailableAnswer = {
    code: string
    label: string
    label_nl?: string | null
    label_en?: string | null
    label_pl?: string | null
    target_node_code: string
    sort_order: number
}

type HistoryStep = {
    step_order: number
    node_code: string
    question_text: string
    answer_label: string
    question_text_nl: string | null
    question_text_en: string | null
    question_text_pl: string | null

    answer_label_nl: string | null
    answer_label_en: string | null
    answer_label_pl: string | null

    target_node_code: string
}

type JustCultureDetail = {
    event_id: number
    status: string

    current_node_code?: string | null
    current_node_text?: string | null
    current_node_text_nl?: string | null
    current_node_text_en?: string | null
    current_node_text_pl?: string | null

    available_answers: AvailableAnswer[]

    conclusion_code?: string | null
    conclusion_label?: string | null
    conclusion_label_nl?: string | null
    conclusion_label_en?: string | null
    conclusion_label_pl?: string | null

    recommendation_code?: string | null
    recommendation_label?: string | null
    recommendation_label_nl?: string | null
    recommendation_label_en?: string | null
    recommendation_label_pl?: string | null

    validated: boolean
    validated_at: string | null
    validated_by_person_id: number | null

    history: HistoryStep[]
}

type JustCulturePageProps = {
    eventId: number
    onBack: () => void
}


// ========================================================
// JUST CULTURE — PAGE
// ========================================================

function JustCulturePage({
    eventId,
    onBack,
}: JustCulturePageProps) {
    const { t, i18n } = useTranslation()

    const [analysis, setAnalysis] =
        useState<JustCultureDetail | null>(null)

    const [isLoading, setIsLoading] =
        useState(true)

    const [error, setError] =
        useState<string | null>(null)

    const [isSubmitting, setIsSubmitting] =
        useState(false)

    const [busy, setBusy] = useState(false)

    // ========================================================
    // JUST CULTURE — LANGUE
    // ========================================================

    const language =
        i18n.resolvedLanguage ?? i18n.language

    const translatedText = (
        fr?: string | null,
        nl?: string | null,
        en?: string | null,
        pl?: string | null,
    ) => {
        if (language?.startsWith('nl')) {
            return nl || fr || ''
        }

        if (language?.startsWith('en')) {
            return en || fr || ''
        }

        if (language?.startsWith('pl')) {
            return pl || fr || ''
        }

        return fr || ''
    }

    // ========================================================
    // JUST CULTURE — NIVEAU DE RECOMMANDATION
    // ========================================================

    const getRecommendationLevel = (
        recommendationCode?: string | null,
    ) => {
        switch (recommendationCode) {
            case 'ACCOMPAGNEMENT':
                return 'support'

            case 'AVERTISSEMENT_VERBAL':
                return 'verbal'

            case 'PREMIER_AVERTISSEMENT_ECRIT':
                return 'written-first'

            case 'DERNIER_AVERTISSEMENT_ECRIT':
                return 'written-final'

            case 'LICENCIEMENT':
                return 'dismissal'

            default:
                return 'neutral'
        }
    }

    // ========================================================
    // JUST CULTURE — CHARGEMENT
    // ========================================================

    useEffect(() => {
        async function loadAnalysis() {
            try {
                setIsLoading(true)
                setError(null)

                const response = await fetch(
                    `${API_BASE_URL}/just-culture/events/${eventId}`,
                )

                if (response.status === 404) {
                    setAnalysis(null)
                    return
                }

                if (!response.ok) {
                    throw new Error(
                        t('accident.justCulture.loadError'),
                    )
                }

                const data: JustCultureDetail =
                    await response.json()

                setAnalysis(data)
            } catch (error) {
                setError(
                    error instanceof Error
                        ? error.message
                        : t('accident.justCulture.loadError'),
                )
            } finally {
                setIsLoading(false)
            }
        }

        void loadAnalysis()
    }, [eventId])

    // ========================================================
    // JUST CULTURE — DÉMARRAGE
    // ========================================================

    const startAnalysis = async () => {
        const token = sessionStorage.getItem(
            'risky_session_token',
        )

        if (!token) {
            setError(t('accident.justCulture.sessionRequired'))
            return
        }

        try {
            setIsSubmitting(true)
            setError(null)

            const response = await fetch(
                `${API_BASE_URL}/just-culture/events/${eventId}/start`,
                {
                    method: 'POST',
                    headers: {
                        'X-Session-Token': token,
                    },
                },
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail ??
                    t('accident.justCulture.startError'),
                )
            }

            /*
             * L'analyse existe maintenant en DB.
             * On recharge son état officiel complet.
             */
            const detailResponse = await fetch(
                `${API_BASE_URL}/just-culture/events/${eventId}`,
            )

            if (!detailResponse.ok) {
                throw new Error(
                    t('accident.justCulture.loadError'),
                )
            }

            const detail: JustCultureDetail =
                await detailResponse.json()

            setAnalysis(detail)
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : t('accident.justCulture.startError'),
            )
        } finally {
            setIsSubmitting(false)
        }
    }

    // ========================================================
    // JUST CULTURE — RÉPONSE
    // ========================================================

    const answerQuestion = async (
        answerCode: string,
    ) => {
        const token = sessionStorage.getItem(
            'risky_session_token',
        )

        if (!token) {
            setError(t('accident.justCulture.sessionRequired'))
            return
        }

        try {
            setIsSubmitting(true)
            setError(null)

            const response = await fetch(
                `${API_BASE_URL}/just-culture/events/${eventId}/answer`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-Token': token,
                    },
                    body: JSON.stringify({
                        answer_code: answerCode,
                    }),
                },
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail ??
                    t('accident.justCulture.answerError'),
                )
            }

            /*
             * On recharge l'état officiel depuis la DB.
             * Le GET reste ainsi la source de vérité pour
             * la question courante, l'historique et la conclusion.
             */
            const detailResponse = await fetch(
                `${API_BASE_URL}/just-culture/events/${eventId}`,
            )

            if (!detailResponse.ok) {
                throw new Error(
                    t('accident.justCulture.loadError'),
                )
            }

            const detail: JustCultureDetail =
                await detailResponse.json()

            setAnalysis(detail)
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : t('accident.justCulture.answerError'),
            )
        } finally {
            setIsSubmitting(false)
        }
    }

    // ========================================================
    // JUST CULTURE — RETOUR À LA QUESTION PRÉCÉDENTE
    // ========================================================

    const goBackOneQuestion = async () => {
        const token = sessionStorage.getItem('risky_session_token')

        if (!token || busy) {
            return
        }

        setBusy(true)
        setError(null)

        try {
            const response = await fetch(
                `${API_BASE_URL}/just-culture/events/${eventId}/back`,
                {
                    method: 'POST',
                    headers: {
                        'X-Session-Token': token,
                    },
                },
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail ??
                    t('accident.justCulture.backError'),
                )
            }

            // On recharge l'analyse complète après le retour.
            const detailResponse = await fetch(
                `${API_BASE_URL}/just-culture/events/${eventId}`,
            )

            if (!detailResponse.ok) {
                throw new Error(
                    t('accident.justCulture.loadError'),
                )
            }

            const detail: JustCultureDetail =
                await detailResponse.json()

            setAnalysis(detail)
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : t('accident.justCulture.unexpectedError'),
            )
        } finally {
            setBusy(false)
        }
    }

    // ========================================================
    // JUST CULTURE — VALIDATION FINALE
    // ========================================================

    const validateAnalysis = async () => {
        const token = sessionStorage.getItem(
            'risky_session_token',
        )

        if (!token || busy) {
            return
        }

        try {
            setBusy(true)
            setError(null)

            const response = await fetch(
                `${API_BASE_URL}/just-culture/events/${eventId}/validate`,
                {
                    method: 'POST',
                    headers: {
                        'X-Session-Token': token,
                    },
                },
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail ??
                    t('accident.justCulture.validateError'),
                )
            }

            /*
             * Recharge l'état officiel après validation.
             */
            const detailResponse = await fetch(
                `${API_BASE_URL}/just-culture/events/${eventId}`,
            )

            if (!detailResponse.ok) {
                throw new Error(
                    t('accident.justCulture.loadError'),
                )
            }

            const detail: JustCultureDetail =
                await detailResponse.json()

            setAnalysis(detail)
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : t('accident.justCulture.validateError'),
            )
        } finally {
            setBusy(false)
        }
    }

    // ========================================================
    // JUST CULTURE — RÉOUVERTURE APRÈS VALIDATION
    // ========================================================

    const reopenAnalysis = async () => {
        const token = sessionStorage.getItem(
            'risky_session_token',
        )

        if (!token || busy) {
            return
        }

        try {
            setBusy(true)
            setError(null)

            const response = await fetch(
                `${API_BASE_URL}/just-culture/events/${eventId}/reopen`,
                {
                    method: 'POST',
                    headers: {
                        'X-Session-Token': token,
                    },
                },
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail ??
                    t('accident.justCulture.reopenError'),
                )
            }

            const detailResponse = await fetch(
                `${API_BASE_URL}/just-culture/events/${eventId}`,
            )

            if (!detailResponse.ok) {
                throw new Error(
                    t('accident.justCulture.loadError'),
                )
            }

            const detail: JustCultureDetail =
                await detailResponse.json()

            setAnalysis(detail)
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : t('accident.justCulture.reopenError'),
            )
        } finally {
            setBusy(false)
        }
    }

    // ========================================================
    // JUST CULTURE — AFFICHAGE
    // ========================================================

    return (
        <div className="just-culture-page">
            <button
                type="button"
                className="just-culture-page__back risky-back-button"
                onClick={onBack}
            >
                <span aria-hidden="true">←</span>
                {t('accident.justCulture.back')}
            </button>

            <section className="just-culture-page__card">
                <div className="just-culture-page__header">
                    <div>
                        <span className="just-culture-page__eyebrow">
                            {t('accident.justCulture.eyebrow')}
                        </span>

                        <h2>{t('accident.justCulture.title')}</h2>
                    </div>
                </div>

                {isLoading && (
                    <p>{t('accident.justCulture.loading')}</p>
                )}

                {error && (
                    <div className="just-culture-page__error">
                        {error}
                    </div>
                )}

                {!isLoading &&
                    !error &&
                    analysis === null && (
                        <div className="just-culture-page__empty">
                            <strong>
                                {t('accident.justCulture.startTitle')}
                            </strong>

                            <p>
                                {t('accident.justCulture.startDescription')}
                            </p>
                            <button
                                type="button"
                                disabled={isSubmitting}
                                onClick={() => {
                                    void startAnalysis()
                                }}
                            >
                                {isSubmitting
                                    ? t('accident.justCulture.starting')
                                    : t('accident.justCulture.start')}
                            </button>
                        </div>
                    )}

                {!isLoading &&
                    !error &&
                    analysis !== null && (
                        <>
                            {analysis.current_node_text && (
                                <div className="just-culture-page__question">
                                    <span>{t('accident.justCulture.question')}</span>

                                    <strong>
                                        {translatedText(
                                            analysis.current_node_text,
                                            analysis.current_node_text_nl,
                                            analysis.current_node_text_en,
                                            analysis.current_node_text_pl,
                                        )}
                                    </strong>
                                </div>
                            )}

                            {analysis.available_answers.length > 0 && (
                                <div className="just-culture-page__answers">
                                    {analysis.available_answers.map((answer) => {
                                        const answerClass =
                                            answer.code === 'YES'
                                                ? 'just-culture-page__answer just-culture-page__answer--yes'
                                                : answer.code === 'NO'
                                                    ? 'just-culture-page__answer just-culture-page__answer--no'
                                                    : 'just-culture-page__answer'

                                        return (
                                            <button
                                                key={answer.code}
                                                type="button"
                                                className={answerClass}
                                                disabled={isSubmitting}
                                                onClick={() => {
                                                    void answerQuestion(answer.code)
                                                }}
                                            >
                                                {translatedText(
                                                    answer.label,
                                                    answer.label_nl,
                                                    answer.label_en,
                                                    answer.label_pl,
                                                )}
                                            </button>
                                        )
                                    })}
                                </div>
                            )}

                            {analysis.conclusion_label && (
                                <div
                                    className={
                                        `just-culture-page__result ` +
                                        `just-culture-page__result--${getRecommendationLevel(
                                            analysis.recommendation_code,
                                        )}`
                                    }
                                >
                                    <div className="just-culture-page__result-section">
                                        <span className="just-culture-page__result-label">
                                            {t('accident.justCulture.conclusion')}
                                        </span>

                                        <strong className="just-culture-page__result-conclusion">
                                            {translatedText(
                                                analysis.conclusion_label,
                                                analysis.conclusion_label_nl,
                                                analysis.conclusion_label_en,
                                                analysis.conclusion_label_pl,
                                            )}
                                        </strong>
                                    </div>

                                    {analysis.recommendation_label && (
                                        <div className="just-culture-page__result-section">
                                            <span className="just-culture-page__result-label">
                                                {t('accident.justCulture.recommendation')}
                                            </span>

                                            <strong className="just-culture-page__result-recommendation">
                                                {translatedText(
                                                    analysis.recommendation_label,
                                                    analysis.recommendation_label_nl,
                                                    analysis.recommendation_label_en,
                                                    analysis.recommendation_label_pl,
                                                )}
                                            </strong>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* ========================================================
                                JUST CULTURE — CHEMIN DE DÉCISION
                                ======================================================== */}

                            {analysis.conclusion_label &&
                                analysis.history.length > 0 && (
                                    <div className="just-culture-page__decision-path">
                                        <div className="just-culture-page__decision-path-header">
                                            <span className="just-culture-page__result-label">
                                                {t('accident.justCulture.decisionPath')}
                                            </span>
                                        </div>

                                        <div className="just-culture-page__decision-path-steps">
                                            {analysis.history.map((step, index) => (
                                                <div
                                                    key={`${step.step_order}-${step.node_code}`}
                                                    className="just-culture-page__decision-step"
                                                >
                                                    <div className="just-culture-page__decision-marker">
                                                        <span>{index + 1}</span>
                                                    </div>

                                                    <div className="just-culture-page__decision-content">
                                                        <div className="just-culture-page__decision-question">
                                                            {translatedText(
                                                                step.question_text,
                                                                step.question_text_nl,
                                                                step.question_text_en,
                                                                step.question_text_pl,
                                                            )}
                                                        </div>

                                                        <span className="just-culture-page__decision-answer">
                                                            {translatedText(
                                                                step.answer_label,
                                                                step.answer_label_nl,
                                                                step.answer_label_en,
                                                                step.answer_label_pl,
                                                            )}
                                                        </span>
                                                    </div>
                                                </div>
                                            ))}

                                            <div className="just-culture-page__decision-final">
                                                <div
                                                    className={
                                                        `just-culture-page__decision-final-marker ` +
                                                        `just-culture-page__decision-final-marker--${getRecommendationLevel(
                                                            analysis.recommendation_code,
                                                        )}`
                                                    }
                                                >
                                                    ✓
                                                </div>

                                                <div>
                                                    <span className="just-culture-page__decision-final-label">
                                                        {t('accident.justCulture.conclusion')}
                                                    </span>

                                                    <strong>
                                                        {translatedText(
                                                            analysis.conclusion_label,
                                                            analysis.conclusion_label_nl,
                                                            analysis.conclusion_label_en,
                                                            analysis.conclusion_label_pl,
                                                        )}
                                                    </strong>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                            {/* ========================================================
                                JUST CULTURE — NAVIGATION ET VALIDATION
                                ======================================================== */}

                            {analysis.history.length > 0 && (
                                <div className="just-culture-page__final-actions">
                                    {!analysis.validated && (
                                        <button
                                            type="button"
                                            className="just-culture-back-step-button"
                                            onClick={() => void goBackOneQuestion()}
                                            disabled={busy}
                                        >
                                            ← {t('accident.justCulture.previousQuestion')}
                                        </button>
                                    )}

                                    {analysis.conclusion_label &&
                                        !analysis.validated && (
                                            <button
                                                type="button"
                                                className="just-culture-page__validate-button"
                                                onClick={() => void validateAnalysis()}
                                                disabled={busy}
                                            >
                                                ✓ {t('accident.justCulture.validate')}
                                            </button>
                                        )}

                                    {analysis.validated && (
                                        <>
                                            <div className="just-culture-page__validated">
                                                ✓ {t('accident.justCulture.validated')}
                                            </div>

                                            <button
                                                type="button"
                                                className="just-culture-page__reopen-button"
                                                onClick={() => void reopenAnalysis()}
                                                disabled={busy}
                                            >
                                                {t('accident.justCulture.reopen')}
                                            </button>
                                        </>
                                    )}
                                </div>
                            )}

                        </>
                    )}
            </section>
        </div>
    )
}

export default JustCulturePage