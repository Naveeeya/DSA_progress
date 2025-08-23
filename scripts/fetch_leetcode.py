import os
import requests
from pathlib import Path

SOLUTIONS_DIR = Path("solutions")
SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

leetcode_session = os.getenv("LEETCODE_SESSION")
leetcode_username = os.getenv("LEETCODE_USERNAME")  # just the username (no password needed)

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

# 1. Fetch recent AC submissions
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

# 2. Fetch code for a given submission
code_query = """
query submissionDetails($id: ID!) {
  submissionDetails(submissionId: $id) {
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
    return res.json()["data"]["recentAcSubmissionList"]

def fetch_submission_code(submission_id):
    payload = {"query": code_query, "variables": {"id": submission_id}}
    res = session.post("https://leetcode.com/graphql", json=payload)
    res.raise_for_status()
    return res.json()["data"]["submissionDetails"]

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
    submissions = fetch_recent_submissions()
    for sub in submissions:
        save_solution(sub)

if __name__ == "__main__":
    main()
