#!/usr/bin/env python3
"""Collect AI engineering signals and optionally create a blog draft.

The script intentionally uses only the Python standard library so it can run
locally and inside GitHub Actions without dependency installation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "_data" / "ai_radar.yml"
DRAFT_DIR = ROOT / "_drafts"

GITHUB_TOPICS = [
    "llm",
    "ai-agent",
    "rag",
    "mcp",
    "generative-ai",
    "llmops",
]

HN_QUERIES = [
    "LLM agent",
    "RAG vector database",
    "MCP server",
    "AI coding tool",
]

HN_RELEVANCE_TERMS = [
    "ai",
    "llm",
    "agent",
    "mcp",
    "rag",
    "vector",
    "token",
    "coding",
    "model",
    "inference",
    "prompt",
]


def request_json(url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "hoonapps-ai-radar",
            **(headers or {}),
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def scalar(value: Any) -> str:
    if value is None:
        return '""'
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def yaml_list(values: list[str], indent: int) -> list[str]:
    pad = " " * indent
    if not values:
        return [f"{pad}[]"]
    return [f"{pad}- {scalar(value)}" for value in values]


def write_yaml(data: dict[str, Any], path: Path) -> None:
    lines: list[str] = []
    lines.append(f"generated_at: {scalar(data['generated_at'])}")
    lines.append(f"window_days: {data['window_days']}")
    lines.append("sources:")
    for source in data["sources"]:
        lines.append(f"  - name: {scalar(source['name'])}")
        lines.append(f"    url: {scalar(source['url'])}")
        lines.append(f"    signal: {scalar(source['signal'])}")
    lines.append("candidates:")
    for item in data["candidates"]:
        lines.append(f"  - name: {scalar(item['name'])}")
        lines.append(f"    source: {scalar(item['source'])}")
        lines.append(f"    url: {scalar(item['url'])}")
        lines.append(f"    summary: {scalar(item['summary'])}")
        lines.append(f"    reason: {scalar(item['reason'])}")
        lines.append(f"    category: {scalar(item['category'])}")
        lines.append("    tags:")
        lines.extend(yaml_list(item["tags"], 6))
        lines.append(f"    stars: {item['stars']}")
        lines.append(f"    score: {item['score']}")
        lines.append(f"    verdict: {scalar(item['verdict'])}")
        lines.append(f"    captured_at: {scalar(item['captured_at'])}")
    lines.append("manual_inbox:")
    for entry in data["manual_inbox"]:
        lines.append(f"  - title: {scalar(entry['title'])}")
        lines.append(f"    url: {scalar(entry['url'])}")
        lines.append(f"    note: {scalar(entry['note'])}")
        lines.append(f"    status: {scalar(entry['status'])}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def normalize_tags(values: list[str] | None) -> list[str]:
    tags = []
    for value in values or []:
        cleaned = re.sub(r"[^a-zA-Z0-9.+#-]+", "-", value.lower()).strip("-")
        if cleaned and cleaned not in tags:
            tags.append(cleaned)
    return tags[:8]


def is_relevant_hn(hit: dict[str, Any]) -> bool:
    haystack = " ".join(
        [
            str(hit.get("title") or ""),
            str(hit.get("url") or ""),
            str(hit.get("story_text") or ""),
        ]
    ).lower()
    return any(term in haystack for term in HN_RELEVANCE_TERMS)


def summarize(text: str | None, fallback: str) -> str:
    source = re.sub(r"\s+", " ", (text or "").strip()) or fallback
    if len(source) <= 180:
        return source
    return source[:177].rstrip() + "..."


def verdict(score: int, tested: bool = False) -> str:
    if not tested:
        return "Watch" if score >= 45 else "Skip"
    if score >= 78:
        return "Adopt"
    if score >= 55:
        return "Watch"
    return "Skip"


def collect_github(days: int, limit: int) -> list[dict[str, Any]]:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).date().isoformat()
    seen: set[str] = set()
    candidates: list[dict[str, Any]] = []

    query_specs = []
    for topic in GITHUB_TOPICS:
        query_specs.append(
            {
                "topic": topic,
                "kind": "fresh",
                "query": f"topic:{topic} created:>{since} stars:>5",
                "sort": "stars",
                "reason": f"new repo, topic:{topic}, created within {days}d",
            }
        )
        query_specs.append(
            {
                "topic": topic,
                "kind": "updated",
                "query": f"topic:{topic} pushed:>{since} stars:>1000",
                "sort": "updated",
                "reason": f"major repo update, topic:{topic}, pushed within {days}d",
            }
        )

    for spec in query_specs:
        params = urllib.parse.urlencode(
            {
                "q": spec["query"],
                "sort": spec["sort"],
                "order": "desc",
                "per_page": min(limit, 15),
            }
        )
        url = f"https://api.github.com/search/repositories?{params}"
        try:
            payload = request_json(url, headers)
        except Exception as exc:  # noqa: BLE001 - keep radar best-effort.
            print(f"warn: GitHub query {spec['query']} failed: {exc}", file=sys.stderr)
            continue

        for repo in payload.get("items", []):
            full_name = repo.get("full_name")
            if not full_name or full_name in seen:
                continue
            seen.add(full_name)
            stars = int(repo.get("stargazers_count") or 0)
            created_recently = repo.get("created_at", "")[:10] >= since
            freshness = 30 if created_recently else 15
            star_signal = min(stars // (25 if created_recently else 500), 35)
            score = min(100, 25 + star_signal + freshness)
            repo_topics = normalize_tags(repo.get("topics"))
            candidates.append(
                {
                    "name": full_name,
                    "source": "github",
                    "url": repo.get("html_url", ""),
                    "summary": summarize(repo.get("description"), full_name),
                    "reason": f"{spec['reason']}, stars:{stars}",
                    "category": f"open-source/{spec['kind']}",
                    "tags": repo_topics or [spec["topic"]],
                    "stars": stars,
                    "score": score,
                    "verdict": verdict(score),
                    "captured_at": dt.datetime.now(dt.timezone.utc).date().isoformat(),
                }
            )

    return sorted(candidates, key=lambda item: (item["score"], item["stars"]), reverse=True)


def collect_hn(days: int, limit: int) -> list[dict[str, Any]]:
    after = int((dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).timestamp())
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()

    for query in HN_QUERIES:
        params = urllib.parse.urlencode(
            {
                "query": query,
                "tags": "story",
                "numericFilters": f"created_at_i>{after},points>20",
                "hitsPerPage": min(limit, 20),
            }
        )
        url = f"https://hn.algolia.com/api/v1/search_by_date?{params}"
        try:
            payload = request_json(url)
        except Exception as exc:  # noqa: BLE001
            print(f"warn: Hacker News query {query} failed: {exc}", file=sys.stderr)
            continue

        for hit in payload.get("hits", []):
            if not is_relevant_hn(hit):
                continue
            object_id = hit.get("objectID")
            if not object_id or object_id in seen:
                continue
            seen.add(object_id)
            points = int(hit.get("points") or 0)
            comments = int(hit.get("num_comments") or 0)
            score = min(100, 30 + min(points // 5, 35) + min(comments // 3, 20))
            candidates.append(
                {
                    "name": hit.get("title") or f"HN story {object_id}",
                    "source": "hacker-news",
                    "url": hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}",
                    "summary": summarize(hit.get("title"), f"Hacker News discussion for {query}"),
                    "reason": f"query:{query}, points:{points}, comments:{comments}",
                    "category": "discussion",
                    "tags": normalize_tags(query.split()),
                    "stars": 0,
                    "score": score,
                    "verdict": verdict(score),
                    "captured_at": dt.datetime.now(dt.timezone.utc).date().isoformat(),
                }
            )

    return sorted(candidates, key=lambda item: item["score"], reverse=True)


def base_data(days: int, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "window_days": days,
        "sources": [
            {
                "name": "GitHub Search",
                "url": "https://api.github.com/search/repositories",
                "signal": "Recently updated AI, LLM, agent, RAG, MCP repositories",
            },
            {
                "name": "Hacker News Algolia",
                "url": "https://hn.algolia.com/api/v1/search_by_date",
                "signal": "Developer discussions about AI infrastructure and tools",
            },
            {
                "name": "Manual Inbox",
                "url": "",
                "signal": "Threads, X, Discord, newsletters, private notes",
            },
        ],
        "candidates": candidates,
        "manual_inbox": [
            {
                "title": "Threads에서 본 AI 도구",
                "url": "",
                "note": "원문 링크와 공식 저장소를 확인한 뒤 candidates로 승격한다.",
                "status": "triage",
            }
        ],
    }


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9가-힣]+", "-", text.lower()).strip("-")
    return slug or "ai-radar"


def create_draft(data: dict[str, Any], dry_run: bool) -> Path:
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date().isoformat()
    path = DRAFT_DIR / f"{today}-ai-radar.md"
    top = data["candidates"][:5]
    lines = [
        "---",
        f'title: "AI Radar: {today}"',
        f"date: {today} 09:00:00 +0900",
        "categories: [AI, OpenSource]",
        "tags: [ai, radar, open-source, llm]",
        "published: false",
        "---",
        "",
        "오늘 볼 AI 기술 후보를 정리한다. 자동 수집 결과는 출발점이고, 최종 판단은 직접 실행 후 확정한다.",
        "",
        "## 후보",
        "",
    ]
    for index, item in enumerate(top, 1):
        lines.extend(
            [
                f"### {index}. {item['name']}",
                "",
                f"- 출처: {item['source']}",
                f"- 링크: {item['url']}",
                f"- 점수: {item['score']}",
                f"- 1차 판단: {item['verdict']}",
                f"- 이유: {item['reason']}",
                "",
                item["summary"],
                "",
                "검증 메모:",
                "",
                "- 설치:",
                "- 백엔드 통합:",
                "- 운영 리스크:",
                "- 최종 판단:",
                "",
            ]
        )
    lines.extend(
        [
            "## 오늘의 결론",
            "",
            "- Adopt:",
            "- Watch:",
            "- Skip:",
            "",
        ]
    )
    if not dry_run:
        DRAFT_DIR.mkdir(exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect AI Radar candidates.")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--write-data", action="store_true")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    candidates = collect_github(args.days, args.limit) + collect_hn(args.days, args.limit)
    candidates = sorted(candidates, key=lambda item: (item["score"], item["stars"]), reverse=True)
    candidates = candidates[: max(args.limit, 1)]
    data = base_data(args.days, candidates)

    if args.write_data and not args.dry_run:
        write_yaml(data, DATA_FILE)
    if args.draft:
        draft_path = create_draft(data, args.dry_run)
        print(f"draft: {draft_path.relative_to(ROOT)}")

    print(json.dumps({"generated_at": data["generated_at"], "count": len(candidates)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
