import './HomePage.css'

import { useTranslation } from 'react-i18next'


type HomeModule =
  | 'risk-analysis'
  | 'accidents'
  | 'action-plans'
  | 'personnel'
  | 'competencies'
  | 'equipment'
  | 'field'
  | 'quality'


type HomePageProps = {
  onOpenModule: (module: HomeModule) => void
}


const modules = [
  { id: 'risk-analysis', titleKey: 'home.modules.riskAnalysis.title', descriptionKey: 'home.modules.riskAnalysis.description', symbol: '◇' },
  { id: 'accidents', titleKey: 'home.modules.accidents.title', descriptionKey: 'home.modules.accidents.description', symbol: '△' },
  { id: 'action-plans', titleKey: 'home.modules.actionPlans.title', descriptionKey: 'home.modules.actionPlans.description', symbol: '☑' },
  { id: 'personnel', titleKey: 'home.modules.personnel.title', descriptionKey: 'home.modules.personnel.description', symbol: '♙' },
  { id: 'competencies', titleKey: 'home.modules.training.title', descriptionKey: 'home.modules.training.description', symbol: '✓' },
  { id: 'equipment', titleKey: 'home.modules.equipment.title', descriptionKey: 'home.modules.equipment.description', symbol: '▣' },
  { id: 'field', titleKey: 'home.modules.field.title', descriptionKey: 'home.modules.field.description', symbol: '⌖' },
  { id: 'quality', titleKey: 'home.modules.quality.title', descriptionKey: 'home.modules.quality.description', symbol: '☆' },
] satisfies Array<{
  id: HomeModule
  titleKey: string
  descriptionKey: string
  symbol: string
}>


export default function HomePage({
  onOpenModule,
}: HomePageProps) {

  const { t } = useTranslation()

  return (
    <div className="home-page">

      {/* ====================================================
          EN-TÊTE
          ==================================================== */}

      <div className="home-section-heading">
        <div>
          <span>{t('home.modulesEyebrow')}</span>
          <h2>{t('home.modulesTitle')}</h2>
        </div>
        <p>{t('home.description')}</p>
      </div>


      {/* ====================================================
          MODULES
          ==================================================== */}

      <section className="home-modules">
        {modules.map((module) => (
          <button
            key={module.id}
            type="button"
            className="home-module-card"
            onClick={() => {
              onOpenModule(module.id)
            }}
          >
            <div className={`home-module-card__symbol home-module-card__symbol--${module.id}`}>
              <span>{module.symbol}</span>
            </div>

            <div className="home-module-card__content">
              <h2>
                {t(module.titleKey)}
              </h2>

              <p>
                {t(module.descriptionKey)}
              </p>
            </div>

            <div className="home-module-card__arrow" aria-hidden="true">
              →
            </div>
          </button>
        ))}
      </section>

    </div>
  )
}