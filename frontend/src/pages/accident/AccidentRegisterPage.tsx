import { at } from './accidentI18n'
import { useEffect, useMemo, useState } from "react";

import './AccidentRegisterPage.css'

type EventRow = {
    id: number;
    event_number: string;
    event_date: string;
    event_type: string;

    person_id: number | null;
    person: string | null;

    organization_id: number | null;
    organization: string | null;

    location: string | null;
    description: string | null;

    lost_time: boolean;
    lost_days: number;

    modified_duty: boolean;
    modified_duty_days: number;

    fatal: boolean;
    permanent_injury: boolean;

    analysis_type: string | null;
    status: string;
};

type EventsResponse = {
    count: number;
    events: EventRow[];
};

type AccidentRegisterPageProps = {
    onOpenEvent: (eventId: number) => void
    onCreateEvent: () => void
}

const API_BASE_URL = "http://127.0.0.1:8000";

function formatEventType(eventType: string) {
    switch (eventType) {
        case "ACCIDENT":
            return at('common.eventType.accident');

        case "INCIDENT":
            return at('common.eventType.incident');

        case "NEAR_MISS":
            return "Presqu'accident";

        default:
            return eventType;
    }
}

function formatAnalysisType(analysisType: string | null) {
    switch (analysisType) {
        case "NORMAL":
            return at('overview.normal');

        case "ADVANCED":
            return at('overview.inDepth');

        default:
            return at('register.toDefine');
    }
}

function formatStatus(status: string) {
    switch (status) {
        case 'OPEN':
            return at('dossier.status.open')

        case 'IN_PROGRESS':
            return at('dossier.status.inProgress')

        case 'ACCEPTED':
            return at('dossier.status.accepted')

        case 'REJECTED':
            return at('dossier.status.rejected')

        case 'CLOSED':
            return at('dossier.status.closed')

        default:
            return status
    }
}

function buildConsequences(event: EventRow) {
    const consequences: string[] = [];

    if (event.fatal) {
        consequences.push(at('create.death'));
    }

    if (event.permanent_injury) {
        consequences.push(at('register.permanentInjury'));
    }

    if (event.lost_time) {
        consequences.push(
            `${event.lost_days} j arrêt`
        );
    }

    if (event.modified_duty) {
        consequences.push(
            `${event.modified_duty_days} j travail adapté`
        );
    }

    if (consequences.length === 0) {
        return at('register.noConsequence');
    }

    return consequences.join(" · ");
}

export default

    function AccidentRegisterPage({
        onOpenEvent,
        onCreateEvent,

    }: AccidentRegisterPageProps) {
    const [events, setEvents] = useState<EventRow[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [search, setSearch] = useState("");

    useEffect(() => {
        async function loadEvents() {
            try {
                setLoading(true);
                setError(null);

                const response = await fetch(
                    `${API_BASE_URL}/events`
                );

                if (!response.ok) {
                    throw new Error(
                        `Erreur HTTP ${response.status}`
                    );
                }

                const data: EventsResponse =
                    await response.json();

                setEvents(data.events);
            } catch (err) {
                console.error(err);

                setError(
                    at('register.loadError')
                );
            } finally {
                setLoading(false);
            }
        }

        loadEvents();
    }, []);

    const filteredEvents = useMemo(() => {
        const value = search.trim().toLowerCase();

        if (!value) {
            return events;
        }

        return events.filter((event) => {
            const searchable = [
                event.event_number,
                event.person,
                event.organization,
                event.location,
                event.description,
                formatEventType(event.event_type),
                formatAnalysisType(event.analysis_type),
                formatStatus(event.status),
            ]
                .filter(Boolean)
                .join(" ")
                .toLowerCase();

            return searchable.includes(value);
        });
    }, [events, search]);


    return (
        <div className="accident-register-page">
            {/* ========================================================
    EN-TÊTE DU REGISTRE
    ======================================================== */}

            <div className="accident-register-header">
                <div>
                    <h1>{at('register.title')}</h1>

                    <p>
                        {at('register.description')}
                    </p>
                </div>

                <button
                    className="accident-register-create"
                    type="button"
                    onClick={onCreateEvent}
                >
                    {at('register.newEvent')}
                </button>
            </div>

            {/* ========================================================
    FIN EN-TÊTE DU REGISTRE
    ======================================================== */}

            <div className="accident-register-toolbar">
                <input
                    type="search"
                    placeholder="Rechercher..."
                    value={search}
                    onChange={(event) =>
                        setSearch(event.target.value)
                    }
                />

                <div className="accident-register-count">
                    {filteredEvents.length} événement
                    {filteredEvents.length > 1 ? "s" : ""}
                </div>
            </div>

            {
                loading && (
                    <div className="accident-register-message">
                        {at('common.loading')}
                    </div>
                )
            }

            {
                error && (
                    <div className="accident-register-error">
                        {error}
                    </div>
                )
            }

            {
                !loading && !error && (
                    <div className="accident-register-table-wrapper">
                        <table className="accident-register-table">
                            <thead>
                                <tr>
                                    <th>{at('register.number')}</th>
                                    <th>{at('overview.date')}</th>
                                    <th>{at('overview.person')}</th>
                                    <th>{at('overview.type')}</th>
                                    <th>{at('register.eventTitle')}</th>
                                    <th>{at('overview.consequences')}</th>
                                    <th>{at('register.analysis')}</th>
                                    <th>{at('register.status')}</th>
                                </tr>
                            </thead>

                            <tbody>
                                {filteredEvents.map((event) => (
                                    <tr
                                        key={event.id}
                                        onClick={() =>
                                            onOpenEvent(event.id)
                                        }
                                        className="accident-register-row"
                                    >
                                        <td>
                                            <strong>
                                                {event.event_number}
                                            </strong>
                                        </td>

                                        <td>
                                            {new Date(
                                                event.event_date
                                            ).toLocaleDateString("fr-BE")}
                                        </td>

                                        <td>
                                            {event.person ?? "—"}
                                        </td>

                                        <td>
                                            <span
                                                className={`accident-register-badge ${event.event_type === 'ACCIDENT'
                                                    ? 'accident-register-badge--accident'
                                                    : event.event_type === 'INCIDENT'
                                                        ? 'accident-register-badge--incident'
                                                        : 'accident-register-badge--near-miss'
                                                    }`}
                                            >
                                                {formatEventType(event.event_type)}
                                            </span>
                                        </td>

                                        <td>
                                            {event.description ?? "—"}
                                        </td>

                                        <td>
                                            <span className="accident-register-consequence">
                                                {buildConsequences(event)}
                                            </span>
                                        </td>

                                        <td>
                                            <span
                                                className={`accident-register-badge ${event.analysis_type === 'ADVANCED'
                                                    ? 'accident-register-badge--advanced'
                                                    : 'accident-register-badge--normal'
                                                    }`}
                                            >
                                                {formatAnalysisType(event.analysis_type)}
                                            </span>
                                        </td>

                                        <td>
                                            <span
                                                className={`accident-register-badge accident-register-badge--status-${event.status
                                                    .toLowerCase()
                                                    .replace('_', '-')}`}
                                            >
                                                {formatStatus(event.status)}
                                            </span>
                                        </td>
                                    </tr>
                                ))}

                                {filteredEvents.length === 0 && (
                                    <tr>
                                        <td
                                            colSpan={8}
                                            className="accident-register-empty"
                                        >
                                            {at('register.none')}
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                )
            }
        </div >
    );
}