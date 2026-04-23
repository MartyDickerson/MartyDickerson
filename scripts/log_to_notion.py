#!/usr/bin/env python3
import os, sys, requests
from datetime import datetime, timezone

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")
NOTION_API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def create_page(title, entry_type, description="", repo=None, url=None, tags=None):
    properties = {
        "Name": {"title": [{"text": {"content": title[:2000]}}]},
        "Type": {"select": {"name": entry_type}},
        "Date": {"date": {"start": datetime.now(timezone.utc).isoformat()}},
    }
    if description:
        properties["Description"] = {"rich_text": [{"text": {"content": description[:2000]}}]}
    if repo:
        properties["Repo"] = {"rich_text": [{"text": {"content": repo}}]}
    if url:
        properties["URL"] = {"url": url}
    if tags:
        properties["Tags"] = {"multi_select": [{"name": t.strip()} for t in tags if t.strip()]}
    r = requests.post(f"{NOTION_API}/pages", headers=HEADERS,
        json={"parent": {"database_id": DATABASE_ID}, "properties": properties}, timeout=10)
    r.raise_for_status()
    print(f"Logged [{entry_type}]: {title}")

message = os.environ.get("COMMIT_MESSAGE", "").strip()
repo = os.environ.get("REPO_NAME", "")
branch = os.environ.get("BRANCH", "")
author = os.environ.get("AUTHOR", "")
url = os.environ.get("COMMIT_URL", "")

if message and not message.startswith("Merge ") and "[skip notion]" not in message:
    repo_short = repo.split("/")[-1] if repo else repo
    title = f"[{repo_short}] {message[:120]}"
    desc = "\n".join(filter(None, [f"Branch: {branch}", f"Author: {author}", "", message]))
    tags = ["Commit"] + ([repo_short] if repo_short else [])
    create_page(title, "Commit", description=desc, repo=repo, url=url, tags=tags)
else:
    print("Skipping commit.")
