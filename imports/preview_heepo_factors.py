import json
import urllib.request
import urllib.error

SOURCE_FILE = "imports/heepo_factors.json"
API_URL = "http://127.0.0.1:8000/events/heepo-factors/import/preview"


with open(SOURCE_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


payload = {
    "source": data.get("source"),
    "source_version": data.get("source_version"),
    "items": data["factors"],
}

body = json.dumps(
    payload,
    ensure_ascii=False,
).encode("utf-8")

request = urllib.request.Request(
    API_URL,
    data=body,
    headers={
        "Content-Type": "application/json",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(request) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    print("HEEPO")
    print("=" * 50)
    print(
        json.dumps(
            result["summary"],
            indent=2,
            ensure_ascii=False,
        )
    )

except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}")
    print(e.read().decode("utf-8"))

except Exception as e:
    print(f"ERREUR : {e}")
