import fr from './locales/fr.json'
import nl from './locales/nl.json'
import en from './locales/en.json'
import pl from './locales/pl.json'

export type ReportLanguage =
    | 'fr'
    | 'nl'
    | 'en'
    | 'pl'

const translations = {
    fr,
    nl,
    en,
    pl,
}

export function getReportLanguage(): ReportLanguage {
    const storedLanguage =
        localStorage.getItem('risky_language')

    if (
        storedLanguage === 'nl' ||
        storedLanguage === 'en' ||
        storedLanguage === 'pl'
    ) {
        return storedLanguage
    }

    return 'fr'
}

export function rt(key: string): string {
    const language = getReportLanguage()

    const parts = key.split('.')

    let value: unknown =
        translations[language]

    for (const part of parts) {
        if (
            typeof value !== 'object' ||
            value === null ||
            !(part in value)
        ) {
            return key
        }

        value = (
            value as Record<string, unknown>
        )[part]
    }

    return typeof value === 'string'
        ? value
        : key
}