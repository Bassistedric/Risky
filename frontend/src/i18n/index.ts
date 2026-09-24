import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import frCommon from './locales/fr/common.json'
import frNavigation from './locales/fr/navigation.json'
import frAccidents from './locales/fr/accidents.json'

import nlCommon from './locales/nl/common.json'
import nlNavigation from './locales/nl/navigation.json'
import nlAccidents from './locales/nl/accidents.json'

import enCommon from './locales/en/common.json'
import enNavigation from './locales/en/navigation.json'
import enAccidents from './locales/en/accidents.json'

import plCommon from './locales/pl/common.json'
import plNavigation from './locales/pl/navigation.json'
import plAccidents from './locales/pl/accidents.json'

const storedLanguage =
  localStorage.getItem('risky_language')

const initialLanguage =
  storedLanguage === 'nl' ||
  storedLanguage === 'en' ||
  storedLanguage === 'pl'
    ? storedLanguage
    : 'fr'

void i18n
  .use(initReactI18next)
  .init({
    resources: {
      fr: {
        translation: {
          ...frCommon,
          ...frNavigation,
          accident: frAccidents,
        },
      },

      nl: {
        translation: {
          ...nlCommon,
          ...nlNavigation,
          accident: nlAccidents,
        },
      },

      en: {
        translation: {
          ...enCommon,
          ...enNavigation,
          accident: enAccidents,
        },
      },

      pl: {
        translation: {
          ...plCommon,
          ...plNavigation,
          accident: plAccidents,
        },
      },
    },

    lng: initialLanguage,
    fallbackLng: 'fr',

    interpolation: {
      escapeValue: false,
    },
  })

export default i18n