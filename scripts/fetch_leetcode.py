import os
import requests
from pathlib import Path

# Directory where solutions will be stored
SOLUTIONS_DIR = Path("solutions")
SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

# Load session token from GitHub Secrets (env vars)
leetcode_session = os.getenv("LEETCODE_SESSION")

if not leetcode_session:
    raise ValueError("❌ Missing LEETCODE_SESSION secret")

# Start a session
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://leetcode.com",
    "Content-Type": "application/json"
})
session.cookies.set("LEETCODE_SESSION", leetcode_session, domain=".leetcode.com")

print("✅ Using LeetCode session cookie")

# GraphQL query for submissions
query = """
query submissions($offset: Int!, $limit: Int!) {
  submissionList(offset: $offset, limit: $limit) {
    submissions {
      id
      title
      titleSlug
      lang
      statusDisplay
      code
    }
  }
}
"""

def fetch_submissions(offset=0, limit=20):
    payload = {"query": query, "variables": {"offset": offset, "limit": limit}}
    res = session.post("https://leetcode.com/graphql", json=payload)
    res.raise_for_status()
    return res.json()["data"]["submissionList"]["submissions"]

def save_solution(sub):
    if sub["statusDisplay"] != "Accepted":
        return

    ext_map = {
        "python3": "py", "python": "py",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "javascript": "js",
    }
    ext = ext_map.get(sub["lang"], "txt")

    filename = f"{sub['titleSlug']}.{ext}"
    filepath = SOLUTIONS_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(sub["code"])

    print(f"✅ Saved {filename}")

def main():
    offset = 0
    limit = 20
    while True:
        submissions = fetch_submissions(offset, limit)
        if not submissions:
            break
        for sub in submissions:
            save_solution(sub)
        offset += limit

if __name__ == "__main__":
    main()
