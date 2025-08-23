import os
import requests
import pathlib

# 🔧 Config
BASE_URL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME")

if not LEETCODE_SESSION or not LEETCODE_USERNAME:
    raise ValueError("❌ Missing LEETCODE_SESSION or LEETCODE_USERNAME secret")

HEADERS["Cookie"] = f"LEETCODE_SESSION={LEETCODE_SESSION}"

# ----------------- GraphQL Queries -----------------
SUBMISSIONS_QUERY = """
query submissions($username: String!, $limit: Int!, $lastKey: String) {
  submissionList(username: $username, limit: $limit, lastKey: $lastKey) {
    lastKey
    hasNext
    submissions {
      id
      title
      titleSlug
      statusDisplay
      lang
      timestamp
    }
  }
}
"""

SUBMISSION_DETAIL_QUERY = """
query submissionDetails($id: ID!) {
  submissionDetails(submissionId: $id) {
    code
    lang
    runtime
    memory
  }
}
"""

# ----------------- Fetching Functions -----------------
def fetch_submissions(limit=20, last_key=None):
    res = requests.post(
        BASE_URL,
        headers=HEADERS,
        json={
            "query": SUBMISSIONS_QUERY,
            "variables": {"username": LEETCODE_USERNAME, "limit": limit, "lastKey": last_key},
        },
    )
    res.raise_for_status()
    data = res.json()["data"]["submissionList"]
    return data["submissions"], data.get("lastKey"), data.get("hasNext")


def fetch_submission_code(sub_id):
    res = requests.post(
        BASE_URL,
        headers=HEADERS,
        json={"query": SUBMISSION_DETAIL_QUERY, "variables": {"id": sub_id}},
    )
    res.raise_for_status()
    return res.json()["data"]["submissionDetails"]


def save_solution(sub):
    details = fetch_submission_code(sub["id"])
    code = details["code"]
    lang = details["lang"].lower()

    # extension mapping
    ext_map = {
        "python3": "py",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "javascript": "js",
        "typescript": "ts",
        "go": "go",
        "ruby": "rb",
        "swift": "swift",
    }
    ext = ext_map.get(lang, lang)

    pathlib.Path("solutions").mkdir(parents=True, exist_ok=True)
    file_path = pathlib.Path("solutions") / f"{sub['titleSlug']}.{ext}"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ Saved {file_path}")


# ----------------- Main -----------------
def main():
    print("✅ Using LeetCode session cookie")
    last_key = None

    while True:
        submissions, last_key, has_next = fetch_submissions(limit=20, last_key=last_key)
        for sub in submissions:
            if sub["statusDisplay"] == "Accepted":  # save only AC submissions
                try:
                    save_solution(sub)
                except Exception as e:
                    print(f"⚠️ Skipped {sub['titleSlug']}: {e}")
        if not has_next:
            break


if __name__ == "__main__":
    main()
