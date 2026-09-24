import {
    useEffect,
    useMemo,
    useState,
} from 'react'

import { useTranslation } from 'react-i18next'

import { API_BASE_URL } from './accidentApi'
import { at } from './accidentI18n'
import './HeepoPage.css'


type HeepoFactor = {
    id: number
    family: string
    code: string
    label: string
    label_nl: string | null
    label_en: string | null
    label_pl: string | null
    active: boolean
}
// ============================================================
// LIBELLÉS MULTILINGUES DES FACTEURS HEEPO
// ============================================================

type SavedHeepoItem = {
    id: number
    event_id: number
    heepo_factor_id: number | null
    family: string
    factor_code_snapshot: string | null
    factor_label_snapshot: string | null
    other_text: string | null
    is_na: boolean
}

type HeepoSelection = {
    factorId: number
    otherText: string
}

type FamilyState = {
    selections: HeepoSelection[]
    isNa: boolean
}

type HeepoState = Record<string, FamilyState>


type HeepoPageProps = {
    eventId: number
    eventNumber?: string
    onBack: () => void
}


const FAMILY_ORDER = [
    'HOMME',
    'EQUIPEMENT',
    'ENVIRONNEMENT',
    'PRODUIT',
    'ORGANISATION',
]


function createEmptyState(): HeepoState {
    return Object.fromEntries(
        FAMILY_ORDER.map((family) => [
            family,
            {
                selections: [],
                isNa: false,
            },
        ]),
    )
}


function HeepoPage({
    eventId,
    eventNumber,
    onBack,
}: HeepoPageProps) {

    const { i18n } = useTranslation()

    const getFactorLabel = (factor: HeepoFactor): string => {
        const language = i18n.resolvedLanguage ?? i18n.language

        if (language?.startsWith('nl')) {
            return factor.label_nl || factor.label
        }

        if (language?.startsWith('en')) {
            return factor.label_en || factor.label
        }

        if (language?.startsWith('pl')) {
            return factor.label_pl || factor.label
        }

        return factor.label
    }

    const [factors, setFactors] =
        useState<HeepoFactor[]>([])

    const [state, setState] =
        useState<HeepoState>(createEmptyState)

    const [isLoading, setIsLoading] =
        useState(true)

    const [isSaving, setIsSaving] =
        useState(false)

    const [showResetConfirm, setShowResetConfirm] =
        useState(false)

    const [error, setError] =
        useState<string | null>(null)

    const [saved, setSaved] =
        useState(false)


    const factorsByFamily = useMemo(() => {
        const result: Record<string, HeepoFactor[]> = {}

        for (const family of FAMILY_ORDER) {
            result[family] = factors
                .filter(
                    (factor) =>
                        factor.family === family,
                )
                .sort((a, b) => {
                    const getNumber = (
                        code: string,
                    ) =>
                        Number(
                            code.match(/\d+/)?.[0] ?? 0,
                        )

                    const aNumber =
                        getNumber(a.code)

                    const bNumber =
                        getNumber(b.code)

                    // Code 0 = "Autres" :
                    // toujours en dernière position.
                    if (
                        aNumber === 0 &&
                        bNumber !== 0
                    ) {
                        return 1
                    }

                    if (
                        bNumber === 0 &&
                        aNumber !== 0
                    ) {
                        return -1
                    }

                    return aNumber - bNumber
                })
        }

        return result
    }, [factors])


    useEffect(() => {
        async function loadHeepo() {
            try {
                setIsLoading(true)
                setError(null)

                const [
                    factorsResponse,
                    eventResponse,
                ] = await Promise.all([
                    fetch(
                        `${API_BASE_URL}/events/heepo-factors`,
                    ),
                    fetch(
                        `${API_BASE_URL}/events/${eventId}/heepo`,
                    ),
                ])

                if (!factorsResponse.ok) {
                    throw new Error(
                        at('heepo.referenceLoadError'),
                    )
                }

                if (!eventResponse.ok) {
                    throw new Error(
                        at('heepo.loadError'),
                    )
                }

                const factorData:
                    HeepoFactor[] =
                    await factorsResponse.json()

                const eventData: {
                    event_id: number
                    items: SavedHeepoItem[]
                } =
                    await eventResponse.json()

                const nextState =
                    createEmptyState()

                for (
                    const item
                    of eventData.items
                ) {
                    if (
                        !nextState[item.family]
                    ) {
                        continue
                    }

                    if (item.is_na) {
                        nextState[
                            item.family
                        ].isNa = true

                        continue
                    }

                    if (
                        item.heepo_factor_id !==
                        null
                    ) {
                        nextState[
                            item.family
                        ].selections.push({
                            factorId:
                                item.heepo_factor_id,

                            otherText:
                                item.other_text ??
                                '',
                        })
                    }
                }

                setFactors(factorData)
                setState(nextState)
            } catch (error) {
                setError(
                    error instanceof Error
                        ? error.message
                        : at(
                            'heepo.unexpectedError',
                        ),
                )
            } finally {
                setIsLoading(false)
            }
        }

        void loadHeepo()
    }, [eventId])


    function toggleFactor(
        family: string,
        factorId: number,
    ) {
        setSaved(false)

        setState((current) => {
            const familyState =
                current[family]

            const exists =
                familyState.selections.some(
                    (item) =>
                        item.factorId ===
                        factorId,
                )

            const selections = exists
                ? familyState.selections.filter(
                    (item) =>
                        item.factorId !==
                        factorId,
                )
                : [
                    ...familyState.selections,
                    {
                        factorId,
                        otherText: '',
                    },
                ]

            return {
                ...current,

                [family]: {
                    selections,
                    isNa: false,
                },
            }
        })
    }


    function toggleNa(
        family: string,
    ) {
        setSaved(false)

        setState((current) => {
            const newValue =
                !current[family].isNa

            return {
                ...current,

                [family]: {
                    selections: [],
                    isNa: newValue,
                },
            }
        })
    }


    function updateOtherText(
        family: string,
        factorId: number,
        value: string,
    ) {
        setSaved(false)

        setState((current) => ({
            ...current,

            [family]: {
                ...current[family],

                selections:
                    current[
                        family
                    ].selections.map(
                        (item) =>
                            item.factorId ===
                                factorId
                                ? {
                                    ...item,
                                    otherText:
                                        value,
                                }
                                : item,
                    ),
            },
        }))
    }


    async function saveHeepo() {
        try {
            setIsSaving(true)
            setError(null)
            setSaved(false)

            const items = []

            for (
                const family
                of FAMILY_ORDER
            ) {
                const familyState =
                    state[family]

                if (familyState.isNa) {
                    items.push({
                        family,
                        factor_id: null,
                        other_text: null,
                        is_na: true,
                    })

                    continue
                }

                for (
                    const selection
                    of familyState.selections
                ) {
                    const factor =
                        factors.find(
                            (item) =>
                                item.id ===
                                selection.factorId,
                        )

                    items.push({
                        family,

                        factor_id:
                            selection.factorId,

                        other_text:
                            Number(
                                factor?.code.match(
                                    /\d+/,
                                )?.[0] ?? -1,
                            ) === 0
                                ? selection.otherText
                                : null,

                        is_na: false,
                    })
                }
            }

            const token =
                sessionStorage.getItem(
                    'risky_session_token',
                )

            if (!token) {
                throw new Error(
                    at(
                        'heepo.sessionRequired',
                    ),
                )
            }

            const response =
                await fetch(
                    `${API_BASE_URL}/events/${eventId}/heepo`,
                    {
                        method: 'PUT',

                        headers: {
                            'Content-Type':
                                'application/json',

                            'X-Session-Token':
                                token,
                        },

                        body:
                            JSON.stringify({
                                items,
                            }),
                    },
                )

            if (!response.ok) {
                const body =
                    await response
                        .json()
                        .catch(() => null)

                throw new Error(
                    body?.detail ??
                    at('heepo.saveError'),
                )
            }

            setSaved(true)
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : at(
                        'heepo.unexpectedError',
                    ),
            )
        } finally {
            setIsSaving(false)
        }
    }


    if (isLoading) {
        return (
            <div className="heepo-page">
                {at('heepo.loading')}
            </div>
        )
    }


    const getFamilyClass = (
        family: string,
    ) => {
        switch (family) {
            case 'HOMME':
                return 'heepo-family--human'

            case 'EQUIPEMENT':
                return 'heepo-family--equipment'

            case 'ENVIRONNEMENT':
                return 'heepo-family--environment'

            case 'PRODUIT':
                return 'heepo-family--product'

            case 'ORGANISATION':
                return 'heepo-family--organization'

            default:
                return ''
        }
    }


    return (
        <div className="heepo-page">

            <button
                type="button"
                className="heepo-page__back risky-back-button"
                onClick={onBack}
            >
                <span aria-hidden="true">
                    ←
                </span>

                {at('heepo.back')}
            </button>


            <header className="heepo-page__header">
                <div>
                    <span className="heepo-page__eyebrow">
                        {at('heepo.eyebrow')}
                    </span>

                    <h1>
                        {at('heepo.title')}
                    </h1>

                    {eventNumber && (
                        <p>
                            {at(
                                'heepo.file',
                                {
                                    eventNumber,
                                },
                            )}
                        </p>
                    )}
                </div>
            </header>


            {error && (
                <div className="heepo-page__error">
                    {error}
                </div>
            )}


            <div className="heepo-page__families">
                {FAMILY_ORDER.map(
                    (family) => {
                        const familyState =
                            state[family]

                        return (
                            <section
                                key={family}
                                className={
                                    `heepo-family ${getFamilyClass(
                                        family,
                                    )}`
                                }
                            >
                                <div className="heepo-family__header">
                                    <div>
                                        <span className="heepo-family__code">
                                            {at(
                                                `heepo.familyCodes.${family}`,
                                            )}
                                        </span>

                                        <h2>
                                            {at(
                                                `heepo.families.${family}`,
                                            )}
                                        </h2>
                                    </div>

                                    <label className="heepo-na">
                                        <input
                                            type="checkbox"
                                            checked={
                                                familyState.isNa
                                            }
                                            onChange={() =>
                                                toggleNa(
                                                    family,
                                                )
                                            }
                                        />

                                        <span>
                                            {at(
                                                'heepo.na',
                                            )}
                                        </span>
                                    </label>
                                </div>


                                <div className="heepo-family__factors">
                                    {factorsByFamily[
                                        family
                                    ]?.map(
                                        (factor) => {
                                            const selection =
                                                familyState
                                                    .selections
                                                    .find(
                                                        (
                                                            item,
                                                        ) =>
                                                            item.factorId ===
                                                            factor.id,
                                                    )

                                            const checked =
                                                selection !==
                                                undefined

                                            const isOther =
                                                Number(
                                                    factor.code.match(
                                                        /\d+/,
                                                    )?.[0] ??
                                                    -1,
                                                ) === 0

                                            return (
                                                <div
                                                    key={
                                                        factor.id
                                                    }
                                                    className={
                                                        `heepo-factor ${checked
                                                            ? 'heepo-factor--selected'
                                                            : ''
                                                        }`
                                                    }
                                                >
                                                    <label>
                                                        <input
                                                            type="checkbox"
                                                            checked={
                                                                checked
                                                            }
                                                            disabled={
                                                                familyState.isNa
                                                            }
                                                            onChange={() =>
                                                                toggleFactor(
                                                                    family,
                                                                    factor.id,
                                                                )
                                                            }
                                                        />

                                                        <span className="heepo-factor__code">
                                                            {
                                                                factor.code
                                                            }
                                                        </span>

                                                        <span className="heepo-factor__label">
                                                            {
                                                                getFactorLabel(factor)
                                                            }
                                                        </span>
                                                    </label>


                                                    {checked &&
                                                        isOther && (
                                                            <input
                                                                type="text"
                                                                className="heepo-factor__other"
                                                                placeholder={
                                                                    at(
                                                                        'heepo.otherPlaceholder',
                                                                    )
                                                                }
                                                                value={
                                                                    selection
                                                                        .otherText
                                                                }
                                                                onChange={(
                                                                    event,
                                                                ) =>
                                                                    updateOtherText(
                                                                        family,
                                                                        factor.id,
                                                                        event
                                                                            .target
                                                                            .value,
                                                                    )
                                                                }
                                                            />
                                                        )}
                                                </div>
                                            )
                                        },
                                    )}
                                </div>
                            </section>
                        )
                    },
                )}


                {/* ====================================================
                    SYNTHÈSE HEEPO / MUOPO
                    ==================================================== */}

                <aside className="heepo-summary">
                    <div className="heepo-summary__header">
                        <div>
                            <strong>
                                {at(
                                    'heepo.summary',
                                )}
                            </strong>

                            <span>
                                {at(
                                    'heepo.summaryDescription',
                                )}
                            </span>
                        </div>
                    </div>


                    <div className="heepo-summary__content">
                        {FAMILY_ORDER.map(
                            (family) => {
                                const familyState =
                                    state[family]

                                const selectedFactors =
                                    familyState
                                        .selections
                                        .map(
                                            (
                                                selection,
                                            ) => {
                                                const factor =
                                                    factorsByFamily[
                                                        family
                                                    ]?.find(
                                                        (
                                                            item,
                                                        ) =>
                                                            item.id ===
                                                            selection.factorId,
                                                    )

                                                if (
                                                    !factor
                                                ) {
                                                    return null
                                                }

                                                const factorLabel =
                                                    getFactorLabel(factor)

                                                return {
                                                    code:
                                                        factor.code,

                                                    label:
                                                        selection.otherText
                                                            ? `${factorLabel} : ${selection.otherText}`
                                                            : factorLabel,
                                                }
                                            },
                                        )
                                        .filter(
                                            (
                                                item,
                                            ): item is {
                                                code: string
                                                label: string
                                            } =>
                                                item !==
                                                null,
                                        )

                                return (
                                    <div
                                        key={
                                            family
                                        }
                                        className="heepo-summary__family"
                                    >
                                        <div
                                            className={
                                                `heepo-summary__family-code ${getFamilyClass(
                                                    family,
                                                )}`
                                            }
                                        >
                                            {at(
                                                `heepo.familyCodes.${family}`,
                                            )}
                                        </div>

                                        <div className="heepo-summary__family-content">
                                            <strong>
                                                {at(
                                                    `heepo.families.${family}`,
                                                )}
                                            </strong>

                                            {familyState.isNa ? (
                                                <span className="heepo-summary__na">
                                                    {at(
                                                        'heepo.na',
                                                    )}
                                                </span>
                                            ) : selectedFactors.length >
                                                0 ? (
                                                <div className="heepo-summary__items">
                                                    {selectedFactors.map(
                                                        (
                                                            factor,
                                                        ) => (
                                                            <span
                                                                key={
                                                                    factor.code
                                                                }
                                                                className="heepo-summary__item"
                                                            >
                                                                <b>
                                                                    {
                                                                        factor.code
                                                                    }
                                                                </b>

                                                                <span>
                                                                    {
                                                                        factor.label
                                                                    }
                                                                </span>
                                                            </span>
                                                        ),
                                                    )}
                                                </div>
                                            ) : (
                                                <span className="heepo-summary__empty">
                                                    {at(
                                                        'heepo.noFactor',
                                                    )}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                )
                            },
                        )}
                    </div>
                </aside>
            </div>


            <div className="heepo-page__actions">
                {saved && (
                    <span className="heepo-page__saved">
                        {at(
                            'heepo.saved',
                        )}
                    </span>
                )}

                <button
                    type="button"
                    className="heepo-page__cancel"
                    onClick={() =>
                        setShowResetConfirm(
                            true,
                        )
                    }
                    disabled={isSaving}
                >
                    {at('heepo.reset')}
                </button>

                <button
                    type="button"
                    className="heepo-page__save"
                    onClick={() => {
                        void saveHeepo()
                    }}
                    disabled={isSaving}
                >
                    {isSaving
                        ? at(
                            'heepo.saving',
                        )
                        : at(
                            'heepo.save',
                        )}
                </button>
            </div>


            {showResetConfirm && (
                <div
                    className="heepo-reset-modal"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="heepo-reset-title"
                >
                    <div
                        className="heepo-reset-modal__backdrop"
                        onClick={() =>
                            setShowResetConfirm(
                                false,
                            )
                        }
                    />

                    <div className="heepo-reset-modal__dialog">
                        <div className="heepo-reset-modal__icon">
                            !
                        </div>

                        <div className="heepo-reset-modal__content">
                            <h2 id="heepo-reset-title">
                                {at(
                                    'heepo.resetTitle',
                                )}
                            </h2>

                            <p>
                                {at(
                                    'heepo.resetMessage',
                                )}
                            </p>

                            <div className="heepo-reset-modal__warning">
                                {at(
                                    'heepo.resetWarning',
                                )}
                            </div>
                        </div>

                        <div className="heepo-reset-modal__actions">
                            <button
                                type="button"
                                className="heepo-reset-modal__keep"
                                onClick={() =>
                                    setShowResetConfirm(
                                        false,
                                    )
                                }
                            >
                                {at(
                                    'heepo.keepAnalysis',
                                )}
                            </button>

                            <button
                                type="button"
                                className="heepo-reset-modal__confirm"
                                onClick={() => {
                                    setState(
                                        Object.fromEntries(
                                            FAMILY_ORDER.map(
                                                (
                                                    family,
                                                ) => [
                                                        family,
                                                        {
                                                            isNa: false,
                                                            selections:
                                                                [],
                                                        },
                                                    ],
                                            ),
                                        ),
                                    )

                                    setSaved(false)

                                    setShowResetConfirm(
                                        false,
                                    )
                                }}
                            >
                                {at(
                                    'heepo.reset',
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}


export default HeepoPage