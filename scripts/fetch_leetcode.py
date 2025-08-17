import os
import requests
from pathlib import Path

# Directory where solutions will be stored
SOLUTIONS_DIR = Path("solutions")
SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

# Load username/password from GitHub Secrets (or env vars)
username = os.getenv("LEETCODE_USERNAME")
password = os.getenv("LEETCODE_PASSWORD")

if not username or not password:
    raise ValueError("❌ Missing LEETCODE_USERNAME or LEETCODE_PASSWORD secrets")

# Start a session
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# Step 1: Get CSRF token
csrf_url = "https://leetcode.com/accounts/login/"
resp = session.get(csrf_url)
csrf_token = resp.cookies.get("csrftoken")
if not csrf_token:
    raise Exception("❌ Could not fetch CSRF token")

# Step 2: Login
login_data = {
    "csrfmiddlewaretoken": csrf_token,
    "login": username,
    "password": password,
}
login_headers = {"Referer": csrf_url}
resp = session.post(csrf_url, data=login_data, headers=login_headers)

if resp.status_code != 200 or "LEETCODE_SESSION" not in session.cookies:
    raise Exception("❌ Login failed! Check username/password.")

print("✅ Logged into LeetCode successfully")

# Step 3: GraphQL query for submissions
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

    # Map extension by language
    ext_map = {
        "python3": "py", "python": "py",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "javascript": "js",
    }
    ext = ext_map.get(sub["lang"], "txt")

    # Filename like: two-sum.py (keeps only the latest accepted version)
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
