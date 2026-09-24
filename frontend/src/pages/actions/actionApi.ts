import type {
    ActionListResponse,
    RiskyAction,
} from './actionTypes'


// ========================================================
// CONFIGURATION API
// ========================================================

const API_BASE_URL = 'http://127.0.0.1:8000'


// ========================================================
// SESSION
// ========================================================

function getSessionToken(): string | null {
    return sessionStorage.getItem(
        'risky_session_token',
    )
}


// ========================================================
// HEADERS
// ========================================================

function getHeaders(): HeadersInit {
    const token = getSessionToken()

    return {
        'Content-Type': 'application/json',
        ...(token
            ? {
                'X-Session-Token': token,
            }
            : {}),
    }
}


// ========================================================
// ACTIONS D'UN ÉVÉNEMENT
// ========================================================

export async function getEventActions(
    eventId: number,
): Promise<RiskyAction[]> {
    const response = await fetch(
        `${API_BASE_URL}/events/${eventId}/actions`,
        {
            headers: getHeaders(),
        },
    )

    if (!response.ok) {
        throw new Error(
            `Unable to load event actions: ${response.status}`,
        )
    }

    const data =
        (await response.json()) as ActionListResponse

    return data.actions ?? []
}

// ========================================================
// LISTE TRANSVERSE DES ACTIONS
// ========================================================

export async function getActions(
    originType?: string,
): Promise<RiskyAction[]> {
    const params = new URLSearchParams()

    if (originType) {
        params.set(
            'origin_type',
            originType,
        )
    }

    const query = params.toString()

    const response = await fetch(
        `${API_BASE_URL}/actions${
            query ? `?${query}` : ''
        }`,
        {
            headers: getHeaders(),
        },
    )

    if (!response.ok) {
        throw new Error(
            `Unable to load actions: ${response.status}`,
        )
    }

    const data =
        (await response.json()) as ActionListResponse

    return data.actions ?? []
}