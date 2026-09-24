import {
    useEffect,
    useState,
} from 'react'

import './AccidentReportPreview.css'

import {
    downloadAnalysisReportPdf,
    getAnalysisReportPreview,
} from './reportApi'

import type {
    AccidentReportPreviewData,
} from './reportTypes'

import { API_BASE_URL } from '../accidentApi'

import CauseTreeReportDiagram
    from './components/CauseTreeReportDiagram'

import {
    getReportLanguage,
    rt,
} from './i18n/reportI18n'


type AccidentReportPreviewProps = {
    eventId: number
    onBack: () => void
}


/* ========================================================
   HELPERS
   ======================================================== */

function formatDate(
    value: string | null | undefined,
): string {
    if (!value) {
        return '—'
    }

    const localeMap = {
        fr: 'fr-BE',
        nl: 'nl-BE',
        en: 'en-GB',
        pl: 'pl-PL',
    } as const

    return new Intl.DateTimeFormat(
        localeMap[getReportLanguage()],
    ).format(
        new Date(value),
    )
}


function valueOrDash(
    value: string | null | undefined,
): string {
    return value?.trim() || '—'
}


function yesNo(
    value: boolean | null | undefined,
): string {
    if (
        value === null ||
        value === undefined
    ) {
        return rt('common.notProvided')
    }

    return value
        ? rt('common.yes')
        : rt('common.no')
}


function valueOrNotProvided(
    value: string | null | undefined,
): string {
    return (
        value?.trim() ||
        rt('common.notProvided')
    )
}


function translatedValue(
    group: string,
    value: string | null | undefined,
): string {
    if (!value?.trim()) {
        return rt('common.notProvided')
    }

    const key =
        `values.${group}.${value}`

    const translated = rt(key)

    return translated === key
        ? value
        : translated
}


function formatDays(
    value: number | null | undefined,
): string {
    const days = value ?? 0

    return `${days} ${days === 1
        ? rt('common.day')
        : rt('common.days')
        }`
}


function AccidentReportPreview({
    eventId,
    onBack,
}: AccidentReportPreviewProps) {
    const [
        report,
        setReport,
    ] = useState<
        AccidentReportPreviewData | null
    >(null)

    const [
        loading,
        setLoading,
    ] = useState(true)

    const [
        error,
        setError,
    ] = useState<string | null>(null)

    const [
        isGeneratingPdf,
        setIsGeneratingPdf,
    ] = useState(false)


    function getHeepoFactorLabel(
        item: AccidentReportPreviewData['heepo'][number],
    ): string {
        const language = getReportLanguage()

        if (language === 'nl') {
            return (
                item.factor_label_nl ||
                item.factor_label_fr ||
                item.factor_label ||
                '—'
            )
        }

        if (language === 'en') {
            return (
                item.factor_label_en ||
                item.factor_label_fr ||
                item.factor_label ||
                '—'
            )
        }

        if (language === 'pl') {
            return (
                item.factor_label_pl ||
                item.factor_label_fr ||
                item.factor_label ||
                '—'
            )
        }

        return (
            item.factor_label_fr ||
            item.factor_label ||
            '—'
        )
    }

    function getClassificationLabel(
        kind:
            | 'deviation'
            | 'material_agent'
            | 'injury_nature'
            | 'injury_location',
    ): string {
        if (!classification) {
            return '—'
        }

        const language = getReportLanguage()

        const snapshot =
            classification[
            `${kind}_label_snapshot`
            ]

        const fr =
            classification[
            `${kind}_label_fr`
            ]

        const nl =
            classification[
            `${kind}_label_nl`
            ]

        const en =
            classification[
            `${kind}_label_en`
            ]

        const pl =
            classification[
            `${kind}_label_pl`
            ]

        if (language === 'nl') {
            return (
                nl ||
                fr ||
                snapshot ||
                '—'
            )
        }

        if (language === 'en') {
            return (
                en ||
                fr ||
                snapshot ||
                '—'
            )
        }

        if (language === 'pl') {
            return (
                pl ||
                fr ||
                snapshot ||
                '—'
            )
        }

        return (
            fr ||
            snapshot ||
            '—'
        )
    }
        function getLocalizedReportText(
        snapshot: string | null | undefined,
        fr: string | null | undefined,
        nl: string | null | undefined,
        en: string | null | undefined,
        pl: string | null | undefined,
    ): string {
        const language = getReportLanguage()

        if (language === 'nl') {
            return (
                nl ||
                fr ||
                snapshot ||
                '—'
            )
        }

        if (language === 'en') {
            return (
                en ||
                fr ||
                snapshot ||
                '—'
            )
        }

        if (language === 'pl') {
            return (
                pl ||
                fr ||
                snapshot ||
                '—'
            )
        }

        return (
            fr ||
            snapshot ||
            '—'
        )
    }

    function getRecommendationLevel(
        recommendationCode: string | null | undefined,
    ): string {
        switch (recommendationCode) {
            case 'ACCOMPAGNEMENT': return 'support'
            case 'AVERTISSEMENT_VERBAL': return 'verbal'
            case 'PREMIER_AVERTISSEMENT_ECRIT': return 'written-first'
            case 'DERNIER_AVERTISSEMENT_ECRIT': return 'written-final'
            case 'LICENCIEMENT': return 'dismissal'
            default: return 'neutral'
        }
    }

    /* ========================================================
       CHARGEMENT
       ======================================================== */

    useEffect(() => {
        let cancelled = false

        async function loadReport() {
            try {
                setLoading(true)
                setError(null)

                const data =
                    await getAnalysisReportPreview(
                        eventId,
                    )

                if (!cancelled) {
                    setReport(data)
                }
            } catch (err) {
                if (!cancelled) {
                    setError(
                        err instanceof Error
                            ? err.message
                            : rt(
                                'preview.unknownError',
                            ),
                    )
                }
            } finally {
                if (!cancelled) {
                    setLoading(false)
                }
            }
        }

        loadReport()

        return () => {
            cancelled = true
        }
    }, [eventId])


    /* ========================================================
       ÉTATS
       ======================================================== */

    if (loading) {
        return (
            <div className="report-preview-state">
                {rt('preview.loading')}
            </div>
        )
    }

    if (error || !report) {
        return (
            <div className="report-preview-state">
                <p>
                    {error ??
                        rt(
                            'preview.unavailable',
                        )}
                </p>

                <button
                    type="button"
                    onClick={onBack}
                >
                    {rt('preview.back')}
                </button>
            </div>
        )
    }


    const {
        event,
        facts,
        classification,
        circumstantial_report,
        photos,
        heepo,
        cause_tree,
        just_culture,
        actions,
        sections,
    } = report


    /* ========================================================
       RENDU
       ======================================================== */

    return (
        <div className="report-preview">

            {/* =================================================
                EN-TÊTE
            ================================================= */}

            <div className="report-preview__toolbar">
                <button
                    type="button"
                    className="report-preview__back"
                    onClick={onBack}
                >
                    ← {rt('preview.back')}
                </button>

                <div>
                    <span>
                        {rt('preview.title')}
                    </span>

                    <strong>
                        {report.event_number}
                    </strong>
                </div>

                <button
                    type="button"
                    className="report-preview__generate"
                    disabled={isGeneratingPdf}
                    onClick={async () => {
                        try {
                            setIsGeneratingPdf(true)
                            await downloadAnalysisReportPdf(
                                eventId,
                                getReportLanguage(),
                            )
                        } catch {
                            setError(rt('preview.pdfGenerationError'))
                        } finally {
                            setIsGeneratingPdf(false)
                        }
                    }}
                >
                    {rt(
                        'preview.generatePdf',
                    )}
                </button>
            </div>


            {/* =================================================
                SYNTHÈSE & CONSÉQUENCES
            ================================================= */}

            <section className="report-preview__section">
                <div className="report-preview__section-title">
                    <span>01</span>

                    <h2>
                        {rt(
                            'preview.sections.summary',
                        )}
                    </h2>
                </div>

                <div className="report-preview__text-card">
                    <span>
                        {rt(
                            'preview.summary.description',
                        )}
                    </span>

                    <p>
                        {valueOrDash(
                            event.description,
                        )}
                    </p>
                </div>

                <div className="report-preview__summary-layout">

                    {/* =============================================
                        SYNTHÈSE
                    ============================================= */}

                    <div className="report-preview__summary-panel">
                        <h3>
                            {rt(
                                'preview.summary.title',
                            )}
                        </h3>

                        <div className="report-preview__summary-grid">
                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.type',
                                    )}
                                </span>

                                <strong>
                                    {translatedValue(
                                        'eventType',
                                        event.event_type,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.date',
                                    )}
                                </span>

                                <strong>
                                    {formatDate(
                                        event.event_date,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.person',
                                    )}
                                </span>

                                <strong>
                                    {valueOrNotProvided(
                                        event.person_name,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.category',
                                    )}
                                </span>

                                <strong>
                                    {translatedValue(
                                        'personCategory',
                                        event.person_category,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.organization',
                                    )}
                                </span>

                                <strong>
                                    {valueOrNotProvided(
                                        event.organization_name,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.location',
                                    )}
                                </span>

                                <strong>
                                    {valueOrNotProvided(
                                        event.location,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.projectManager',
                                    )}
                                </span>

                                <strong>
                                    {valueOrNotProvided(
                                        event.project_manager,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.siteSupervisor',
                                    )}
                                </span>

                                <strong>
                                    {valueOrNotProvided(
                                        event.site_supervisor,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.materialDamage',
                                    )}
                                </span>

                                <strong>
                                    {yesNo(
                                        event.material_damage,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.environmentalDamage',
                                    )}
                                </span>

                                <strong>
                                    {yesNo(
                                        event.environmental_damage,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.summary.analysisType',
                                    )}
                                </span>

                                <strong>
                                    {circumstantial_report
                                        ? rt('circumstantial.analysisType')
                                        : translatedValue(
                                            'analysisType',
                                            event.analysis_type,
                                        )}
                                </strong>
                            </div>
                        </div>
                    </div>


                    {/* =============================================
                        CONSÉQUENCES
                    ============================================= */}

                    <div className="report-preview__summary-panel">
                        <h3>
                            {rt(
                                'preview.consequences.title',
                            )}
                        </h3>

                        <div className="report-preview__consequences">
                            <div>
                                <span>
                                    {rt(
                                        'preview.consequences.lostTime',
                                    )}
                                </span>

                                <strong>
                                    {event.lost_time
                                        ? `${rt(
                                            'common.yes',
                                        )} — ${formatDays(
                                            event.lost_days,
                                        )}`
                                        : rt(
                                            'common.no',
                                        )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.consequences.modifiedDuty',
                                    )}
                                </span>

                                <strong>
                                    {event.modified_duty
                                        ? `${rt(
                                            'common.yes',
                                        )} — ${formatDays(
                                            event.modified_duty_days,
                                        )}`
                                        : rt(
                                            'common.no',
                                        )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.consequences.permanentInjury',
                                    )}
                                </span>

                                <strong>
                                    {yesNo(
                                        event.permanent_injury,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.consequences.fatal',
                                    )}
                                </span>

                                <strong>
                                    {yesNo(
                                        event.fatal,
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.consequences.materialDamageCost',
                                    )}
                                </span>

                                <strong>
                                    {event.material_damage
                                        ? event.material_damage_cost ??
                                        rt(
                                            'common.notProvided',
                                        )
                                        : rt(
                                            'common.notApplicable',
                                        )}
                                </strong>
                            </div>
                        </div>
                    </div>
                </div>


            </section>


            {/* =================================================
                RELATION DES FAITS
            ================================================= */}

            {sections.facts && facts && (
                <section className="report-preview__section">
                    <div className="report-preview__section-title">
                        <span>02</span>

                        <h2>
                            {rt(
                                'preview.sections.facts',
                            )}
                        </h2>
                    </div>

                    <div className="report-preview__facts-grid">
                        <div className="report-preview__fact-card">
                            <span>
                                {rt(
                                    'preview.facts.client',
                                )}
                            </span>

                            <strong>
                                {valueOrNotProvided(
                                    facts.client,
                                )}
                            </strong>
                        </div>

                        <div className="report-preview__fact-card">
                            <span>
                                {rt(
                                    'preview.facts.witnesses',
                                )}
                            </span>

                            <strong>
                                {valueOrNotProvided(
                                    facts.witnesses,
                                )}
                            </strong>
                        </div>

                        <div className="report-preview__fact-card">
                            <span>
                                {rt(
                                    'preview.facts.usualPosition',
                                )}
                            </span>

                            <strong>
                                {yesNo(
                                    facts.usual_position,
                                )}
                            </strong>
                        </div>
                    </div>

                    <div className="report-preview__text-card">
                        <span>
                            {rt(
                                'preview.facts.activityBefore',
                            )}
                        </span>

                        <p>
                            {valueOrNotProvided(
                                facts.activity_before_event,
                            )}
                        </p>
                    </div>

                    <div className="report-preview__text-card">
                        <span>
                            {rt(
                                'preview.facts.description',
                            )}
                        </span>

                        <p>
                            {valueOrNotProvided(
                                facts.event_description,
                            )}
                        </p>
                    </div>

                    <div className="report-preview__text-card">
                        <span>
                            {rt(
                                'preview.facts.directCause',
                            )}
                        </span>

                        <p>
                            {valueOrNotProvided(
                                facts.direct_cause,
                            )}
                        </p>
                    </div>

                    <div className="report-preview__facts-grid report-preview__facts-grid--two">
                        <div className="report-preview__fact-card">
                            <span>
                                {rt(
                                    'preview.facts.thirdParty',
                                )}
                            </span>

                            <strong>
                                {yesNo(
                                    facts.caused_by_third_party,
                                )}
                            </strong>
                        </div>

                        <div className="report-preview__fact-card">
                            <span>
                                {rt(
                                    'preview.facts.policeReport',
                                )}
                            </span>

                            <strong>
                                {yesNo(
                                    facts.police_report,
                                )}
                            </strong>
                        </div>
                    </div>

                    {facts.caused_by_third_party && (
                        <div className="report-preview__text-card">
                            <span>
                                {rt(
                                    'preview.facts.thirdPartyDetails',
                                )}
                            </span>

                            <p>
                                {valueOrNotProvided(
                                    facts.third_party_details,
                                )}
                            </p>
                        </div>
                    )}
                </section>
            )}


            {/* =================================================
                ACCIDENT GRAVE — DONNÉES COMPLÉMENTAIRES
            ================================================= */}

            {sections.circumstantial_details && circumstantial_report && (
                <section className="report-preview__section report-preview__section--circumstantial">
                    <div className="report-preview__section-title">
                        <span>03</span>
                        <h2>Données complémentaires du rapport circonstancié</h2>
                    </div>
                    <div className="report-preview__circumstantial-grid">
                        {[
                            ['Adresse de la victime', circumstantial_report.victim_address],
                            ['Date de naissance', circumstantial_report.victim_birth_date],
                            ['Ancienneté dans l’entreprise', circumstantial_report.victim_company_seniority],
                            ['Ancienneté dans la fonction', circumstantial_report.victim_job_seniority],
                            ['Employeur', circumstantial_report.employer_name],
                            ['Adresse de l’employeur', circumstantial_report.employer_address],
                            ['Assureur accidents du travail', circumstantial_report.insurer_name],
                            ['N° de police', circumstantial_report.insurance_policy_number],
                            ['Conseiller en prévention', circumstantial_report.prevention_advisor],
                            ['Responsable SIPP', circumstantial_report.sipp_manager],
                            ['SEPP', circumstantial_report.sepp_name],
                            ['Coordonnées SEPP', circumstantial_report.sepp_contact],
                        ].map(([label, value]) => (
                            <div className="report-preview__circumstantial-card" key={label}>
                                <span>{label}</span>
                                <strong>{valueOrNotProvided(value)}</strong>
                            </div>
                        ))}
                    </div>
                    {circumstantial_report.report_contributors && (
                        <div className="report-preview__text-card">
                            <span>Personnes ayant participé à l’élaboration</span>
                            <p>{circumstantial_report.report_contributors}</p>
                        </div>
                    )}
                    {circumstantial_report.report_recipients && (
                        <div className="report-preview__text-card">
                            <span>Destinataires du rapport</span>
                            <p>{circumstantial_report.report_recipients}</p>
                        </div>
                    )}
                </section>
            )}

            {/* =================================================
                DOCUMENTATION PHOTOGRAPHIQUE
            ================================================= */}

            {sections.photos &&
                photos.length > 0 && (
                    <section className="report-preview__section">
                        <div className="report-preview__section-title">
                            <span>04</span>

                            <h2>
                                {rt(
                                    'preview.sections.photos',
                                )}
                            </h2>
                        </div>

                        <div className="report-preview__photo-grid">
                            {photos.map((photo) => {
                                const imageUrl =
                                    `${API_BASE_URL}/events/${eventId}` +
                                    `/photos/${photo.id}/file`

                                return (
                                    <figure
                                        key={photo.id}
                                        className="report-preview__photo"
                                    >
                                        <a
                                            href={imageUrl}
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            <img
                                                src={imageUrl}
                                                alt={
                                                    photo.caption ||
                                                    photo.original_filename
                                                }
                                            />
                                        </a>

                                        <figcaption>
                                            {photo.caption ? (
                                                <strong>
                                                    {photo.caption}
                                                </strong>
                                            ) : (
                                                <span>
                                                    {photo.original_filename}
                                                </span>
                                            )}
                                        </figcaption>
                                    </figure>
                                )
                            })}
                        </div>
                    </section>
                )}


            {/* =================================================
                CLASSIFICATION
            ================================================= */}

            {sections.classification &&
                classification && (
                    <section className="report-preview__section">
                        <div className="report-preview__section-title">
                            <span>05</span>

                            <h2>
                                {rt(
                                    'preview.sections.classification',
                                )}
                            </h2>
                        </div>

                        <div className="report-preview__classification">
                            <div>
                                <span>
                                    {rt(
                                        'preview.classification.deviation',
                                    )}
                                </span>

                                <strong>
                                    {classification.deviation_code}
                                </strong>

                                <p>
                                    {getClassificationLabel(
                                        'deviation',
                                    )}
                                </p>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.classification.materialAgent',
                                    )}
                                </span>

                                <strong>
                                    {classification.material_agent_code}
                                </strong>

                                <p>
                                    {getClassificationLabel(
                                        'material_agent',
                                    )}
                                </p>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.classification.injuryNature',
                                    )}
                                </span>

                                <strong>
                                    {classification.injury_nature_code}
                                </strong>

                                <p>
                                    {getClassificationLabel(
                                        'injury_nature',
                                    )}
                                </p>
                            </div>

                            <div>
                                <span>
                                    {rt(
                                        'preview.classification.injuryLocation',
                                    )}
                                </span>

                                <strong>
                                    {classification.injury_location_code}
                                </strong>

                                <p>
                                    {getClassificationLabel(
                                        'injury_location',
                                    )}
                                </p>
                            </div>
                        </div>
                    </section>
                )}


            {/* =================================================
                ACCIDENT GRAVE — CAUSES COMPLÉMENTAIRES
            ================================================= */}

            {sections.circumstantial_causes && circumstantial_report && (() => {
                let selected: string[] = []
                try {
                    selected = JSON.parse(circumstantial_report.cause_selections_json || '[]')
                } catch {
                    selected = []
                }
                const groups = [
                    { title: 'Causes primaires · matérielles', codes: ['product','machine','tool','orderCleanliness','transport','materialOther','collectiveAbsent','collectiveMissing','collectiveDisabled','collectiveOther','ppeMisuse','ppeAbsent','ppeUnsuitable','ppeOther','lighting','noise','temperature','environmentOther'], details: circumstantial_report.primary_details },
                    { title: 'Causes secondaires · organisationnelles', codes: ['riskAnalysis','instructions','sippOperation','organizationOther','followupControl','trainingGap','communicationOther','distraction','intentionalNegligence','fatigue','incompetence','haste','humanOther'], details: circumstantial_report.secondary_details },
                    { title: 'Causes tertiaires · tiers', codes: ['designManufacturing','noncompliantEquipment','badAdvice','instructionsNotFollowed','sitePressure','thirdOrganizationOther'], details: circumstantial_report.tertiary_details },
                ]
                return (
                    <section className="report-preview__section report-preview__section--circumstantial">
                        <div className="report-preview__section-title">
                            <span>06</span>
                            <h2>Analyse complémentaire des causes</h2>
                        </div>
                        <div className="report-preview__circumstantial-causes">
                            {groups.map(group => (
                                <div className="report-preview__circumstantial-cause" key={group.title}>
                                    <h3>{group.title}</h3>
                                    <div className="report-preview__circumstantial-pills">
                                        {group.codes.filter(code => selected.includes(code)).map(code => (
                                            <span key={code}>✓ {rt('circumstantial.options.' + code)}</span>
                                        ))}
                                        {!group.codes.some(code => selected.includes(code)) && <em>Aucune cause sélectionnée</em>}
                                    </div>
                                    {group.details && <p>{group.details}</p>}
                                </div>
                            ))}
                        </div>
                    </section>
                )
            })()}

            {/* =================================================
                HEEPO
            ================================================= */}

            {sections.heepo && (
                <section className="report-preview__section">
                    <div className="report-preview__section-title">
                        <span>07</span>

                        <h2>
                            {rt(
                                'preview.sections.heepo',
                            )}
                        </h2>
                    </div>

                    <div className="report-preview__list">
                        {heepo
                            .filter(
                                (item) =>
                                    !item.is_na,
                            )
                            .map((item) => (
                                <div
                                    key={item.id}
                                    className="report-preview__list-item"
                                >
                                    <strong>
                                        {item.factor_code}
                                    </strong>

                                    <div>
                                        <span>
                                            {item.family}
                                        </span>

                                        <p>
                                            {getHeepoFactorLabel(
                                                item,
                                            )}
                                        </p>
                                    </div>
                                </div>
                            ))}
                    </div>
                </section>
            )}


            {/* =================================================
                JUST CULTURE
            ================================================= */}

            <section className="report-preview__section">
                <div className="report-preview__section-title">
                    <span>08</span>
                    <h2>{rt('preview.sections.justCulture')}</h2>
                </div>

                {just_culture ? (
                    <>
                        <div className="report-preview__decision-path">
                            {just_culture.history.map((step) => (
                                <div key={step.step_order} className="report-preview__decision">
                                    <span>{step.step_order}</span>
                                    <div>
                                        <p>{getLocalizedReportText(step.question_text, step.question_text_fr, step.question_text_nl, step.question_text_en, step.question_text_pl)}</p>
                                        <strong>{getLocalizedReportText(step.answer_label, step.answer_label_fr, step.answer_label_nl, step.answer_label_en, step.answer_label_pl)}</strong>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className={`report-preview__result-grid report-preview__result-grid--${getRecommendationLevel(just_culture.recommendation_code)}`}>
                            <div>
                                <span>{rt('preview.justCulture.conclusion')}</span>
                                <strong>{getLocalizedReportText(just_culture.conclusion_label, just_culture.conclusion_label_fr, just_culture.conclusion_label_nl, just_culture.conclusion_label_en, just_culture.conclusion_label_pl)}</strong>
                            </div>
                            <div>
                                <span>{rt('preview.justCulture.recommendation')}</span>
                                <strong>{getLocalizedReportText(just_culture.recommendation_label, just_culture.recommendation_label_fr, just_culture.recommendation_label_nl, just_culture.recommendation_label_en, just_culture.recommendation_label_pl)}</strong>
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="report-preview__not-applicable">
                        {rt('common.notApplicable')}
                    </div>
                )}
            </section>


            {/* =================================================
                ARBRE DES CAUSES
            ================================================= */}

            {sections.cause_tree &&
                cause_tree && (
                    <section className="report-preview__section">
                        <div className="report-preview__section-title">
                            <span>09</span>

                            <h2>
                                {rt(
                                    'preview.sections.causeTree',
                                )}
                            </h2>
                        </div>

                        <CauseTreeReportDiagram
                            facts={
                                cause_tree.facts
                            }
                            relations={
                                cause_tree.relations
                            }
                        />
                    </section>
                )}


            {/* =================================================
                ACTIONS
            ================================================= */}

            {sections.actions && (
                <section className="report-preview__section">
                    <div className="report-preview__section-title">
                        <span>10</span>

                        <h2>
                            {rt(
                                'preview.sections.actions',
                            )}
                        </h2>
                    </div>

                    <div className="report-preview__actions">
                        {actions.map((action) => (
                            <div
                                key={action.id}
                                className="report-preview__action"
                            >
                                <div>
                                    <strong>
                                        {
                                            action.description
                                        }
                                    </strong>

                                    <span>
                                        {translatedValue(
                                            'actionType',
                                            action.action_type,
                                        )}
                                        {' · '}
                                        {translatedValue(
                                            'scope',
                                            action.scope,
                                        )}
                                    </span>
                                </div>

                                <div>
                                    <span>
                                        {rt(
                                            'preview.actions.responsible',
                                        )}
                                    </span>

                                    <strong>
                                        {valueOrDash(
                                            action.responsible_text,
                                        )}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        {rt(
                                            'preview.actions.dueDate',
                                        )}
                                    </span>

                                    <strong>
                                        {formatDate(
                                            action.due_date,
                                        )}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        {rt(
                                            'preview.actions.progress',
                                        )}
                                    </span>

                                    <strong>
                                        {action.progress_percent ??
                                            0}{' '}
                                        %
                                    </strong>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}
        </div>
    )
}

export default AccidentReportPreview