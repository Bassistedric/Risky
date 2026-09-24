/* ========================================================
   RISKY — API RAPPORTS
   ======================================================== */

import type {
    AccidentReportPreviewData,
} from './reportTypes'


export const API_BASE_URL =
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

/* ========================================================
   PDF RAPPORT D'ANALYSE
   ======================================================== */

export async function downloadAnalysisReportPdf(
    eventId: number,
    language: string,
): Promise<void> {
    const token = getSessionToken()
    const response = await fetch(
        `${API_BASE_URL}/events/${eventId}/reports/analysis/pdf?language=${encodeURIComponent(language)}`,
        { headers: token ? { 'X-Session-Token': token } : {} },
    )
    if (!response.ok) {
        throw new Error(`Impossible de générer le PDF (${response.status}).`)
    }
    const blob = await response.blob()
    const disposition = response.headers.get('Content-Disposition') ?? ''
    const match = disposition.match(/filename="?([^";]+)"?/i)
    const filename = match?.[1] ?? `RISKY_event_${eventId}_rapport_analyse.pdf`
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
}


/* ========================================================
   SAFETY FLASH CFE
   ======================================================== */

export async function getSafetyFlashPreview(eventId: number): Promise<any> {
    const token = getSessionToken()
    const response = await fetch(`${API_BASE_URL}/events/${eventId}/reports/safety-flash/preview`, {
        headers: token ? { 'X-Session-Token': token } : {},
    })
    if (!response.ok) throw new Error(`Impossible de charger le Safety Flash (${response.status}).`)
    return response.json()
}

export async function downloadSafetyFlashPdf(eventId: number, language: string, draft: unknown): Promise<void> {
    const token = getSessionToken()
    const response = await fetch(`${API_BASE_URL}/events/${eventId}/reports/safety-flash/pdf?language=${encodeURIComponent(language)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token ? { 'X-Session-Token': token } : {}) },
        body: JSON.stringify(draft),
    })
    if (!response.ok) throw new Error(`Impossible de générer le Safety Flash (${response.status}).`)
    const blob = await response.blob()
    const disposition = response.headers.get('Content-Disposition') ?? ''
    const match = disposition.match(/filename="?([^";]+)"?/i)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = match?.[1] ?? `RISKY_event_${eventId}_Safety_Flash.pdf`
    document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url)
}
