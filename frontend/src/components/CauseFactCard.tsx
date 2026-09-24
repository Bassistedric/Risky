import { useTranslation } from 'react-i18next'

import './CauseFactCard.css'

type CauseFactCardProps = {
  description: string
  factType: string
  isTerminal: boolean
  level: number | null
  isSelected?: boolean
  onClick?: () => void
}

function CauseFactCard({
  description,
  factType,
  isTerminal,
  level,
  isSelected = false,
  onClick,
}: CauseFactCardProps) {
  const { t } = useTranslation()

  const levelClass =
    factType === 'FINAL'
      ? 'cause-fact-card--final'
      : level === null
        ? 'cause-fact-card--unlinked'
        : level === 1
          ? 'cause-fact-card--level-1'
          : level === 2
            ? 'cause-fact-card--level-2'
            : level >= 3
              ? 'cause-fact-card--level-deep'
              : ''

  const classes = [
    'cause-fact-card',
    levelClass,
    factType === 'CIRCUMSTANCE' ? 'cause-fact-card--circumstance' : '',
    isTerminal ? 'cause-fact-card--terminal' : '',
    isSelected ? 'cause-fact-card--selected' : '',
  ].filter(Boolean).join(' ')

  return (
    <div
      className={classes}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="cause-fact-card__description">{description}</div>

      <div className="cause-fact-card__type">
        {factType === 'FINAL' && t('accident.causeTree.finalFact')}
        {factType === 'CAUSE' && (
          isTerminal
            ? t('accident.causeTree.branchEnd')
            : t('accident.causeTree.cause')
        )}
        {factType === 'CIRCUMSTANCE' && t('accident.causeTree.unlinked')}
      </div>

      {level !== null && (
        <small className="cause-fact-card__level">
          {t('accident.causeTree.level', { level })}
        </small>
      )}
    </div>
  )
}

export default CauseFactCard
