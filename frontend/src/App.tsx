import { useEffect, useState } from 'react'

import AccidentCreatePage from './pages/accident/AccidentCreatePage'
import AccidentDossierPage from './pages/accident/AccidentDossierPage'
import AccidentRegisterPage from './pages/accident/AccidentRegisterPage'
import CauseTreePage from './pages/accident/CauseTreePage'
import HeepoPage from './pages/accident/HeepoPage'
import JustCulturePage from './pages/accident/JustCulturePage'
import ActionPlanPage from './pages/actions/ActionPlanPage'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import SafetyDashboardPage from './pages/dashboard/SafetyDashboardPage'
import RiskyDemoVisionPage from './pages/demo/RiskyDemoVisionPage'

import LanguageSelector, {
  type RiskyLanguage,
} from './components/LanguageSelector'

import './App.css'

import { useTranslation } from 'react-i18next'

// ============================================================
// TYPES
// ============================================================

type MainView =
  | 'home'
  | 'dashboard'
  | 'risk-analysis'
  | 'accidents'
  | 'action-plans'
  | 'personnel'
  | 'cppt'
  | 'competencies'
  | 'equipment'
  | 'field'
  | 'quality'
  | 'demo-vision'

type RiskySession = {
  mode?: string

  user: {
    person_id: number
    initials: string
    display_name: string
  }

  roles?: string[]
  scope_all?: boolean

  scopes?: Array<{
    organization_id?: number
    organization_name?: string
    name?: string
  }>
}
// ============================================================
// APPLICATION
// ============================================================

function App() {
  // ============================================================
  // APPLICATION SHELL STATE
  // ============================================================

  const [sidebarCollapsed, setSidebarCollapsed] =
    useState(false)

  const [mainView, setMainView] =
    useState<MainView>('home')

  const [language, setLanguage] =
    useState<RiskyLanguage>(() => {
      const storedLanguage =
        localStorage.getItem(
          'risky_language',
        )

      if (
        storedLanguage === 'fr' ||
        storedLanguage === 'nl' ||
        storedLanguage === 'en' ||
        storedLanguage === 'pl'
      ) {
        return storedLanguage
      }

      return 'fr'
    })

  useEffect(() => {
    localStorage.setItem(
      'risky_language',
      language,
    )
  }, [language])

  const { t, i18n } = useTranslation()

  // ============================================================
  // ACCIDENT MODULE NAVIGATION
  // ============================================================

  const [accidentView, setAccidentView] =
    useState<
      | 'register'
      | 'create'
      | 'dossier'
      | 'cause-tree'
      | 'heepo'
      | 'just-culture'
    >('register')

  const [selectedEventId, setSelectedEventId] =
    useState<number | null>(null)


  // ============================================================
  // SESSION RISKY
  // ============================================================

  const [sessionChecked, setSessionChecked] =
    useState(false)

  const [authenticated, setAuthenticated] =
    useState(false)

  const [currentSession, setCurrentSession] =
    useState<RiskySession | null>(null)

  const [profileMenuOpen, setProfileMenuOpen] =
    useState(false)

  // ============================================================
  // VÉRIFICATION DE LA SESSION
  // ============================================================

  useEffect(() => {
    async function checkSession() {
      const token = sessionStorage.getItem(
        'risky_session_token',
      )

      if (!token) {
        setCurrentSession(null)
        setAuthenticated(false)
        setSessionChecked(true)
        return
      }

      try {
        const response = await fetch(
          'http://127.0.0.1:8000/session/me',
          {
            headers: {
              'X-Session-Token': token,
            },
          },
        )

        const data = await response.json()

        if (
          response.ok &&
          data.status === 'authenticated'
        ) {
          setCurrentSession(data)
          setAuthenticated(true)
        } else {
          sessionStorage.removeItem(
            'risky_session_token',
          )

          setCurrentSession(null)
          setAuthenticated(false)
        }
      } catch {
        setCurrentSession(null)
        setAuthenticated(false)
      } finally {
        setSessionChecked(true)
      }
    }

    checkSession()
  }, [])


  // ============================================================
  // PROFIL UTILISATEUR
  // ============================================================

  const userInitials =
    currentSession?.user?.initials?.toUpperCase() ??
    '---'

  const userDisplayName =
    currentSession?.user?.display_name ??
    t('profile.user')

  const userRole =
    currentSession?.roles?.[0] ??
    currentSession?.mode ??
    'UTILISATEUR'

  const userScope =
    currentSession?.scope_all
      ? t('profile.allEntities')
      : currentSession?.scopes?.[0]?.organization_name ??
      currentSession?.scopes?.[0]?.name ??
      t('profile.assignedScope')


  // ============================================================
  // DÉCONNEXION
  // ============================================================

  async function handleLogout() {
    const token = sessionStorage.getItem(
      'risky_session_token',
    )

    try {
      if (token) {
        await fetch(
          'http://127.0.0.1:8000/session/logout',
          {
            method: 'POST',
            headers: {
              'X-Session-Token': token,
            },
          },
        )
      }
    } finally {
      sessionStorage.removeItem(
        'risky_session_token',
      )

      setCurrentSession(null)
      setProfileMenuOpen(false)
      setAuthenticated(false)
      setMainView('home')
    }
  }

  // ============================================================
  // CHARGEMENT DE L'APPLICATION
  // ============================================================

  if (!sessionChecked) {
    return (
      <div className="app-loading">
        {t('common.loadingRisky')}
      </div>
    )
  }


  // ============================================================
  // IDENTIFICATION
  // ============================================================

  if (!authenticated) {
    return (
      <LoginPage
        onAuthenticated={() => {
          setAuthenticated(true)
          setMainView('home')
        }}
      />
    )
  }


  // ============================================================
  // APPLICATION RISKY
  // ============================================================

  return (
    <div
      className={`risky-shell ${sidebarCollapsed
        ? 'risky-shell--sidebar-collapsed'
        : ''
        }`}
    >

      {/* ============================================================
          SIDEBAR
          ============================================================ */}

      <aside className="risky-sidebar">

        {/* ============================================================
            IDENTITÉ RISKY
            ============================================================ */}

        <div className="risky-brand">
          <div className="risky-brand__mark">
            R
          </div>

          <div className="risky-brand__text">
            <strong>RISKY</strong>
            <span>Q H S E</span>
          </div>

          <img
            className="risky-brand__signature"
            src="/images/winston_bycco_logo.png"
            alt="By Cco"
          />
        </div>


        {/* ============================================================
            RÉDUCTION SIDEBAR
            ============================================================ */}

        <button
          className="risky-sidebar-toggle"
          type="button"
          onClick={() =>
            setSidebarCollapsed(
              (current) => !current,
            )
          }
          aria-label={
            sidebarCollapsed
              ? t('common.expandMenu')
              : t('common.collapseMenu')
          }
          title={
            sidebarCollapsed
              ? t('common.expandMenu')
              : t('common.collapseMenu')
          }
        >
          {sidebarCollapsed ? '»' : '«'}
        </button>


        {/* ============================================================
            NAVIGATION
            ============================================================ */}

        <nav className="risky-nav">

          {/* ============================================================
            VUE GÉNÉRALE
            ============================================================ */}

          <div className="risky-nav-group">
            <div className="risky-nav-group__title">
              {t('navigation.overview')}
            </div>

            <button
              className={`risky-nav-item ${mainView === 'home'
                ? 'risky-nav-item--active'
                : ''
                }`}
              type="button"
              aria-label={t('common.home')}
              title={
                sidebarCollapsed
                  ? t('common.home')
                  : undefined
              }
              onClick={() => {
                setMainView('home')
              }}
            >
              <span className="risky-nav-item__icon">
                ⌂
              </span>

              {t('common.home')}
            </button>

            <button
              className={`risky-nav-item ${mainView === 'dashboard'
                ? 'risky-nav-item--active'
                : ''
                }`}
              type="button"
              aria-label={t('common.dashboard')}
              title={
                sidebarCollapsed
                  ? t('common.dashboard')
                  : undefined
              }
              onClick={() => {
                setMainView('dashboard')
              }}
            >
              <span className="risky-nav-item__icon">
                ▦
              </span>

              {t('common.dashboard')}
            </button>
          </div>


          {/* ============================================================
            SÉCURITÉ
            ============================================================ */}

          <div className="risky-nav-group">
            <div className="risky-nav-group__title">
              {t('navigation.safety')}
            </div>

            <button
              className={`risky-nav-item ${mainView === 'accidents'
                ? 'risky-nav-item--active'
                : ''
                }`}
              type="button"
              aria-label={t('navigation.accidents')}
              title={
                sidebarCollapsed
                  ? t('navigation.accidents')
                  : undefined
              }
              onClick={() => {
                setMainView('accidents')
                setSelectedEventId(null)
                setAccidentView('register')
              }}
            >
              <span className="risky-nav-item__icon">
                △
              </span>

              {t('navigation.accidents')}
            </button>

            <button
              className={`risky-nav-item ${mainView === 'risk-analysis'
                ? 'risky-nav-item--active'
                : ''
                }`}
              type="button"
              aria-label={t('navigation.riskAnalysis')}
              title={
                sidebarCollapsed
                  ? t('navigation.riskAnalysis')
                  : undefined
              }
              onClick={() => {
                setMainView('risk-analysis')
              }}
            >
              <span className="risky-nav-item__icon">
                ◇
              </span>

              {t('navigation.riskAnalysis')}
            </button>

            <button
              className="risky-nav-item"
              type="button"
              aria-label="FMRA"
              title={sidebarCollapsed ? 'FMRA' : undefined}
            >
              <span className="risky-nav-item__icon">
                ✓
              </span>

              FMRA
            </button>

            <button
              className="risky-nav-item"
              type="button"
              aria-label="STOP"
              title={sidebarCollapsed ? 'STOP' : undefined}
            >
              <span className="risky-nav-item__icon">
                ⬢
              </span>

              STOP
            </button>

            <button
              className="risky-nav-item"
              type="button"
              aria-label="ILT"
              title={sidebarCollapsed ? 'ILT' : undefined}
            >
              <span className="risky-nav-item__icon">
                ⌕
              </span>

              ILT
            </button>

            <button
              className="risky-nav-item"
              type="button"
              aria-label="Toolbox"
              title={
                sidebarCollapsed
                  ? 'Toolbox'
                  : undefined
              }
            >
              <span className="risky-nav-item__icon">
                ♟
              </span>

              Toolbox
            </button>
          </div>


          {/* ============================================================
            GESTION
            ============================================================ */}

          <div className="risky-nav-group">
            <div className="risky-nav-group__title">
              {t('navigation.management')}
            </div>

            <button
              className={`risky-nav-item ${mainView === 'personnel'
                ? 'risky-nav-item--active'
                : ''
                }`}
              type="button"
              aria-label={t('navigation.personnel')}
              title={
                sidebarCollapsed
                  ? t('navigation.personnel')
                  : undefined
              }
              onClick={() => {
                setMainView('personnel')
              }}
            >
              <span className="risky-nav-item__icon">
                ♙
              </span>

              {t('navigation.personnel')}
            </button>

            <button
              className={`risky-nav-item ${mainView === 'cppt'
                ? 'risky-nav-item--active'
                : ''
                }`}
              type="button"
              aria-label={t('navigation.cppt')}
              title={
                sidebarCollapsed
                  ? t('navigation.cppt')
                  : undefined
              }
              onClick={() => {
                setMainView('cppt')
              }}
            >
              <span className="risky-nav-item__icon">
                ◫
              </span>

              {t('navigation.cppt')}
            </button>

            <button
              className={`risky-nav-item ${mainView === 'equipment'
                ? 'risky-nav-item--active'
                : ''
                }`}
              type="button"
              aria-label={t('navigation.equipment')}
              title={
                sidebarCollapsed
                  ? t('navigation.equipment')
                  : undefined
              }
              onClick={() => {
                setMainView('equipment')
              }}
            >
              <span className="risky-nav-item__icon">
                ▣
              </span>

              {t('navigation.equipment')}
            </button>

            <button
              className="risky-nav-item"
              type="button"
              aria-label={t('navigation.training')}
              title={
                sidebarCollapsed
                  ? t('navigation.training')
                  : undefined
              }
            >
              <span className="risky-nav-item__icon">
                ♧
              </span>

              {t('navigation.training')}
            </button>

            <button
              className={`risky-nav-item ${mainView === 'quality'
                ? 'risky-nav-item--active'
                : ''
                }`}
              type="button"
              aria-label={t('navigation.quality')}
              title={
                sidebarCollapsed
                  ? t('navigation.quality')
                  : undefined
              }
              onClick={() => {
                setMainView('quality')
              }}
            >
              <span className="risky-nav-item__icon">
                ☆
              </span>

              {t('navigation.quality')}
            </button>

            <button
              className="risky-nav-item"
              type="button"
              aria-label={t('navigation.documents')}
              title={
                sidebarCollapsed
                  ? t('navigation.documents')
                  : undefined
              }
            >
              <span className="risky-nav-item__icon">
                ▤
              </span>

              {t('navigation.documents')}
            </button>

            <button
              className={`risky-nav-item ${mainView === 'action-plans'
                ? 'risky-nav-item--active'
                : ''
                }`}
              type="button"
              aria-label={t('navigation.actionPlans')}
              title={
                sidebarCollapsed
                  ? t('navigation.actionPlans')
                  : undefined
              }
              onClick={() => {
                setMainView('action-plans')
              }}
            >
              <span className="risky-nav-item__icon">
                ☑
              </span>

              {t('navigation.actionPlans')}
            </button>
          </div>


          <div className="risky-nav-group">
            <div className="risky-nav-group__title">DÉMONSTRATION</div>
            <button
              className={`risky-nav-item ${mainView === 'demo-vision' ? 'risky-nav-item--active' : ''}`}
              type="button"
              aria-label="Vision cible"
              title={sidebarCollapsed ? 'Vision cible' : undefined}
              onClick={() => setMainView('demo-vision')}
            >
              <span className="risky-nav-item__icon">◎</span>
              Vision cible
            </button>
          </div>

          {/* ============================================================
            SYSTÈME
            ============================================================ */}

          <div className="risky-nav-group">
            <div className="risky-nav-group__title">
              {t('navigation.system')}
            </div>

            <button
              className="risky-nav-item"
              type="button"
              aria-label={t('navigation.forms')}
              title={
                sidebarCollapsed
                  ? t('navigation.forms')
                  : undefined
              }
            >
              <span className="risky-nav-item__icon">
                ▧
              </span>

              {t('navigation.forms')}
            </button>

            <button
              className="risky-nav-item"
              type="button"
              aria-label={t('navigation.administration')}
              title={
                sidebarCollapsed
                  ? t('navigation.administration')
                  : undefined
              }
            >
              <span className="risky-nav-item__icon">
                ⚙
              </span>

              {t('navigation.administration')}
            </button>
          </div>
        </nav>


        {/* ============================================================
            PROFIL
            ============================================================ */}

        <div className="risky-profile-wrapper">

          {profileMenuOpen && (
            <div className="risky-profile-menu">

              <button
                type="button"
                className="risky-profile-menu__item"
              >
                {t('profile.myProfile')}
              </button>

              {!currentSession?.scope_all && (
                <button
                  type="button"
                  className="risky-profile-menu__item"
                >
                  {t('profile.changeScope')}
                </button>
              )}

              <div className="risky-profile-menu__separator" />

              <button
                type="button"
                className="risky-profile-menu__item risky-profile-menu__item--logout"
                onClick={handleLogout}
              >
                {t('profile.logout')}
              </button>

            </div>
          )}

          <button
            className="risky-profile"
            type="button"
            onClick={() =>
              setProfileMenuOpen(
                (current) => !current,
              )
            }
            title={t('profile.profile')}
          >
            <div className="risky-profile__avatar">
              {userInitials}
            </div>

            {!sidebarCollapsed && (
              <>
                <div className="risky-profile__identity">
                  <strong>
                    {userDisplayName}
                  </strong>

                  <span>
                    {userRole} · {userScope}
                  </span>

                  <small>
                    {t('profile.profile')}
                  </small>
                </div>

                <span className="risky-profile__chevron">
                  {profileMenuOpen ? '⌃' : '›'}
                </span>
              </>
            )}
          </button>

        </div>
      </aside>


      {/* ============================================================
          ESPACE DE TRAVAIL
          ============================================================ */}

      <div className="risky-workspace">

        {/* ============================================================
            TOPBAR
            ============================================================ */}

        <header className="risky-topbar">
          <div>
            <div className="risky-topbar__eyebrow">
              {mainView === 'home'
                ? t('common.home')
                : mainView === 'dashboard'
                  ? t('navigation.overview')
                  : mainView === 'accidents'
                    ? t('navigation.accidents')
                    : mainView === 'risk-analysis'
                      ? t('navigation.riskAnalysis')
                      : mainView === 'action-plans'
                        ? t('navigation.actionPlans')
                        : mainView === 'personnel'
                          ? t('navigation.personnel')
                          : mainView === 'cppt'
                            ? t('navigation.cppt')
                          : mainView === 'cppt'
                            ? t('navigation.cppt')
                          : mainView === 'competencies'
                            ? t('navigation.competencies')
                            : mainView === 'equipment'
                              ? t('navigation.equipmentSafety')
                              : mainView === 'field'
                                ? t('navigation.field')
                                : mainView === 'quality'
                                  ? t('navigation.qualitySmi')
                                  : t('common.riskyQhse')}
            </div>

            <h1>
              {mainView === 'home'
                ? t('common.home')
                : mainView === 'dashboard'
                  ? t('common.dashboard')
                  : mainView === 'accidents'
                    ? accidentView === 'register'
                      ? t('topbar.accidentRegister')
                      : accidentView === 'create'
                        ? t('topbar.newEvent')
                        : accidentView === 'dossier'
                          ? t('topbar.eventFile')
                          : accidentView === 'cause-tree'
                            ? t('topbar.causeTree')
                            : accidentView === 'heepo'
                              ? t('topbar.heepo')
                              : accidentView === 'just-culture'
                                ? 'Just Culture'
                                : t('topbar.accidentRegister')
                    : mainView === 'risk-analysis'
                      ? t('navigation.riskAnalysis')
                      : mainView === 'action-plans'
                        ? t('navigation.actionPlans')
                        : mainView === 'personnel'
                          ? t('navigation.personnel')
                          : mainView === 'competencies'
                            ? t('navigation.competencies')
                            : mainView === 'equipment'
                              ? t('navigation.equipmentSafety')
                              : mainView === 'field'
                                ? t('navigation.field')
                                : mainView === 'quality'
                                  ? t('navigation.qualitySmi')
                                  : t('common.riskyQhse')}
            </h1>

            <p>
              {mainView === 'home'
                ? t('topbar.homeDescription')
                : mainView === 'dashboard'
                  ? t('topbar.dashboardDescription')
                  : mainView === 'accidents'
                    ? accidentView === 'register'
                      ? t('topbar.accidentRegisterDescription')
                      : accidentView === 'create'
                        ? t('topbar.newEventDescription')
                        : accidentView === 'dossier'
                          ? t('topbar.eventFileDescription')
                          : accidentView === 'cause-tree'
                            ? t('topbar.causeTreeDescription')
                            : accidentView === 'heepo'
                              ? t('topbar.heepoDescription')
                              : accidentView === 'just-culture'
                                ? t('accident.justCulture.pageDescription')
                                : t('topbar.accidentRegisterDescription')
                    : t('topbar.genericDescription')}
            </p>
          </div>


          {/* ============================================================
              FILTRES
              ============================================================ */}

          <div className="risky-topbar__tools">

            <div className="risky-topbar__language">
              <LanguageSelector
                value={language}
                onChange={(newLanguage) => {
                  setLanguage(newLanguage)

                  localStorage.setItem(
                    'risky_language',
                    newLanguage,
                  )

                  void i18n.changeLanguage(
                    newLanguage,
                  )
                }}
              />
            </div>

            <div className="risky-topbar__filters">
              <select defaultValue="vma-sud">
                <option value="vma-sud">
                  VMA Sud
                </option>
              </select>

              <select defaultValue="all">
                <option value="all">
                  {t('common.allTrades')}
                </option>

                <option value="hvac">
                  HVAC
                </option>

                <option value="ref">
                  REF
                </option>

                <option value="elec">
                  ELEC
                </option>
              </select>

              <button
                className="risky-notification"
                type="button"
                aria-label={t('common.notifications')}
              >
                ●
              </button>
            </div>

          </div>
        </header>


        {/* ============================================================
            CONTENU PRINCIPAL
            ============================================================ */}

        <main className="risky-main">

          {/* ========================================================
              ACCUEIL
              ======================================================== */}

          {mainView === 'home' && (
            <HomePage
              onOpenModule={(module) => {
                setMainView(module)

                if (module === 'accidents') {
                  setSelectedEventId(null)
                  setAccidentView('register')
                }
              }}
            />
          )}

          {/* ========================================================
    TABLEAU DE BORD
    ======================================================== */}

          {mainView === 'dashboard' && (
            <SafetyDashboardPage />
          )}
          {/* ========================================================
              MODULE ACCIDENTS
              ======================================================== */}

          {mainView === 'accidents' && (
            <>

              {/* ========================================================
                  REGISTRE
                  ======================================================== */}

              {accidentView === 'register' && (
                <AccidentRegisterPage
                  onOpenEvent={(eventId) => {
                    setSelectedEventId(eventId)
                    setAccidentView('dossier')
                  }}
                  onCreateEvent={() => {
                    setSelectedEventId(null)
                    setAccidentView('create')
                  }}
                />
              )}


              {/* ========================================================
                  CRÉATION D'UN ÉVÉNEMENT
                  ======================================================== */}

              {accidentView === 'create' && (
                <AccidentCreatePage
                  onBack={() => {
                    setAccidentView('register')
                  }}
                  onCreated={(eventId) => {
                    setSelectedEventId(eventId)
                    setAccidentView('dossier')
                  }}
                />
              )}


              {/* ========================================================
                  DOSSIER ÉVÉNEMENT
                  ======================================================== */}

              {accidentView === 'dossier' &&
                selectedEventId !== null && (
                  <AccidentDossierPage
                    eventId={selectedEventId}
                    onBack={() => {
                      setAccidentView('register')
                    }}
                    onOpenCauseTree={() => {
                      setAccidentView('cause-tree')
                    }}
                    onOpenHeepo={() => {
                      setAccidentView('heepo')
                    }}
                    onOpenJustCulture={() => {
                      setAccidentView('just-culture')
                    }}
                  />
                )}


              {/* ========================================================
                  ARBRE DES CAUSES
                  ======================================================== */}

              {accidentView === 'cause-tree' &&
                selectedEventId !== null && (
                  <CauseTreePage
                    eventId={selectedEventId}
                    onBack={() => {
                      setAccidentView('dossier')
                    }}
                  />
                )}

            </>
          )}

          {/* ========================================================
    HEEPO
    ======================================================== */}

          {accidentView === 'heepo' &&
            selectedEventId !== null && (
              <HeepoPage
                eventId={selectedEventId}
                onBack={() => {
                  setAccidentView('dossier')
                }}
              />
            )}

          {/* ========================================================
              JUST CULTURE
              ======================================================== */}

          {accidentView === 'just-culture' &&
            selectedEventId !== null && (
              <JustCulturePage
                eventId={selectedEventId}
                onBack={() => {
                  setAccidentView('dossier')
                }}
              />
            )}

          {/* ========================================================
              PLAN D'ACTIONS
              ======================================================== */}

          {mainView === 'action-plans' && (
            <ActionPlanPage
              onOpenEvent={(eventId) => {
                setSelectedEventId(eventId)
                setAccidentView('dossier')
                setMainView('accidents')
              }}
            />
          )}

          {mainView === 'demo-vision' && (
            <RiskyDemoVisionPage onBack={() => setMainView('home')} />
          )}

          {/* ========================================================
              MODULES EN ATTENTE
              ======================================================== */}

          {mainView !== 'home' &&
            mainView !== 'dashboard' &&
            mainView !== 'accidents' &&
            mainView !== 'action-plans' &&
            mainView !== 'demo-vision' && (
              <section className="risky-placeholder">
                <h2>
                  {t('common.moduleInPreparation')}
                </h2>

                <p>
                  {t('common.sectionComingSoon')}
                </p>
              </section>
            )}

        </main>
      </div>
    </div>
  )
}

export default App