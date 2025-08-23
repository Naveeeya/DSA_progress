import os
import requests
from pathlib import Path

SOLUTIONS_DIR = Path("solutions")
SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

leetcode_session = os.getenv("LEETCODE_SESSION")
leetcode_username = os.getenv("LEETCODE_USERNAME")

if not leetcode_session or not leetcode_username:
    raise ValueError("❌ Missing LEETCODE_SESSION or LEETCODE_USERNAME secret")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://leetcode.com",
    "Content-Type": "application/json"
})
session.cookies.set("LEETCODE_SESSION", leetcode_session, domain=".leetcode.com")

print("✅ Using LeetCode session cookie")

# Query: recent accepted submissions
recent_query = """
query recentAcSubmissions($username: String!) {
  recentAcSubmissionList(username: $username) {
    id
    title
    titleSlug
    lang
    timestamp
  }
}
"""

# Query: get code for one submission
code_query = """
query submissionDetails($submissionId: Int!) {
  submissionDetails(submissionId: $submissionId) {
    id
    code
    lang
  }
}
"""

def fetch_recent_submissions():
    payload = {"query": recent_query, "variables": {"username": leetcode_username}}
    res = session.post("https://leetcode.com/graphql", json=payload)
    res.raise_for_status()
    data = res.json()
    if "errors" in data:
        raise Exception(f"❌ GraphQL error: {data['errors']}")
    return data["data"]["recentAcSubmissionList"]

def fetch_submission_code(submission_id):
    payload = {"query": code_query, "variables": {"submissionId": int(submission_id)}}
    res = session.post("https://leetcode.com/graphql", json=payload)
    res.raise_for_status()
    data = res.json()
    if "errors" in data:
        raise Exception(f"❌ GraphQL error: {data['errors']}")
    return data["data"]["submissionDetails"]

def save_solution(sub):
    details = fetch_submission_code(sub["id"])
    code = details["code"]
    lang = details["lang"]

    ext_map = {
        "python3": "py", "python": "py",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "javascript": "js",
    }
    ext = ext_map.get(lang, "txt")

    filename = f"{sub['titleSlug']}.{ext}"
    filepath = SOLUTIONS_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ Saved {filename}")

def main():
    subs = fetch_recent_submissions()
    for sub in subs:
        try:
            save_solution(sub)
        except Exception as e:
            print(f"⚠️ Skipped {sub['titleSlug']}: {e}")

if __name__ == "__main__":
    main()
