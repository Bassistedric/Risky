import i18n from '../../i18n'

export function at(key: string, options?: Record<string, unknown>) {
  return i18n.t(`accident.${key}`, options)
}
