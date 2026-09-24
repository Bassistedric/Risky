import './LanguageSelector.css'

import flagFr from '../assets/images/flag-fr.svg'
import flagNl from '../assets/images/flag-nl.svg'
import flagGb from '../assets/images/flag-gb.svg'
import flagPl from '../assets/images/flag-pl.svg'

export type RiskyLanguage =
    | 'fr'
    | 'nl'
    | 'en'
    | 'pl'

type LanguageSelectorProps = {
    value: RiskyLanguage
    onChange: (language: RiskyLanguage) => void
}

const languages: Array<{
    code: RiskyLanguage
    label: string
    flag: string
}> = [
    { code: 'fr', label: 'Français', flag: flagFr },
    { code: 'nl', label: 'Nederlands', flag: flagNl },
    { code: 'en', label: 'English', flag: flagGb },
    { code: 'pl', label: 'Polski', flag: flagPl },
]

function LanguageSelector({
    value,
    onChange,
}: LanguageSelectorProps) {
    return (
        <div
            className="language-selector"
            role="group"
            aria-label="Langue de l’interface"
        >
            {languages.map((language) => (
                <button
                    key={language.code}
                    className={
                        value === language.code
                            ? 'language-selector__button language-selector__button--active'
                            : 'language-selector__button'
                    }
                    type="button"
                    title={language.label}
                    aria-label={language.label}
                    aria-pressed={value === language.code}
                    onClick={() => onChange(language.code)}
                >
                    <img
                        src={language.flag}
                        alt=""
                        aria-hidden="true"
                    />
                </button>
            ))}
        </div>
    )
}

export default LanguageSelector
