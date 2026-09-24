import requests

BASE_URL = "http://127.0.0.1:8000"
URL = f"{BASE_URL}/events"

# Utilisateur de test existant dans Risky.
# À adapter uniquement si ces initiales n'existent pas dans la base.
INITIALS = "Cco"


def get_test_headers():
    response = requests.post(
        f"{BASE_URL}/session/login",
        json={"initials": INITIALS},
    )

    data = response.json()

    if data.get("status") != "authenticated":
        raise RuntimeError(
            f"Impossible d'ouvrir la session de test : {data}"
        )

    token = data["session_token"]

    print(
        "🔐 Session de test ouverte :",
        data["user"]["display_name"],
    )
    print()

    return {
        "X-Session-Token": token,
    }


HEADERS = get_test_headers()


def run_test(name, payload, check):
    try:
        response = requests.post(
            URL,
            json=payload,
            headers=HEADERS,
        )
        data = response.json()

        if check(data):
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
            print("   Réponse :", data)

    except Exception as exc:
        print(f"💥 {name}")
        print("   Erreur :", exc)

base_payload = {
    "event_date": "2026-09-08T10:00:00",
    "event_type": "ACCIDENT",
    "person_id": 1,
    "organization_id": None,
    "location": "Test automatique",
    "description": "Test automatique API events",
    "lost_time": False,
    "lost_days": 0,
    "modified_duty": False,
    "modified_duty_days": 0,
    "fatal": False,
    "permanent_injury": False,
}


# 1. Création normale
payload = base_payload.copy()

run_test(
    "Création normale",
    payload,
    lambda d:
        d.get("status") == "created"
        and d["event"]["event_type"] == "ACCIDENT"
)


# 2. Jours perdus normalisés
payload = base_payload.copy()
payload["lost_time"] = False
payload["lost_days"] = 12

run_test(
    "lost_time false => lost_days 0",
    payload,
    lambda d:
        d.get("status") == "created"
        and d["event"]["lost_days"] == 0
)


# 3. Travail adapté normalisé
payload = base_payload.copy()
payload["modified_duty"] = False
payload["modified_duty_days"] = 8

run_test(
    "modified_duty false => modified_duty_days 0",
    payload,
    lambda d:
        d.get("status") == "created"
        and d["event"]["modified_duty_days"] == 0
)


# 4. Jours perdus négatifs
payload = base_payload.copy()
payload["lost_time"] = True
payload["lost_days"] = -3

run_test(
    "Refus lost_days négatif",
    payload,
    lambda d:
        d.get("status") == "error"
)


# 5. Personne inexistante
payload = base_payload.copy()
payload["person_id"] = 999999

run_test(
    "Refus personne inexistante",
    payload,
    lambda d:
        d.get("status") == "error"
        and "Personne" in d.get("message", "")
)


# 6. Organisation inexistante
payload = base_payload.copy()
payload["organization_id"] = 999999

run_test(
    "Refus organisation inexistante",
    payload,
    lambda d:
        d.get("status") == "error"
        and "Organisation" in d.get("message", "")
)


# 7. Type invalide
payload = base_payload.copy()
payload["event_type"] = "BIDON"

run_test(
    "Refus type événement invalide",
    payload,
    lambda d:
        d.get("status") == "error"
        and "allowed_types" in d
)


# 8. Incident valide
payload = base_payload.copy()
payload["event_type"] = "INCIDENT"

run_test(
    "Création INCIDENT",
    payload,
    lambda d:
        d.get("status") == "created"
        and d["event"]["event_type"] == "INCIDENT"
)


# 9. Near miss valide
payload = base_payload.copy()
payload["event_type"] = "NEAR_MISS"

run_test(
    "Création NEAR_MISS",
    payload,
    lambda d:
        d.get("status") == "created"
        and d["event"]["event_type"] == "NEAR_MISS"
)


# 10. Travail adapté valide
payload = base_payload.copy()
payload["modified_duty"] = True
payload["modified_duty_days"] = 10

run_test(
    "Travail adapté valide",
    payload,
    lambda d:
        d.get("status") == "created"
        and d["event"]["modified_duty"] is True
        and d["event"]["modified_duty_days"] == 10
)


print()
print("=== FIN DES TESTS EVENTS ===")