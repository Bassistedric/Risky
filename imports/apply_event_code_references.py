import json
import urllib.request
import urllib.error

SOURCE_FILE = "imports/event_code_references.json"
API_URL = "http://127.0.0.1:8000/event-code-references/import/apply"

# Remplace par ton token de session WRITE actif
SESSION_TOKEN = input("70iye6ez58R6kaMBq9CyWjWGa9O2M_zLQql38K6RDp4").strip()


with open(SOURCE_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


for category, items in data["references"].items():
    payload = {
        "category": category,
        "source": data.get("source"),
        "source_version": data.get("source_version"),
        "items": items,
    }

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Session-Token": SESSION_TOKEN,
        },
        method="POST",
    )

    print()
    print("=" * 70)
    print(category)
    print("=" * 70)

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))

        print(json.dumps(result["summary"], indent=2, ensure_ascii=False))

    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}")
        print(e.read().decode("utf-8"))
        break

    except Exception as e:
        print(f"ERREUR : {e}")
        break