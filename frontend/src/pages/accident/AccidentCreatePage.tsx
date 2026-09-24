import { at } from './accidentI18n'
import {
    useEffect,
    useState,
} from 'react'

import './AccidentCreatePage.css'

// ============================================================
// CONFIGURATION
// ============================================================

const API_BASE_URL = 'http://127.0.0.1:8000'

// ============================================================
// TYPES
// ============================================================

type Person = {
    id: number
    employee_number: string | null
    last_name: string
    first_name: string
}

type AccidentCreatePageProps = {
    onBack: () => void
    onCreated: (eventId: number) => void
}

// ============================================================
// COMPONENT
// ============================================================

function AccidentCreatePage({
    onBack,
    onCreated,
}: AccidentCreatePageProps) {

    // ========================================================
    // DONNÉES DE RÉFÉRENCE
    // ========================================================

    const [people, setPeople] =
        useState<Person[]>([])

    // ========================================================
    // ÉVÉNEMENT
    // ========================================================

    const [eventType, setEventType] =
        useState('ACCIDENT')

    const [eventDate, setEventDate] =
        useState('')

    const [location, setLocation] =
        useState('')

    const [description, setDescription] =
        useState('')

    // ========================================================
    // PERSONNE / VICTIME
    // ========================================================

    const [personCategory, setPersonCategory] =
        useState('')

    const [victimLastName, setVictimLastName] =
        useState('')

    const [victimFirstName, setVictimFirstName] =
        useState('')

    // ========================================================
    // LIGNE HIÉRARCHIQUE
    // ========================================================

    const [projectManager, setProjectManager] =
        useState('')

    const [siteSupervisor, setSiteSupervisor] =
        useState('')

    // ========================================================
    // CONSÉQUENCES HUMAINES
    // ========================================================

    const [lostTime, setLostTime] =
        useState(false)

    const [lostDays, setLostDays] =
        useState(0)

    const [modifiedDuty, setModifiedDuty] =
        useState(false)

    const [modifiedDutyDays, setModifiedDutyDays] =
        useState(0)

    const [fatal, setFatal] =
        useState(false)

    const [
        permanentInjury,
        setPermanentInjury,
    ] = useState(false)

    // ========================================================
    // CONSÉQUENCES MATÉRIELLES
    // ========================================================

    const [materialDamage, setMaterialDamage] =
        useState(false)

    const [
        materialDamageDetails,
        setMaterialDamageDetails,
    ] = useState('')

    const [
        materialDamageCost,
        setMaterialDamageCost,
    ] = useState('')

    // ========================================================
    // CONSÉQUENCES ENVIRONNEMENTALES
    // ========================================================

    const [
        environmentalDamage,
        setEnvironmentalDamage,
    ] = useState(false)

    const [
        environmentalDamageType,
        setEnvironmentalDamageType,
    ] = useState('')

    const [
        environmentalDamageDetails,
        setEnvironmentalDamageDetails,
    ] = useState('')

    const [
        environmentalQuantity,
        setEnvironmentalQuantity,
    ] = useState('')

    const [
        environmentalUnit,
        setEnvironmentalUnit,
    ] = useState('')

    // ========================================================
    // INTERFACE
    // ========================================================

    const [isSaving, setIsSaving] =
        useState(false)

    const [error, setError] =
        useState<string | null>(null)

    // ========================================================
    // INITIALISATION
    // ========================================================

    useEffect(() => {
        const now = new Date()

        const localDate =
            new Date(
                now.getTime() -
                now.getTimezoneOffset() * 60000
            )
                .toISOString()
                .slice(0, 16)

        setEventDate(localDate)
    }, [])

    // ========================================================
    // PERSONNEL RISKY
    // ========================================================

    useEffect(() => {
        async function loadPeople() {
            try {
                const response = await fetch(
                    `${API_BASE_URL}/people`
                )

                if (!response.ok) {
                    return
                }

                const data = await response.json()

                if (Array.isArray(data)) {
                    setPeople(data)
                } else if (Array.isArray(data.people)) {
                    setPeople(data.people)
                }
            } catch {
                // Une personne externe doit pouvoir être
                // enregistrée même si Personnel est indisponible.
            }
        }

        loadPeople()
    }, [])

    // ========================================================
    // TYPE D'ÉVÉNEMENT
    // ========================================================

    function handleEventTypeChange(
        value: string
    ) {
        setEventType(value)

        // Le type principal active automatiquement
        // la conséquence correspondante.
        if (value === 'MATERIAL') {
            setMaterialDamage(true)
        }

        if (value === 'ENVIRONMENT') {
            setEnvironmentalDamage(true)
        }
    }

    // ========================================================
    // RECHERCHE DU LIEN PERSONNEL
    // ========================================================

    function findMatchingPersonId():
        number | null {

        const normalizedLastName =
            victimLastName
                .trim()
                .toLocaleLowerCase('fr')

        const normalizedFirstName =
            victimFirstName
                .trim()
                .toLocaleLowerCase('fr')

        if (
            !normalizedLastName ||
            !normalizedFirstName
        ) {
            return null
        }

        const person = people.find(
            (candidate) =>
                candidate.last_name
                    .trim()
                    .toLocaleLowerCase('fr') ===
                    normalizedLastName
                &&
                candidate.first_name
                    .trim()
                    .toLocaleLowerCase('fr') ===
                    normalizedFirstName
        )

        return person?.id ?? null
    }

    // ========================================================
    // CRÉATION
    // ========================================================

    async function handleSubmit(
        submitEvent: React.FormEvent<HTMLFormElement>
    ) {
        submitEvent.preventDefault()

        try {
            setIsSaving(true)
            setError(null)

            // ====================================================
            // SESSION
            // ====================================================

            const sessionToken =
                sessionStorage.getItem(
                    'risky_session_token'
                )

            if (!sessionToken) {
                throw new Error(
                    'Session RISKY absente. Veuillez vous identifier.'
                )
            }

            // ====================================================
            // LIEN PERSONNEL
            // ====================================================

            const matchedPersonId =
                findMatchingPersonId()

            // ====================================================
            // REQUÊTE
            // ====================================================

            const response = await fetch(
                `${API_BASE_URL}/events`,
                {
                    method: 'POST',

                    headers: {
                        'Content-Type':
                            'application/json',
                        'X-Session-Token':
                            sessionToken,
                    },

                    body: JSON.stringify({

                        // ========================================
                        // ÉVÉNEMENT
                        // ========================================

                        event_date: eventDate,
                        event_type: eventType,

                        organization_id: null,

                        location:
                            location.trim() || null,

                        description:
                            description.trim(),

                        // ========================================
                        // PERSONNE / VICTIME
                        // ========================================

                        person_id:
                            matchedPersonId,

                        person_category:
                            personCategory || null,

                        victim_last_name:
                            victimLastName.trim()
                            || null,

                        victim_first_name:
                            victimFirstName.trim()
                            || null,

                        // ========================================
                        // LIGNE HIÉRARCHIQUE
                        // ========================================

                        project_manager:
                            projectManager.trim()
                            || null,

                        site_supervisor:
                            siteSupervisor.trim()
                            || null,

                        // ========================================
                        // CONSÉQUENCES HUMAINES
                        // ========================================

                        lost_time:
                            lostTime,

                        lost_days:
                            lostTime
                                ? lostDays
                                : 0,

                        modified_duty:
                            modifiedDuty,

                        modified_duty_days:
                            modifiedDuty
                                ? modifiedDutyDays
                                : 0,

                        fatal,

                        permanent_injury:
                            permanentInjury,

                        // ========================================
                        // CONSÉQUENCES MATÉRIELLES
                        // ========================================

                        material_damage:
                            materialDamage,

                        material_damage_details:
                            materialDamage
                                ? (
                                    materialDamageDetails
                                        .trim()
                                    || null
                                )
                                : null,

                        material_damage_cost:
                            (
                                materialDamage &&
                                materialDamageCost !== ''
                            )
                                ? Number(
                                    materialDamageCost
                                )
                                : null,

                        // ========================================
                        // CONSÉQUENCES ENVIRONNEMENTALES
                        // ========================================

                        environmental_damage:
                            environmentalDamage,

                        environmental_damage_type:
                            environmentalDamage
                                ? (
                                    environmentalDamageType
                                    || null
                                )
                                : null,

                        environmental_damage_details:
                            environmentalDamage
                                ? (
                                    environmentalDamageDetails
                                        .trim()
                                    || null
                                )
                                : null,

                        environmental_quantity:
                            (
                                environmentalDamage &&
                                environmentalQuantity !== ''
                            )
                                ? Number(
                                    environmentalQuantity
                                )
                                : null,

                        environmental_unit:
                            environmentalDamage
                                ? (
                                    environmentalUnit
                                        .trim()
                                    || null
                                )
                                : null,
                    }),
                }
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    data.message ||
                    at('create.createError')
                )
            }

            if (
                data.status !== 'created' ||
                !data.event?.id
            ) {
                throw new Error(
                    data.message ||
                    at('create.notCreated')
                )
            }

            onCreated(data.event.id)

        } catch (error) {
            if (error instanceof Error) {
                setError(error.message)
            } else {
                setError(
                    'Une erreur est survenue.'
                )
            }
        } finally {
            setIsSaving(false)
        }
    }

    // ========================================================
    // RENDER
    // ========================================================

    return (
        <div className="accident-create">

            {/* ====================================================
                RETOUR
                ==================================================== */}

            <button
                className="accident-dossier-back"
                type="button"
                onClick={onBack}
            >
                <span aria-hidden="true">
                    ←
                </span>

                {at('create.back')}
            </button>

            {/* ====================================================
                EN-TÊTE
                ==================================================== */}

            <div className="accident-create__header">
                <div>
                    <h1>
                        {at('create.title')}
                    </h1>

                    <p>{at('create.intro')}</p>
                </div>
            </div>

            {/* ====================================================
                FORMULAIRE
                ==================================================== */}

            <form
                className="accident-create__form"
                onSubmit={handleSubmit}
            >

                {/* ================================================
                    INFORMATIONS GÉNÉRALES
                    ================================================ */}

                <section className="accident-create__section">
                    <h2>
                        {at('create.general')}
                    </h2>

                    <div className="accident-create__grid">

                        <label>
                            <span>
                                {at('create.eventType')}
                            </span>

                            <select
                                value={eventType}
                                onChange={(e) =>
                                    handleEventTypeChange(
                                        e.target.value
                                    )
                                }
                            >
                                <option value="ACCIDENT">
                                    {at('common.eventType.accident')}
                                </option>

                                <option value="INCIDENT">
                                    {at('common.eventType.incident')}
                                </option>

                                <option value="NEAR_MISS">
                                    {at('common.eventType.nearMiss')}
                                </option>

                                <option value="MATERIAL">
                                    {at('common.eventType.material')}
                                </option>

                                <option value="ENVIRONMENT">
                                    {at('common.eventType.environment')}
                                </option>
                            </select>
                        </label>

                        <label>
                            <span>
                                {at('create.dateTime')}
                            </span>

                            <input
                                type="datetime-local"
                                required
                                value={eventDate}
                                onChange={(e) =>
                                    setEventDate(
                                        e.target.value
                                    )
                                }
                            />
                        </label>

                        <label>
                            <span>
                                {at('overview.location')}
                            </span>

                            <input
                                type="text"
                                value={location}
                                onChange={(e) =>
                                    setLocation(
                                        e.target.value
                                    )
                                }
                                placeholder={at('create.locationPh')}
                            />
                        </label>

                        <label
                            className="accident-create__wide"
                        >
                            <span>
                                {at('create.eventTitle')}
                            </span>

                            <input
                                type="text"
                                required
                                value={description}
                                onChange={(e) =>
                                    setDescription(
                                        e.target.value
                                    )
                                }
                                placeholder={at('create.eventTitlePh')}
                            />
                        </label>
                    </div>
                </section>

                {/* ================================================
                    PERSONNE / CATÉGORIE
                    ================================================ */}

                <section className="accident-create__section">
                    <h2>
                        {at('create.personSection')}
                    </h2>

                    <div className="accident-create__grid">

                        <label>
                            <span>
                                {at('overview.category')}
                            </span>

                            <select
                                value={personCategory}
                                onChange={(e) =>
                                    setPersonCategory(
                                        e.target.value
                                    )
                                }
                            >
                                <option value="">
                                    {at('create.notApplicable')}
                                </option>

                                <option value="WORKER">
                                    {at('common.category.worker')}
                                </option>

                                <option value="EMPLOYEE">
                                    {at('common.category.employee')}
                                </option>

                                <option value="TEMPORARY">
                                    {at('common.category.temp')}
                                </option>

                                <option value="SUBCONTRACTOR">
                                    {at('common.category.contractor')}
                                </option>

                                <option value="OTHER">
                                    {at('common.category.other')}
                                </option>
                            </select>
                        </label>

                        <div />

                        <label>
                            <span>
                                {at('create.lastName')}
                            </span>

                            <input
                                type="text"
                                value={victimLastName}
                                onChange={(e) =>
                                    setVictimLastName(
                                        e.target.value
                                    )
                                }
                                placeholder={at('create.lastName')}
                            />
                        </label>

                        <label>
                            <span>
                                {at('create.firstName')}
                            </span>

                            <input
                                type="text"
                                value={victimFirstName}
                                onChange={(e) =>
                                    setVictimFirstName(
                                        e.target.value
                                    )
                                }
                                placeholder={at('create.firstName')}
                            />
                        </label>
                    </div>
                </section>

                {/* ================================================
                    LIGNE HIÉRARCHIQUE
                    ================================================ */}

                <section className="accident-create__section">
                    <h2>
                        {at('create.managementLine')}
                    </h2>

                    <div className="accident-create__grid">

                        <label>
                            <span>
                                PM
                            </span>

                            <input
                                type="text"
                                value={projectManager}
                                onChange={(e) =>
                                    setProjectManager(
                                        e.target.value
                                    )
                                }
                                placeholder={at('overview.projectManager')}
                            />
                        </label>

                        <label>
                            <span>
                                CE
                            </span>

                            <input
                                type="text"
                                value={siteSupervisor}
                                onChange={(e) =>
                                    setSiteSupervisor(
                                        e.target.value
                                    )
                                }
                                placeholder={at('overview.siteSupervisor')}
                            />
                        </label>
                    </div>
                </section>

                {/* ================================================
                    CONSÉQUENCES CONNUES
                    ================================================ */}

                <section className="accident-create__section">
                    <h2>
                        {at('create.knownConsequences')}
                    </h2>

                    {/* ============================================
                        HUMAINES
                        ============================================ */}

                    <div className="accident-create__subsection">
                        <h3>
                            {at('create.human')}
                        </h3>

                        <div className="accident-create__consequences">

                            <label>
                                <input
                                    type="checkbox"
                                    checked={lostTime}
                                    onChange={(e) =>
                                        setLostTime(
                                            e.target.checked
                                        )
                                    }
                                />

                                <span>
                                    {at('create.lostTime')}
                                </span>
                            </label>

                            {lostTime && (
                                <label>
                                    <span>
                                        {at('create.days')}
                                    </span>

                                    <input
                                        type="number"
                                        min="0"
                                        value={lostDays}
                                        onChange={(e) =>
                                            setLostDays(
                                                Number(
                                                    e.target.value
                                                )
                                            )
                                        }
                                    />
                                </label>
                            )}

                            <label>
                                <input
                                    type="checkbox"
                                    checked={modifiedDuty}
                                    onChange={(e) =>
                                        setModifiedDuty(
                                            e.target.checked
                                        )
                                    }
                                />

                                <span>
                                    {at('create.modifiedDuty')}
                                </span>
                            </label>

                            {modifiedDuty && (
                                <label>
                                    <span>
                                        {at('create.days')}
                                    </span>

                                    <input
                                        type="number"
                                        min="0"
                                        value={
                                            modifiedDutyDays
                                        }
                                        onChange={(e) =>
                                            setModifiedDutyDays(
                                                Number(
                                                    e.target.value
                                                )
                                            )
                                        }
                                    />
                                </label>
                            )}

                            <label>
                                <input
                                    type="checkbox"
                                    checked={
                                        permanentInjury
                                    }
                                    onChange={(e) =>
                                        setPermanentInjury(
                                            e.target.checked
                                        )
                                    }
                                />

                                <span>
                                    {at('create.permanentInjury')}
                                </span>
                            </label>

                            <label>
                                <input
                                    type="checkbox"
                                    checked={fatal}
                                    onChange={(e) =>
                                        setFatal(
                                            e.target.checked
                                        )
                                    }
                                />

                                <span>
                                    {at('create.death')}
                                </span>
                            </label>
                        </div>
                    </div>

                    {/* ============================================
                        MATÉRIELLES
                        ============================================ */}

                    <div className="accident-create__subsection">
                        <h3>
                            {at('create.material')}
                        </h3>

                        <label className="accident-create__check">
                            <input
                                type="checkbox"
                                checked={materialDamage}
                                onChange={(e) =>
                                    setMaterialDamage(
                                        e.target.checked
                                    )
                                }
                            />

                            <span>
                                {at('create.materialDamage')}
                            </span>
                        </label>

                        {materialDamage && (
                            <div className="accident-create__grid accident-create__details">

                                <label className="accident-create__wide">
                                    <span>
                                        {at('create.damageDescription')}
                                    </span>

                                    <textarea
                                        value={
                                            materialDamageDetails
                                        }
                                        onChange={(e) =>
                                            setMaterialDamageDetails(
                                                e.target.value
                                            )
                                        }
                                        rows={3}
                                        placeholder="Description succincte des dommages..."
                                    />
                                </label>

                                <label>
                                    <span>
                                        {at('create.estimatedCost')}
                                    </span>

                                    <input
                                        type="number"
                                        min="0"
                                        step="0.01"
                                        value={
                                            materialDamageCost
                                        }
                                        onChange={(e) =>
                                            setMaterialDamageCost(
                                                e.target.value
                                            )
                                        }
                                    />
                                </label>
                            </div>
                        )}
                    </div>

                    {/* ============================================
                        ENVIRONNEMENTALES
                        ============================================ */}

                    <div className="accident-create__subsection">
                        <h3>
                            {at('create.environmental')}
                        </h3>

                        <label className="accident-create__check">
                            <input
                                type="checkbox"
                                checked={
                                    environmentalDamage
                                }
                                onChange={(e) =>
                                    setEnvironmentalDamage(
                                        e.target.checked
                                    )
                                }
                            />

                            <span>
                                {at('create.environmentalImpact')}
                            </span>
                        </label>

                        {environmentalDamage && (
                            <div className="accident-create__grid accident-create__details">

                                <label>
                                    <span>
                                        {at('create.impactNature')}
                                    </span>

                                    <select
                                        value={
                                            environmentalDamageType
                                        }
                                        onChange={(e) =>
                                            setEnvironmentalDamageType(
                                                e.target.value
                                            )
                                        }
                                    >
                                        <option value="">
                                            {at('common.notProvidedF')}
                                        </option>

                                        <option value="SPILL">
                                            {at('create.spill')}
                                        </option>

                                        <option value="LEAK">
                                            {at('create.leak')}
                                        </option>

                                        <option value="RELEASE">
                                            {at('create.release')}
                                        </option>

                                        <option value="SOIL">
                                            {at('create.soil')}
                                        </option>

                                        <option value="WATER">
                                            {at('create.water')}
                                        </option>

                                        <option value="AIR">
                                            {at('create.air')}
                                        </option>

                                        <option value="OTHER">
                                            {at('common.category.other')}
                                        </option>
                                    </select>
                                </label>

                                <div />

                                <label className="accident-create__wide">
                                    <span>
                                        {at('create.impactDescription')}
                                    </span>

                                    <textarea
                                        value={
                                            environmentalDamageDetails
                                        }
                                        onChange={(e) =>
                                            setEnvironmentalDamageDetails(
                                                e.target.value
                                            )
                                        }
                                        rows={3}
                                        placeholder="Description succincte..."
                                    />
                                </label>

                                <label>
                                    <span>
                                        {at('create.quantity')}
                                    </span>

                                    <input
                                        type="number"
                                        min="0"
                                        step="0.01"
                                        value={
                                            environmentalQuantity
                                        }
                                        onChange={(e) =>
                                            setEnvironmentalQuantity(
                                                e.target.value
                                            )
                                        }
                                    />
                                </label>

                                <label>
                                    <span>
                                        {at('overview.unit')}
                                    </span>

                                    <input
                                        type="text"
                                        value={
                                            environmentalUnit
                                        }
                                        onChange={(e) =>
                                            setEnvironmentalUnit(
                                                e.target.value
                                            )
                                        }
                                        placeholder={at('create.unitPh')}
                                    />
                                </label>
                            </div>
                        )}
                    </div>
                </section>

                {/* ================================================
                    ERREUR
                    ================================================ */}

                {error && (
                    <div className="accident-create__error">
                        {error}
                    </div>
                )}

                {/* ================================================
                    ACTIONS
                    ================================================ */}

                <div className="accident-create__actions">

                    <button
                        className="accident-dossier-back"
                        type="button"
                        onClick={onBack}
                    >
                        {at('common.cancel')}
                    </button>

                    <button
                        className="accident-register-create"
                        type="submit"
                        disabled={isSaving}
                    >
                        {isSaving
                            ? at('causeTree.creating')
                            : 'Créer le dossier'}
                    </button>
                </div>
            </form>
        </div>
    )
}

export default AccidentCreatePage