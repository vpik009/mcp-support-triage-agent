# where jira tickets and slack messages actually end up  (supposed to mimic an actual API)

import base64
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SLACK_API = "https://slack.com/api/chat.postMessage"
OUTBOX = Path(os.environ.get("OUTBOX_DIR", Path(__file__).resolve().parent.parent / "outbox"))


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class FileBackend:
    def __init__(self, outbox=OUTBOX):
        self.outbox = outbox
        self.outbox.mkdir(parents=True, exist_ok=True)

    def append(self, name, record):
        with open(self.outbox / name, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def next_key(self):
        path = self.outbox / "jira.jsonl"
        count = 0
        if path.exists():
            with open(path, encoding="utf-8") as f:
                for line in f:
                    count += 1
        return "SUP-" + str(101 + count)

    def create_ticket(self, fields):
        key = self.next_key()
        self.append("jira.jsonl", {"key": key, "created": now(), **fields})
        return {"key": key, "status": "created", "backend": "file"}

    def post_message(self, channel, text):
        self.append("slack.jsonl", {"channel": channel, "text": text, "ts": now()})  # for now just write to a local file
        return {"ok": True, "channel": channel, "backend": "file"}


class JiraBackend(FileBackend):
    # real jira for tickets, slack still goes to the outbox file

    def __init__(self):
        super().__init__()
        self.url = os.environ["JIRA_URL"].rstrip("/")
        token = os.environ["JIRA_EMAIL"] + ":" + os.environ["JIRA_API_TOKEN"]
        self.auth = "Basic " + base64.b64encode(token.encode()).decode()

    def create_ticket(self, fields):
        body = {"fields": {
            "project": {"key": fields["project"]},
            "issuetype": {"name": fields["issuetype"]},
            "summary": fields["summary"],
            # api v3 wants the description in atlassian document format, plain string gets rejected
            "description": {"type": "doc", "version": 1, "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": fields["description"]}]}]},
            "priority": {"name": fields["priority"]},
            "labels": fields["labels"],
        }}
        # print(json.dumps(body, indent=2, ensure_ascii=False))
        req = urllib.request.Request(self.url + "/rest/api/3/issue", data=json.dumps(body).encode(),
                                     headers={"Authorization": self.auth, "Content-Type": "application/json"},
                                     method="POST")
        with urllib.request.urlopen(req, timeout=20) as resp:
            key = json.loads(resp.read())["key"]
        return {"key": key, "status": "created", "backend": "jira"}


class SlackBackend(FileBackend):
    # real slack for messages, tickets still go to the outbox file

    def __init__(self):
        super().__init__()
        self.token = os.environ["SLACK_BOT_TOKEN"]

    def post_message(self, channel, text):
        body = {"channel": channel, "text": text}
        req = urllib.request.Request(SLACK_API, data=json.dumps(body).encode(),
                                     headers={"Authorization": "Bearer " + self.token,
                                              "Content-Type": "application/json; charset=utf-8"}, method="POST")
        with urllib.request.urlopen(req, timeout=20) as resp:
            answer = json.loads(resp.read())
        # print("slack:", answer)
        if not answer["ok"]:
            raise RuntimeError("slack error: " + answer["error"])  # slack sends 200 even on errors, e.g. not_in_channel
        return {"ok": True, "channel": channel, "backend": "slack"}


def get_jira_backend():
    if os.environ.get("JIRA_URL"):
        return JiraBackend()
    return FileBackend()


def get_slack_backend():
    if os.environ.get("SLACK_BOT_TOKEN"):
        return SlackBackend()
    return FileBackend()
