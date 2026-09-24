/* ========================================================
   RISKY — API RAPPORTS
   ======================================================== */

import type {
    AccidentReportPreviewData,
} from './reportTypes'


const API_BASE_URL =
    'http://127.0.0.1:8000'


/* ========================================================
   SESSION
   ======================================================== */

function getSessionToken(): string | null {
    return sessionStorage.getItem(
        'risky_session_token',
    )
}


/* ========================================================
   APERÇU RAPPORT D'ANALYSE
   ======================================================== */

export async function getAnalysisReportPreview(
    eventId: number,
): Promise<AccidentReportPreviewData> {
    const token = getSessionToken()

    const response = await fetch(
        `${API_BASE_URL}/events/${eventId}/reports/analysis/preview`,
        {
            headers: token
                ? {
                      'X-Session-Token': token,
                  }
                : {},
        },
    )

    if (!response.ok) {
        throw new Error(
            `Impossible de charger l'aperçu du rapport (${response.status}).`,
        )
    }

    return response.json()
}