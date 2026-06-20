import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHALLENGES_FILE = SCRIPT_DIR / "data" / "challenges.json"
OUTPUT_FILE = SCRIPT_DIR / "data" / "writeups.json"
RAW_BASE = "https://raw.githubusercontent.com/hackthebox"
BRANCHES = ["main", "master"]
REQUEST_DELAY = 0.3
MAX_RETRIES = 3
RETRY_DELAY = 3


def candidate_paths(record):
    event = record["ctf_event"]
    category = record["category"]
    name = record["challenge_name"]
    difficulty = record["difficulty_original"]

    folder_variants = [
        f"[{difficulty}] {name}",
        f"{name} [{difficulty}]",
        f"{name}[{difficulty}]",
        name,
    ]

    category_variants = [category]
    if category == "crypto":
        category_variants.append("cryptography")
    elif category == "pwn":
        category_variants.append("pwning")
    elif category == "reversing":
        category_variants.append("rev")
        category_variants.append("reverse")
    elif category == "misc":
        category_variants.append("miscellaneous")
    elif category == "fullpwn":
        category_variants.append("full-pwn")
    elif category == "hardware":
        category_variants.append("hw")

    roots = ["", f"{event}/"]
    filenames = ["README.md", "readme.md", "Readme.md", f"{name}.md"]

    paths = []
    for root in roots:
        for cat in category_variants:
            for folder in folder_variants:
                for filename in filenames:
                    paths.append(f"{root}{cat}/{folder}/{filename}")
    return paths


def encode_path(event, path):
    parts = path.split("/")
    encoded = "/".join(urllib.parse.quote(p) for p in parts)
    return f"{RAW_BASE}/{event}/{{branch}}/{encoded}"


def fetch_url(url):
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ctf-benchmark-fetch"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status == 200:
                    return resp.read().decode("utf-8", errors="ignore")
            return None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503):
                time.sleep(RETRY_DELAY)
                continue
            return None
        except (urllib.error.URLError, TimeoutError):
            time.sleep(RETRY_DELAY)
            continue
    return None


def fetch_record(record):
    event = record["ctf_event"]
    for path in candidate_paths(record):
        template = encode_path(event, path)
        for branch in BRANCHES:
            url = template.format(branch=branch)
            text = fetch_url(url)
            if text is not None and len(text) >= 100:
                return text, url
            time.sleep(REQUEST_DELAY)
    return None, None


def load_challenges():
    if not CHALLENGES_FILE.exists():
        print(f"error: {CHALLENGES_FILE} not found")
        sys.exit(1)
    with open(CHALLENGES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    records = load_challenges()
    total = len(records)
    results = []
    failures = []

    print(f"fetching {total} writeups from hackthebox public repos")
    print("-" * 60)

    for i, record in enumerate(records, 1):
        name = record["challenge_name"]
        event = record["ctf_event"]
        text, url = fetch_record(record)

        if text is None:
            failures.append(record)
            status = "MISS"
        else:
            entry = dict(record)
            entry["writeup_text"] = text
            results.append(entry)
            status = "ok"

        print(f"[{i:3}/{total}] {status:4} {event} / {name}")

    print("-" * 60)
    print(f"fetched {len(results)} / {total}")

    if failures:
        print(f"missed {len(failures)}:")
        for record in failures:
            print(f"  {record['ctf_event']} / {record['category']} / {record['challenge_name']}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()