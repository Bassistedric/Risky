import { at } from './accidentI18n'
import './FedrisCodeSelect.css'

import { useState } from 'react'
import { useTranslation } from 'react-i18next'

import type { EventCodeReference } from './accidentTypes'

// ============================================================
// OUTILS DE TRI DES CODES FEDRIS
// ============================================================

function fedrisCodeParts(code: string): number[] {
    return code
        .trim()
        .replace(',', '.')
        .split('.')
        .map((part) => Number(part))
}

function compareFedrisCodes(
    a: EventCodeReference,
    b: EventCodeReference,
): number {
    const aParts = fedrisCodeParts(a.code)
    const bParts = fedrisCodeParts(b.code)

    const length = Math.max(
        aParts.length,
        bParts.length,
    )

    for (let i = 0; i < length; i += 1) {
        const aValue = aParts[i] ?? 0
        const bValue = bParts[i] ?? 0

        if (aValue !== bValue) {
            return aValue - bValue
        }
    }

    return a.code.localeCompare(b.code)
}

function isFedrisCategoryCode(
    code: string,
): boolean {
    const normalized =
        code.trim().replace(',', '.')

    if (normalized.includes('.')) {
        const parts = normalized.split('.')

        return (
            parts.length === 2 &&
            Number(parts[1]) === 0
        )
    }

    const numericCode = Number(normalized)

    if (!Number.isFinite(numericCode)) {
        return false
    }

    return (
        numericCode === 0 ||
        numericCode % 10 === 0
    )
}

function getReferenceLabel(
    reference: EventCodeReference,
    language: string,
): string {
    if (language === 'nl') {
        return (
            reference.label_nl ||
            reference.label
        )
    }

    if (language === 'en') {
        return (
            reference.label_en ||
            reference.label
        )
    }

    if (language === 'pl') {
        return (
            reference.label_pl ||
            reference.label
        )
    }

    return reference.label
}

// ============================================================
// SÉLECTEUR RÉFÉRENTIEL FEDRIS
// ============================================================

type FedrisCodeSelectProps = {
    label: string
    value: string
    references: EventCodeReference[]
    emptyLabel: string
    onChange: (value: string) => void
}

function FedrisCodeSelect({
    label,
    value,
    references,
    emptyLabel,
    onChange,
}: FedrisCodeSelectProps) {
    const { i18n } = useTranslation()

    const language = i18n.language

    const [search, setSearch] = useState('')
    const [open, setOpen] = useState(false)

    const normalizedSearch =
        search.trim().toLocaleLowerCase()

    const sortedReferences = [...references].sort(
        compareFedrisCodes,
    )

    const filteredReferences =
        normalizedSearch === ''
            ? sortedReferences
            : sortedReferences.filter(
                (reference) => {
                    const searchable =
                        `${reference.code} ${getReferenceLabel(
                            reference,
                            language,
                        )}`
                            .toLocaleLowerCase()

                    return searchable.includes(
                        normalizedSearch,
                    )
                },
            )

    const selectedReference =
        references.find(
            (reference) => reference.code === value,
        ) ?? null

    const selectReference = (
        reference: EventCodeReference,
    ) => {
        onChange(reference.code)
        setSearch('')
        setOpen(false)
    }

    return (
        <div className="accident-dossier__fedris">
            <span className="accident-dossier__fedris-label">
                {label}
            </span>

            <button
                className="accident-dossier__fedris-current"
                type="button"
                onClick={() => setOpen((current) => !current)}
            >
                <span>
                    {selectedReference
                        ? `${selectedReference.code} — ${getReferenceLabel(
                            selectedReference,
                            language,
                        )}`
                        : emptyLabel}
                </span>

                <span aria-hidden="true">
                    {open ? '⌃' : '⌄'}
                </span>
            </button>

            {open && (
                <div className="accident-dossier__fedris-panel">
                    <input
                        className="accident-dossier__fedris-search"
                        type="search"
                        value={search}
                        placeholder={at('fedris.search')}
                        autoFocus
                        onChange={(event) =>
                            setSearch(event.target.value)
                        }
                    />

                    <div className="accident-dossier__fedris-list">
                        <button
                            className="accident-dossier__fedris-option accident-dossier__fedris-option--empty"
                            type="button"
                            onClick={() => {
                                onChange('')
                                setSearch('')
                                setOpen(false)
                            }}
                        >
                            {emptyLabel}
                        </button>

                        {filteredReferences.map(
                            (reference) => (
                                <button
                                    key={reference.id}
                                    className={`
                                        accident-dossier__fedris-option
                                        ${isFedrisCategoryCode(reference.code)
                                            ? 'accident-dossier__fedris-option--category'
                                            : ''}
                                        ${reference.code === value
                                            ? 'accident-dossier__fedris-option--selected'
                                            : ''}
                                    `}
                                    type="button"
                                    onClick={() =>
                                        selectReference(reference)
                                    }
                                >
                                    <strong>
                                        {reference.code}
                                    </strong>

                                    <span>
                                        {getReferenceLabel(
                                            reference,
                                            language,
                                        )}
                                    </span>
                                </button>
                            ),
                        )}

                        {filteredReferences.length === 0 && (
                            <div className="accident-dossier__fedris-no-result">
                                {at('fedris.noResult')}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}

export default FedrisCodeSelect
