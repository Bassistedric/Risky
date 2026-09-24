import { useCallback, useEffect, useState } from 'react'

import { at } from '../accidentI18n'
import { API_BASE_URL } from '../accidentApi'
import AccidentPhotoCard from './AccidentPhotoCard'
import AccidentPhotoUploader from './AccidentPhotoUploader'
import './AccidentPhotosSection.css'


// ========================================================
// TYPES
// ========================================================

export type EventPhoto = {
    id: number
    event_id: number
    filename: string
    original_filename: string
    content_type: string
    file_size: number
    caption: string | null
    sort_order: number
    uploaded_by_person_id: number | null
    created_at: string
}

type EventPhotoListResponse = {
    event_id: number
    photos: EventPhoto[]
    count: number
    max_photos: number
}

type AccidentPhotosSectionProps = {
    eventId: number
}


// ========================================================
// SECTION PHOTOS
// ========================================================

export default function AccidentPhotosSection({
    eventId,
}: AccidentPhotosSectionProps) {
    const [photos, setPhotos] = useState<EventPhoto[]>([])
    const [maxPhotos, setMaxPhotos] = useState(4)

    const [open, setOpen] = useState(false)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)


    // ========================================================
    // CHARGEMENT
    // ========================================================

    const loadPhotos = useCallback(async () => {
        try {
            setLoading(true)
            setError(null)

            const response = await fetch(
                `${API_BASE_URL}/events/${eventId}/photos`,
            )

            if (!response.ok) {
                throw new Error(
                    `${at('photos.loadError')} (${response.status})`,
                )
            }

            const data: EventPhotoListResponse = await response.json()

            setPhotos(data.photos)
            setMaxPhotos(data.max_photos)
        } catch (err) {
            console.error(err)
            setError(at('photos.loadError'))
        } finally {
            setLoading(false)
        }
    }, [eventId])

    useEffect(() => {
        void loadPhotos()
    }, [loadPhotos])


    // ========================================================
    // AFFICHAGE
    // ========================================================

    return (
        <section className="accident-photos">
            <button
                type="button"
                className="accident-photos__header"
                onClick={() => setOpen((current) => !current)}
                aria-expanded={open}
            >
                <span className="accident-photos__chevron">
                    {open ? '▾' : '▸'}
                </span>

                <span className="accident-photos__title">
                    {at('photos.title')}
                </span>

                <span className="accident-photos__summary">
                    {loading
                        ? '...'
                        : photos.length > 0
                            ? `${photos.length}/${maxPhotos}`
                            : at('photos.addPhotos')}
                </span>
            </button>

            {open && (
                <div className="accident-photos__content">
                    {error && (
                        <div className="accident-photos__error">
                            {error}
                        </div>
                    )}

                    <AccidentPhotoUploader
                        eventId={eventId}
                        photoCount={photos.length}
                        maxPhotos={maxPhotos}
                        onUploaded={loadPhotos}
                    />

                    {photos.length > 0 && (
                        <div className="accident-photos__grid">
                            {photos.map((photo) => (
                                <AccidentPhotoCard
                                    key={photo.id}
                                    eventId={eventId}
                                    photo={photo}
                                    onChanged={loadPhotos}
                                />
                            ))}
                        </div>
                    )}
                </div>
            )}
        </section>
    )
}