import { useState } from 'react'


import './LoginPage.css'


const API_BASE_URL = 'http://127.0.0.1:8000'


type LoginPageProps = {
    onAuthenticated: () => void
}


export default function LoginPage({
    onAuthenticated,
}: LoginPageProps) {
    const [initials, setInitials] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)


    // ========================================================
    // IDENTIFICATION
    // ========================================================

    async function handleSubmit(
        event: React.SubmitEvent<HTMLFormElement>,
    ) {
        event.preventDefault()

        const cleanInitials = initials.trim()

        if (!cleanInitials) {
            setError('Veuillez renseigner vos initiales.')
            return
        }

        setIsLoading(true)
        setError(null)

        try {
            const response = await fetch(
                `${API_BASE_URL}/session/login`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        initials: cleanInitials,
                    }),
                },
            )

            const data = await response.json()

            if (
                !response.ok ||
                data.status !== 'authenticated' ||
                !data.session_token
            ) {
                throw new Error(
                    data.message ||
                    data.detail ||
                    'Identification impossible.',
                )
            }

            sessionStorage.setItem(
                'risky_session_token',
                data.session_token,
            )

            onAuthenticated()
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : 'Identification impossible.',
            )
        } finally {
            setIsLoading(false)
        }
    }


    // ========================================================
    // AFFICHAGE
    // ========================================================

    return (
        <main className="login-page">
            <section className="login-card">

                {/* ====================================================
          IDENTITÉ RISKY
          ==================================================== */}

                <div className="login-brand">
                    <div className="login-brand__icon">
                        R
                    </div>

                    <div className="login-brand__text">
                        <strong>RISKY</strong>

                        <span>Q H S E</span>
                    </div>
                </div>


                {/* ====================================================
          IDENTIFICATION
          ==================================================== */}

                <div className="login-heading">
                    <h1>Identification</h1>

                    <p>
                        Identifiez-vous pour accéder à votre
                        environnement Risky.
                    </p>
                </div>


                {/* ====================================================
          FORMULAIRE
          ==================================================== */}

                <form
                    className="login-form"
                    onSubmit={handleSubmit}
                >
                    <label htmlFor="login-initials">
                        Initiales
                    </label>

                    <div className="login-input-wrapper">
                        <input
                            id="login-initials"
                            type="text"
                            value={initials}
                            onChange={(event) => {
                                setInitials(event.target.value)
                            }}
                            placeholder="Ex : Jean Démo → JED"
                            autoComplete="off"
                            autoFocus
                            disabled={isLoading}
                        />

                        <svg
                            className="login-input-icon"
                            viewBox="0 0 24 24"
                            aria-hidden="true"
                        >
                            <circle
                                cx="12"
                                cy="8"
                                r="4"
                            />

                            <path
                                d="M5 20c0-4 3-7 7-7s7 3 7 7"
                            />
                        </svg>
                    </div>

                    {error && (
                        <div className="login-error">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={isLoading}
                    >
                        <span>
                            {isLoading
                                ? 'Identification...'
                                : "S'identifier"}
                        </span>

                        {!isLoading && (
                            <span className="login-button-arrow">
                                →
                            </span>
                        )}
                    </button>
                </form>


                {/* ====================================================
          PIED DE CARTE
          ==================================================== */}

                <div className="login-footer">
                    <div className="login-version">
                        <span>Gestion QHSE</span>
                        <span>| Version 1.0</span>
                    </div>

                    <img
                        className="login-bycco-logo"
                        src="/images/winston_bycco_logo.png"
                        alt="By Cco"
                    />
                </div>

            </section>
        </main>
    )
}