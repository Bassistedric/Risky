import i18n from 'i18next'

import fr from './locales/fr.json'
import nl from './locales/nl.json'
import en from './locales/en.json'


// ========================================================
// TRADUCTIONS DU MODULE ACTIONS
// ========================================================

const resources = {
    fr,
    nl,
    en,
} as const


// ========================================================
// LECTURE D'UNE CLÉ
// ========================================================

function getNestedValue(
    source: Record<string, unknown>,
    path: string,
): string | undefined {
    const value = path
        .split('.')
        .reduce<unknown>((current, key) => {
            if (
                current &&
                typeof current === 'object' &&
                key in current
            ) {
                return (
                    current as Record<string, unknown>
                )[key]
            }

            return undefined
        }, source)

    return typeof value === 'string'
        ? value
        : undefined
}


// ========================================================
// FONCTION DE TRADUCTION
// ========================================================

export function act(
    key: string,
): string {
    const language =
        i18n.language === 'nl' ||
        i18n.language === 'en'
            ? i18n.language
            : 'fr'

    return (
        getNestedValue(
            resources[language],
            key,
        ) ??
        getNestedValue(
            resources.fr,
            key,
        ) ??
        key
    )
}