import './AccidentReportsSection.css'

import { rt } from './i18n/reportI18n'

type AccidentReportsSectionProps = {
    onOpenAnalysisReport: () => void
    onOpenSafetyFlash: () => void
}

function AccidentReportsSection({
    onOpenAnalysisReport,
    onOpenSafetyFlash,
}: AccidentReportsSectionProps) {

    return (
        <section className="accident-reports">
            {/* ========================================================
                EN-TÊTE
            ======================================================== */}

            <div className="accident-reports__header">
                <div>
                    <h2>{rt('title')}</h2>
                    <p>{rt('subtitle')}</p>
                </div>
            </div>

            {/* ========================================================
                DOCUMENTS
            ======================================================== */}

            <div className="accident-reports__grid">
                <article className="accident-reports__card">
                    <div className="accident-reports__card-header">
                        <div>
                            <span className="accident-reports__eyebrow">
                                {rt('analysisReport.type')}
                            </span>

                            <h3>
                                {rt('analysisReport.title')}
                            </h3>
                        </div>

                        <span className="accident-reports__badge">
                            {rt('common.notGenerated')}
                        </span>
                    </div>

                    <p className="accident-reports__description">
                        {rt('analysisReport.description')}
                    </p>

                    <div className="accident-reports__actions">
                        <button
                            type="button"
                            className="accident-reports__button accident-reports__button--primary"
                            onClick={onOpenAnalysisReport}
                        >
                            {rt('analysisReport.preview')}
                        </button>
                    </div>
                </article>

                <article className="accident-reports__card">
                    <div className="accident-reports__card-header">
                        <div>
                            <span className="accident-reports__eyebrow">
                                {rt('safetyFlash.type')}
                            </span>

                            <h3>
                                {rt('safetyFlash.title')}
                            </h3>
                        </div>

                        <span className="accident-reports__badge">
                            {rt('common.draft')}
                        </span>
                    </div>

                    <p className="accident-reports__description">
                        {rt('safetyFlash.description')}
                    </p>

                    <div className="accident-reports__actions">
                        <button
                            type="button"
                            className="accident-reports__button accident-reports__button--secondary"
                            onClick={onOpenSafetyFlash}
                        >
                            {rt('safetyFlash.prepare')}
                        </button>
                    </div>
                </article>
            </div>
        </section>
    )
}

export default AccidentReportsSection