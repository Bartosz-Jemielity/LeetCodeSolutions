#!/usr/bin/env python3
"""
Syncs accepted LeetCode submissions into this repository.

For every problem it writes a file:
    <difficulty>/<number>-<slug>/Solution.<ext>
with the problem statement and stats (runtime / memory + "beats %") in a header comment,
then regenerates the README.md sections (recent solutions + Easy / Medium / Hard lists).

Required environment variables (or a .env file in the repo root):
    LEETCODE_SESSION     - LEETCODE_SESSION cookie from the browser

Optional:
    LEETCODE_FULL_SYNC=1 - ignore saved state and walk the entire submission history
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import textwrap
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "data" / "solutions.json"
README = ROOT / "README.md"

BASE_URL = "https://leetcode.com"
GRAPHQL_URL = f"{BASE_URL}/graphql/"
SUBMISSIONS_URL = f"{BASE_URL}/api/submissions/"

RECENT_COUNT = 5
REQUEST_DELAY = 1.0  # seconds between requests, to avoid HTTP 429
WRAP_WIDTH = 100

# lang (from the LeetCode API) -> (file extension, comment prefix, file name without extension)
LANGS = {
    "java": ("java", "//", "Solution"),
    "cpp": ("cpp", "//", "solution"),
    "c": ("c", "//", "solution"),
    "csharp": ("cs", "//", "Solution"),
    "python": ("py", "#", "solution"),
    "python3": ("py", "#", "solution"),
    "pythondata": ("py", "#", "solution"),
    "pandas": ("py", "#", "solution"),
    "javascript": ("js", "//", "solution"),
    "typescript": ("ts", "//", "solution"),
    "golang": ("go", "//", "solution"),
    "kotlin": ("kt", "//", "Solution"),
    "swift": ("swift", "//", "solution"),
    "rust": ("rs", "//", "solution"),
    "scala": ("scala", "//", "Solution"),
    "ruby": ("rb", "#", "solution"),
    "php": ("php", "//", "solution"),
    "dart": ("dart", "//", "solution"),
    "elixir": ("ex", "#", "solution"),
    "erlang": ("erl", "%", "solution"),
    "racket": ("rkt", ";", "solution"),
    "bash": ("sh", "#", "solution"),
    "mysql": ("sql", "--", "solution"),
    "mssql": ("sql", "--", "solution"),
    "oraclesql": ("sql", "--", "solution"),
    "postgresql": ("sql", "--", "solution"),
}
DEFAULT_LANG = ("txt", "#", "solution")

DIFFICULTIES = ["Easy", "Medium", "Hard"]

MARKERS = {
    "stats": ("<!-- LEETCODE:STATS:START -->", "<!-- LEETCODE:STATS:END -->"),
    "recent": ("<!-- LEETCODE:RECENT:START -->", "<!-- LEETCODE:RECENT:END -->"),
    "problems": ("<!-- LEETCODE:PROBLEMS:START -->", "<!-- LEETCODE:PROBLEMS:END -->"),
}

DEFAULT_README = f"""# LeetCode

My [LeetCode](https://leetcode.com) solutions, synced automatically via GitHub Actions.

{MARKERS["stats"][0]}
{MARKERS["stats"][1]}

## Recent solutions

{MARKERS["recent"][0]}
{MARKERS["recent"][1]}

{MARKERS["problems"][0]}
{MARKERS["problems"][1]}
"""


# --------------------------------------------------------------------------- HTTP


class LeetCodeClient:
    def __init__(self, session: str):
        self.headers = {
            "Cookie": f"LEETCODE_SESSION={session}",
            "Referer": BASE_URL,
            "Origin": BASE_URL,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (leetcode-sync)",
        }

    def _request(self, url: str, body: dict | None = None, retries: int = 5) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        for attempt in range(retries):
            time.sleep(REQUEST_DELAY)
            req = urllib.request.Request(url, data=data, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    sys.exit(
                        f"Authorization error ({e.code}) for {url}. "
                        " The LEETCODE_SESSION cookie has probably expired - update the secret."
                    )
                if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                    wait = 5 * (attempt + 1)
                    print(f"  HTTP {e.code}, retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                raise
            except urllib.error.URLError:
                if attempt < retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
        raise RuntimeError(f"Failed to fetch {url}")

    def graphql(self, query: str, variables: dict) -> dict:
        resp = self._request(GRAPHQL_URL, {"query": query, "variables": variables})
        if resp.get("errors"):
            raise RuntimeError(f"GraphQL error: {resp['errors']}")
        return resp["data"]

    def iter_submissions(self):
        """Yields all submissions, newest first."""
        offset, last_key = 0, ""
        while True:
            url = f"{SUBMISSIONS_URL}?offset={offset}&limit=20&lastkey={last_key}"
            page = self._request(url)
            yield from page.get("submissions_dump", [])
            if not page.get("has_next"):
                return
            offset += 20
            last_key = page.get("last_key", "")

    def submission_details(self, submission_id: int) -> dict | None:
        query = """
        query submissionDetails($submissionId: Int!) {
          submissionDetails(submissionId: $submissionId) {
            runtimeDisplay runtimePercentile
            memoryDisplay memoryPercentile
            code timestamp statusCode
            lang { name verboseName }
          }
        }"""
        try:
            return self.graphql(query, {"submissionId": int(submission_id)})["submissionDetails"]
        except Exception as e:  # details are "nice to have" - the submission list has the code too
            print(f"  ! failed to fetch details for submission {submission_id}: {e}")
            return None

    def question(self, slug: str) -> dict:
        query = """
        query questionData($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionFrontendId title titleSlug difficulty content isPaidOnly
          }
        }"""
        return self.graphql(query, {"titleSlug": slug})["question"]


# --------------------------------------------------------------------------- HTML -> text


class _HTMLToText(HTMLParser):
    BLOCK = {"p", "div", "pre", "ul", "ol", "table", "tr", "h1", "h2", "h3", "h4", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.in_pre = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self.out.append("\n")
        if tag == "pre":
            self.in_pre += 1
        elif tag == "br":
            self.out.append("\n")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag == "sup":
            self.out.append("^")
        elif tag == "img":
            src = dict(attrs).get("src")
            if src:
                self.out.append(f"[image: {src}]")

    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_pre = max(0, self.in_pre - 1)
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.in_pre:
            data = re.sub(r"\s+", " ", data)
        self.out.append(data)


def html_to_text(content: str) -> str:
    parser = _HTMLToText()
    parser.feed(content)
    text = html.unescape("".join(parser.out)).replace("\xa0", " ")
    lines = []
    for line in text.splitlines():
        line = line.rstrip()
        if len(line) > WRAP_WIDTH and not line.startswith(" "):
            indent = "  " if line.lstrip().startswith("- ") else ""
            lines.extend(textwrap.wrap(line, WRAP_WIDTH, subsequent_indent=indent))
        else:
            lines.append(line)
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


# --------------------------------------------------------------------------- files


def fmt_pct(pct) -> str:
    return f"{float(pct):.2f}%" if pct is not None else "n/a"


def fmt_date(ts: int) -> str:
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")


def problem_dir(q: dict) -> str:
    return f"{q['difficulty'].lower()}/{int(q['questionFrontendId']):04d}-{q['titleSlug']}"


def build_solution_file(q: dict, sol: dict, code: str) -> str:
    _, c, _ = LANGS.get(sol["lang"], DEFAULT_LANG)
    header = [
        f"{q['questionFrontendId']}. {q['title']}",
        f"{BASE_URL}/problems/{q['titleSlug']}/",
        "",
        f"Difficulty: {q['difficulty']}",
        f"Language:   {sol['langName']}",
        f"Runtime:    {sol['runtime']} (beats {fmt_pct(sol['runtimePct'])})",
        f"Memory:     {sol['memory']} (beats {fmt_pct(sol['memoryPct'])})",
        f"Submitted:  {fmt_date(sol['timestamp'])}",
        f"Submission: {BASE_URL}/submissions/detail/{sol['submissionId']}/",
    ]
    if q.get("content"):
        header += ["", "-" * 60, ""] + html_to_text(q["content"]).splitlines()
    elif q.get("isPaidOnly"):
        header += ["", "(Premium problem - statement not available.)"]

    comment = "\n".join(f"{c} {line}".rstrip() for line in header)
    return f"{comment}\n\n{code.strip()}\n"


# --------------------------------------------------------------------------- README


def replace_section(text: str, key: str, body: str) -> str:
    start, end = MARKERS[key]
    if start not in text:
        text = text.rstrip() + f"\n\n{start}\n{end}\n"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    return pattern.sub(lambda _: f"{start}\n{body.strip()}\n{end}", text)


def problem_link(p: dict) -> str:
    return f"[{p['title']}]({BASE_URL}/problems/{p['slug']}/)"


def solution_links(p: dict) -> str:
    return " · ".join(
        f"[{s['langName']}]({s['path']})" for s in sorted(p["solutions"].values(), key=lambda s: s["langName"])
    )


def best_solution(p: dict) -> dict:
    return max(p["solutions"].values(), key=lambda s: s["timestamp"])


def render_readme(state: dict) -> None:
    problems = list(state["problems"].values())
    text = README.read_text(encoding="utf-8") if README.exists() else DEFAULT_README

    # Stats
    counts = {d: sum(1 for p in problems if p["difficulty"] == d) for d in DIFFICULTIES}
    stats = (
        "| Easy | Medium | Hard | Total |\n|:---:|:---:|:---:|:---:|\n"
        f"| {counts['Easy']} | {counts['Medium']} | {counts['Hard']} | {len(problems)} |\n\n"
        f"_Last sync: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC_"
    )
    text = replace_section(text, "stats", stats)

    # Recent solutions (per individual submission, not per problem)
    recent = sorted(
        ((p, s) for p in problems for s in p["solutions"].values()),
        key=lambda ps: ps[1]["timestamp"],
        reverse=True,
    )[:RECENT_COUNT]
    rows = ["| Date | # | Problem | Difficulty | Language | Runtime | Memory |", "|---|---:|---|---|---|---|---|"]
    for p, s in recent:
        rows.append(
            f"| {fmt_date(s['timestamp'])} | {p['id']} | {problem_link(p)} | {p['difficulty']} "
            f"| [{s['langName']}]({s['path']}) | {s['runtime']} (beats {fmt_pct(s['runtimePct'])}) "
            f"| {s['memory']} (beats {fmt_pct(s['memoryPct'])}) |"
        )
    text = replace_section(text, "recent", "\n".join(rows) if recent else "_No solutions yet._")

    # Lists per difficulty
    sections = []
    for d in DIFFICULTIES:
        ps = sorted((p for p in problems if p["difficulty"] == d), key=lambda p: int(p["id"]))
        sections.append(f"## {d} ({len(ps)})\n")
        if not ps:
            sections.append("_None yet._\n")
            continue
        sections.append("| # | Problem | Solution | Runtime | Memory |\n|---:|---|---|---|---|")
        for p in ps:
            s = best_solution(p)
            sections.append(
                f"| {p['id']} | {problem_link(p)} | {solution_links(p)} "
                f"| beats {fmt_pct(s['runtimePct'])} | beats {fmt_pct(s['memoryPct'])} |"
            )
        sections.append("")
    text = replace_section(text, "problems", "\n".join(sections))

    README.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------- main


def load_dotenv(path: Path) -> None:
    """Local runs: load KEY=VALUE pairs from .env (variables already set, e.g. in GitHub Actions, take precedence)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"lastTimestamp": 0, "problems": {}}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv(ROOT / ".env")
    session = os.environ.get("LEETCODE_SESSION")
    if not session:
        sys.exit("Set the LEETCODE_SESSION environment variable (or create a .env file).")

    client = LeetCodeClient(session)
    state = load_state()
    full_sync = os.environ.get("LEETCODE_FULL_SYNC") == "1"
    since = 0 if full_sync else int(state.get("lastTimestamp", 0))

    # 1. Collect new accepted submissions (newest first) - keep only the newest per (problem, language)
    print(f"Fetching submissions newer than {fmt_date(since) if since else 'the beginning'}...")
    newest: dict[tuple[str, str], dict] = {}
    max_ts = since
    for sub in client.iter_submissions():
        ts = int(sub["timestamp"])
        if ts <= since:
            break
        max_ts = max(max_ts, ts)
        if sub.get("status_display") != "Accepted":
            continue
        newest.setdefault((sub["title_slug"], sub["lang"]), sub)

    print(f"New accepted solutions (problem+language): {len(newest)}")
    if not newest:
        state["lastTimestamp"] = max_ts
        save_state(state)
        render_readme(state)
        return

    # 2. For each one, fetch the problem statement + stats and write the file
    questions: dict[str, dict] = {}
    for (slug, lang), sub in sorted(newest.items(), key=lambda kv: int(kv[1]["timestamp"])):
        print(f"- {slug} [{lang}]")
        if slug not in questions:
            questions[slug] = client.question(slug)
        q = questions[slug]
        if not q:
            print(f"  ! problem {slug} not found, skipping")
            continue

        details = client.submission_details(sub["id"]) or {}
        ext, _, name = LANGS.get(lang, DEFAULT_LANG)
        rel_path = f"{problem_dir(q)}/{name}.{ext}"
        sol = {
            "submissionId": int(sub["id"]),
            "lang": lang,
            "langName": (details.get("lang") or {}).get("verboseName") or sub.get("lang_name") or lang,
            "timestamp": int(sub["timestamp"]),
            "runtime": details.get("runtimeDisplay") or sub.get("runtime") or "n/a",
            "runtimePct": details.get("runtimePercentile"),
            "memory": details.get("memoryDisplay") or sub.get("memory") or "n/a",
            "memoryPct": details.get("memoryPercentile"),
            "path": rel_path,
        }
        code = details.get("code") or sub.get("code") or ""

        out = ROOT / rel_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build_solution_file(q, sol, code), encoding="utf-8")

        problem = state["problems"].setdefault(
            slug, {"id": q["questionFrontendId"], "title": q["title"], "slug": slug, "solutions": {}}
        )
        problem.update(id=q["questionFrontendId"], title=q["title"], difficulty=q["difficulty"])
        problem["solutions"][lang] = sol

    state["lastTimestamp"] = max_ts
    save_state(state)
    render_readme(state)
    print("Done.")


if __name__ == "__main__":
    main()
