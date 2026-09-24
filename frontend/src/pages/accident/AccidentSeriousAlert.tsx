import { at } from './accidentI18n'
import './AccidentSeriousAlert.css'

import type {
    EventClassification,
    SeriousAccidentAssessment,
} from './accidentTypes'

type AccidentSeriousAlertProps = {
    assessment: SeriousAccidentAssessment | null
    loading: boolean
    classification: EventClassification | null
}

function seriousCriterionGroupLabel(
    group: string,
): string {
    if (group.includes('DEVIATION')) {
        return at('classification.deviation')
    }

    if (group.includes('MATERIAL_AGENT')) {
        return at('classification.materialAgent')
    }

    if (group.includes('INJURY')) {
        return at('classification.injuryNature')
    }

    if (group === 'CONSEQUENCE') {
        return at('serious.consequence')
    }

    return group
}

function seriousCriterionSelectedCode(
    group: string,
    classification: EventClassification | null,
): string | null {
    if (!classification) {
        return null
    }

    if (group.includes('DEVIATION')) {
        return classification.deviation_code
    }

    if (group.includes('MATERIAL_AGENT')) {
        return classification.material_agent_code
    }

    if (group.includes('INJURY')) {
        return classification.injury_nature_code
    }

    return null
}

function AccidentSeriousAlert({
    assessment,
    loading,
    classification,
}: AccidentSeriousAlertProps) {
    if (
        loading ||
        !assessment?.serious_accident
    ) {
        return null
    }

    return (
        <section
            className={
                assessment.very_serious_accident
                    ? 'accident-dossier__serious accident-dossier__serious--very'
                    : 'accident-dossier__serious'
            }
        >
            <div className="accident-dossier__serious-title">
                {assessment.very_serious_accident
                    ? at('serious.verySerious')
                    : at('serious.serious')}
            </div>

            {assessment.circumstantial_report_required && (
                <div>
                    {at('serious.reportRequired')}
                </div>
            )}

            {assessment.immediate_notification_required && (
                <div>
                    {at('serious.notificationRequired')}
                </div>
            )}

            {assessment.matched_criteria.length > 0 && (
                <div className="accident-dossier__serious-criteria">
                    <strong>
                        {at('serious.criteria')}
                    </strong>

                    {assessment.matched_criteria.map(
                        (criterion, index) => {
                            const groupLabel =
                                seriousCriterionGroupLabel(
                                    criterion.group,
                                )

                            const codeLabel =
                                seriousCriterionSelectedCode(
                                    criterion.group,
                                    classification,
                                )

                            return (
                                <div
                                    className="accident-dossier__serious-criterion"
                                    key={
                                        `${criterion.group}-` +
                                        `${criterion.code_from}-` +
                                        `${index}`
                                    }
                                >
                                    <strong>
                                        {groupLabel}
                                        {codeLabel &&
                                            ` — ${codeLabel}`}
                                    </strong>

                                    <span>
                                        {criterion.label}
                                    </span>
                                </div>
                            )
                        },
                    )}
                </div>
            )}
        </section>
    )
}

export default AccidentSeriousAlert
