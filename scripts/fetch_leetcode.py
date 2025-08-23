import os
import requests
import json

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME")

if not LEETCODE_SESSION or not LEETCODE_USERNAME:
    raise ValueError("❌ Missing LEETCODE_SESSION or LEETCODE_USERNAME secret")

print("✅ Using LeetCode session cookie")

BASE_URL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}",
    "Referer": "https://leetcode.com",
}

# Query submissions list
SUBMISSIONS_QUERY = """
query submissions($username: String!, $offset: Int!, $limit: Int!) {
  submissionList(
    username: $username,
    offset: $offset,
    limit: $limit,
  ) {
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

# Query single submission details
SUBMISSION_DETAIL_QUERY = """
query submissionDetails($id: ID!) {
  submissionDetail(submissionId: $id) {
    code
    lang
  }
}
"""

def fetch_submissions(offset=0, limit=20):
    res = requests.post(
        BASE_URL,
        headers=HEADERS,
        json={"query": SUBMISSIONS_QUERY,
              "variables": {"username": LEETCODE_USERNAME, "offset": offset, "limit": limit}},
    )
    res.raise_for_status()
    return res.json()["data"]["submissionList"]["submissions"]

def fetch_submission_code(submission_id):
    res = requests.post(
        BASE_URL,
        headers=HEADERS,
        json={"query": SUBMISSION_DETAIL_QUERY, "variables": {"id": submission_id}},
    )
    res.raise_for_status()
    return res.json()["data"]["submissionDetail"]

def save_solution(sub):
    if sub["statusDisplay"] != "Accepted":
        return  # skip non-AC

    try:
        details = fetch_submission_code(sub["id"])
    except requests.exceptions.HTTPError:
        print(f"⚠️ Skipped {sub['titleSlug']}: 400 Bad Request")
        return

    lang = details["lang"]
    code = details["code"]

    ext_map = {
        "python3": "py",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "javascript": "js",
        "typescript": "ts",
    }
    ext = ext_map.get(lang.lower(), "txt")

    os.makedirs("solutions", exist_ok=True)
    filename = f"solutions/{sub['titleSlug']}.{ext}"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ Saved {sub['titleSlug']}")

def main():
    offset = 0
    limit = 20
    submissions = fetch_submissions(offset, limit)
    for sub in submissions:
        save_solution(sub)

if __name__ == "__main__":
    main()
