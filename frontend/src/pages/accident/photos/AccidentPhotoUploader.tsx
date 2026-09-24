import {
    useRef,
    useState,
} from 'react'

import type {
    ChangeEvent,
    ClipboardEvent,
    DragEvent,
} from 'react'
import { at } from '../accidentI18n'
import { API_BASE_URL } from '../accidentApi'


// ========================================================
// TYPES
// ========================================================

type AccidentPhotoUploaderProps = {
    eventId: number
    photoCount: number
    maxPhotos: number
    onUploaded: () => Promise<void>
}


// ========================================================
// CONFIGURATION
// ========================================================

const MAX_FILE_SIZE = 15 * 1024 * 1024

const ALLOWED_TYPES = [
    'image/jpeg',
    'image/png',
]


// ========================================================
// UPLOADER
// ========================================================

export default function AccidentPhotoUploader({
    eventId,
    photoCount,
    maxPhotos,
    onUploaded,
}: AccidentPhotoUploaderProps) {
    const inputRef = useRef<HTMLInputElement>(null)

    const [uploading, setUploading] = useState(false)
    const [dragging, setDragging] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const remainingPhotos = Math.max(
        maxPhotos - photoCount,
        0,
    )


    // ========================================================
    // VALIDATION
    // ========================================================

    const validateFile = (file: File): string | null => {
        const extension = file.name
            .toLowerCase()
            .split('.')
            .pop()

        const validExtension =
            extension === 'jpg' ||
            extension === 'jpeg' ||
            extension === 'png'

        const validMimeType =
            file.type === '' ||
            ALLOWED_TYPES.includes(file.type)

        if (!validExtension || !validMimeType) {
            return at('photos.formatError')
        }

        if (file.size > MAX_FILE_SIZE) {
            return at('photos.sizeError')
        }

        return null
    }


    // ========================================================
    // ENVOI
    // ========================================================

    const uploadFiles = async (files: File[]) => {
        if (uploading || files.length === 0) {
            return
        }

        if (remainingPhotos <= 0) {
            setError(
                at('photos.limitError', { max: maxPhotos }),
            )
            return
        }

        const filesToUpload = files.slice(
            0,
            remainingPhotos,
        )

        const invalidFile = filesToUpload.find(
            (file) => validateFile(file) !== null,
        )

        if (invalidFile) {
            setError(validateFile(invalidFile))
            return
        }

        try {
            setUploading(true)
            setError(null)

            for (const file of filesToUpload) {
                const formData = new FormData()
                formData.append('file', file)

                const sessionToken = sessionStorage.getItem(
                    'risky_session_token',
                )

                const headers: HeadersInit = {}

                if (sessionToken) {
                    headers['X-Session-Token'] = sessionToken
                }

                const response = await fetch(
                    `${API_BASE_URL}/events/${eventId}/photos`,
                    {
                        method: 'POST',
                        headers,
                        body: formData,
                    },
                )

                if (!response.ok) {
                    const data = await response
                        .json()
                        .catch(() => null)

                    throw new Error(
                        data?.detail ??
                        `${at('photos.uploadError')} (${response.status})`,
                    )
                }
            }

            await onUploaded()
        } catch (err) {
            console.error(err)

            setError(
                err instanceof Error
                    ? err.message
                    : at('photos.uploadError'),
            )
        } finally {
            setUploading(false)

            if (inputRef.current) {
                inputRef.current.value = ''
            }
        }
    }


    // ========================================================
    // PARCOURIR
    // ========================================================

    const handleFileInput = (
        event: ChangeEvent<HTMLInputElement>,
    ) => {
        const files = Array.from(
            event.target.files ?? [],
        )

        void uploadFiles(files)
    }


    // ========================================================
    // GLISSER-DÉPOSER
    // ========================================================

    const handleDragOver = (
        event: DragEvent<HTMLDivElement>,
    ) => {
        event.preventDefault()

        if (!uploading && remainingPhotos > 0) {
            setDragging(true)
        }
    }

    const handleDragLeave = (
        event: DragEvent<HTMLDivElement>,
    ) => {
        event.preventDefault()
        setDragging(false)
    }

    const handleDrop = (
        event: DragEvent<HTMLDivElement>,
    ) => {
        event.preventDefault()
        setDragging(false)

        const files = Array.from(
            event.dataTransfer.files,
        )

        void uploadFiles(files)
    }


    // ========================================================
    // COLLER — CTRL+V
    // ========================================================

    const handlePaste = (
        event: ClipboardEvent<HTMLDivElement>,
    ) => {
        const files = Array.from(
            event.clipboardData.files,
        )

        if (files.length === 0) {
            return
        }

        event.preventDefault()
        void uploadFiles(files)
    }


    // ========================================================
    // AFFICHAGE
    // ========================================================

    return (
        <div className="accident-photo-uploader">
            <div
                className={[
                    'accident-photo-uploader__dropzone',
                    dragging
                        ? 'accident-photo-uploader__dropzone--dragging'
                        : '',
                    remainingPhotos === 0
                        ? 'accident-photo-uploader__dropzone--disabled'
                        : '',
                ]
                    .filter(Boolean)
                    .join(' ')}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onPaste={handlePaste}
                tabIndex={remainingPhotos > 0 ? 0 : -1}
            >
                <div className="accident-photo-uploader__main">
                    {uploading
                        ? at('photos.uploading')
                        : remainingPhotos === 0
                            ? at('photos.maximumReached')
                            : at('photos.dropzone')}
                </div>

                <div className="accident-photo-uploader__hint">
                    {at('photos.formats', {
                        count: photoCount,
                        max: maxPhotos,
                    })}
                </div>

                <input
                    ref={inputRef}
                    type="file"
                    accept="image/jpeg,image/png"
                    multiple
                    hidden
                    onChange={handleFileInput}
                />

                <button
                    type="button"
                    className="accident-photo-uploader__browse"
                    disabled={
                        uploading ||
                        remainingPhotos === 0
                    }
                    onClick={() => inputRef.current?.click()}
                >
                    {at('photos.browse')}
                </button>
            </div>

            {error && (
                <div className="accident-photo-uploader__error">
                    {error}
                </div>
            )}
        </div>
    )
}