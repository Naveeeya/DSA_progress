import os
import requests
from pathlib import Path

# Constants
BASE_URL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# Load secrets
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME")
if not LEETCODE_SESSION or not LEETCODE_USERNAME:
    raise ValueError("❌ Missing LEETCODE_SESSION or LEETCODE_USERNAME secret")

# Add session cookie
HEADERS["Cookie"] = f"LEETCODE_SESSION={LEETCODE_SESSION}"

# GraphQL Query: Recent Accepted Submissions
SUBMISSIONS_QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!, $offset: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit, offset: $offset) {
    id
    titleSlug
    lang
    timestamp
  }
}
"""

# GraphQL Query: Submission Details (code)
SUBMISSION_DETAIL_QUERY = """
query submissionDetails($id: ID!) {
  submissionDetails(submissionId: $id) {
    code
    lang
  }
}
"""

def fetch_submissions(limit=20, offset=0):
    resp = requests.post(
        BASE_URL,
        headers=HEADERS,
        json={"query": SUBMISSIONS_QUERY, "variables": {"username": LEETCODE_USERNAME, "limit": limit, "offset": offset}},
    )
    resp.raise_for_status()
    data = resp.json()["data"]["recentAcSubmissionList"]
    return data

def fetch_submission_code(submission_id):
    resp = requests.post(
        BASE_URL,
        headers=HEADERS,
        json={"query": SUBMISSION_DETAIL_QUERY, "variables": {"id": submission_id}},
    )
    resp.raise_for_status()
    return resp.json()["data"]["submissionDetails"]

def save_solution(sub):
    details = fetch_submission_code(sub["id"])
    code = details["code"]
    lang = details["lang"].lower()

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
    ext = ext_map.get(lang, "txt")

    Path("solutions").mkdir(exist_ok=True)
    filename = Path("solutions") / f"{sub['titleSlug']}.{ext}"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"✅ Saved {filename}")

def main():
    print("✅ Using LeetCode session cookie")
    offset = 0
    limit = 20
    while True:
        subs = fetch_submissions(limit=limit, offset=offset)
        if not subs:
            break
        for sub in subs:
            try:
                save_solution(sub)
            except Exception as e:
                print(f"⚠️ Skipped {sub.get('titleSlug', 'unknown')}: {e}")
        offset += limit

if __name__ == "__main__":
    main()
