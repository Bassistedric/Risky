import {
    useEffect,
    useState,
} from 'react'

import type {
    ChangeEvent,
} from 'react'

import { API_BASE_URL } from '../accidentApi'
import type { EventPhoto } from './AccidentPhotosSection'
import { at } from '../accidentI18n'


// ========================================================
// TYPES
// ========================================================

type AccidentPhotoCardProps = {
    eventId: number
    photo: EventPhoto
    onChanged: () => Promise<void>
}


// ========================================================
// CARTE PHOTO
// ========================================================

export default function AccidentPhotoCard({
    eventId,
    photo,
    onChanged,
}: AccidentPhotoCardProps) {
    const [caption, setCaption] = useState(
        photo.caption ?? '',
    )

    const [saving, setSaving] = useState(false)
    const [deleting, setDeleting] = useState(false)
    const [confirmDelete, setConfirmDelete] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const imageUrl =
        `${API_BASE_URL}/events/${eventId}` +
        `/photos/${photo.id}/file`


    // ========================================================
    // SYNCHRONISATION
    // ========================================================

    useEffect(() => {
        setCaption(photo.caption ?? '')
    }, [photo.caption])


    // ========================================================
    // TOKEN DE SESSION
    // ========================================================

    const getHeaders = (): HeadersInit => {
        const sessionToken = sessionStorage.getItem(
            'risky_session_token',
        )

        if (!sessionToken) {
            return {
                'Content-Type': 'application/json',
            }
        }

        return {
            'Content-Type': 'application/json',
            'X-Session-Token': sessionToken,
        }
    }


    // ========================================================
    // LÉGENDE
    // ========================================================

    const saveCaption = async () => {
        if (caption === (photo.caption ?? '')) {
            return
        }

        try {
            setSaving(true)
            setError(null)

            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}/photos/${photo.id}`,
                {
                    method: 'PUT',
                    headers: getHeaders(),
                    body: JSON.stringify({
                        caption,
                    }),
                },
            )

            if (!response.ok) {
                const data = await response
                    .json()
                    .catch(() => null)

                throw new Error(
                    data?.detail ??
                    `${at('photos.captionError')} (${response.status})`,
                )
            }

            await onChanged()
        } catch (err) {
            console.error(err)

            setError(
                err instanceof Error
                    ? err.message
                    : at('photos.captionError'),
            )
        } finally {
            setSaving(false)
        }
    }

    const handleCaptionChange = (
        event: ChangeEvent<HTMLInputElement>,
    ) => {
        setCaption(event.target.value)
    }


    // ========================================================
    // SUPPRESSION
    // ========================================================

    const deletePhoto = async () => {


        try {
            setDeleting(true)
            setError(null)

            const sessionToken = sessionStorage.getItem(
                'risky_session_token',
            )

            const headers: HeadersInit = {}

            if (sessionToken) {
                headers['X-Session-Token'] = sessionToken
            }

            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}/photos/${photo.id}`,
                {
                    method: 'DELETE',
                    headers,
                },
            )

            if (!response.ok) {
                const data = await response
                    .json()
                    .catch(() => null)

                throw new Error(
                    data?.detail ??
                    `${at('photos.deleteError')} (${response.status})`,
                )
            }

            await onChanged()
            setConfirmDelete(false)

        } catch (err) {
            console.error(err)

            setError(
                err instanceof Error
                    ? err.message
                    : at('photos.deleteError')
            )
        } finally {
            setDeleting(false)
        }
    }

    // ========================================================
    // AFFICHAGE
    // ========================================================

    return (
        <article className="accident-photo-card">
            <a
                className="accident-photo-card__preview"
                href={imageUrl}
                target="_blank"
                rel="noreferrer"
                title={photo.original_filename}
            >
                <img
                    src={imageUrl}
                    alt={caption || photo.original_filename}
                    className="accident-photo-card__image"
                />
            </a>

            <div className="accident-photo-card__body">
                <input
                    type="text"
                    value={caption}
                    maxLength={500}
                    className="accident-photo-card__caption"
                    placeholder={at('photos.captionPlaceholder')}
                    disabled={saving || deleting}
                    onChange={handleCaptionChange}
                    onBlur={() => void saveCaption()}
                    onKeyDown={(event) => {
                        if (event.key === 'Enter') {
                            event.currentTarget.blur()
                        }
                    }}
                />

                <div className="accident-photo-card__actions">
                    <span className="accident-photo-card__filename">
                        {photo.original_filename}
                    </span>

                    {!confirmDelete ? (
                        <button
                            type="button"
                            className="accident-photo-card__delete"
                            disabled={saving || deleting}
                            onClick={() => setConfirmDelete(true)}
                        >
                            {at('photos.delete')}
                        </button>
                    ) : (
                        <div className="accident-photo-card__delete-confirm">
                            <span>
                                {at('photos.deleteQuestion')}
                            </span>

                            <button
                                type="button"
                                className="accident-photo-card__delete-cancel"
                                disabled={deleting}
                                onClick={() => setConfirmDelete(false)}
                            >
                                {at('photos.cancel')}
                            </button>

                            <button
                                type="button"
                                className="accident-photo-card__delete-confirm-button"
                                disabled={deleting}
                                onClick={() => void deletePhoto()}
                            >
                                {deleting
                                    ? at('photos.deleting')
                                    : at('photos.confirm')}
                            </button>
                        </div>
                    )}
                </div>

                {saving && (
                    <div className="accident-photo-card__saving">
                        {at('photos.saving')}
                    </div>
                )}

                {error && (
                    <div className="accident-photo-card__error">
                        {error}
                    </div>
                )}
            </div>
        </article>
    )
}