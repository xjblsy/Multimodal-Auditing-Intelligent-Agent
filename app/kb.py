from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from hashlib import sha1
from pathlib import Path
from typing import Any

from .config import AppConfig


def now_iso() -> str:
    from datetime import datetime

    return datetime.now().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    base = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    if base:
        return base[:60]
    digest = sha1((value or "entry").encode("utf-8")).hexdigest()[:10]
    return f"entry-{digest}"


def split_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        if "\n" in value:
            lines = value.splitlines()
            return [line.strip("- ").strip() for line in lines if line.strip()]
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def split_markdown_sections(markdown_text: str) -> list[dict[str, str]]:
    text = (markdown_text or "").strip()
    if not text:
        return []
    sections: list[dict[str, str]] = []
    current_heading = "实践说明"
    buffer: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if buffer:
                sections.append(
                    {
                        "heading": current_heading,
                        "body": "\n".join(buffer).strip(),
                    }
                )
                buffer = []
            current_heading = line[3:].strip() or "实践说明"
            continue
        buffer.append(line)
    if buffer:
        sections.append({"heading": current_heading, "body": "\n".join(buffer).strip()})
    return sections


def build_match_expression(query: str) -> str:
    tokens = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", query)
    if not tokens:
        return ""
    return " OR ".join(f'"{token}"' for token in tokens[:10])


def tokenize_for_search(text: str) -> set[str]:
    tokens: set[str] = set()
    lower_text = (text or "").lower()
    for token in re.findall(r"[a-z0-9]+", lower_text):
        if len(token) > 1:
            tokens.add(token)
    for chunk in re.findall(r"[\u4e00-\u9fff]+", text or ""):
        if len(chunk) <= 4:
            tokens.add(chunk)
        else:
            for size in (2, 3, 4):
                for index in range(0, len(chunk) - size + 1):
                    tokens.add(chunk[index : index + size])
    return tokens


class KnowledgeBase:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.config.generated_dir.mkdir(parents=True, exist_ok=True)
        self.rebuild_index()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.config.index_db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _normalize_item(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = str(payload.get("title") or "未命名知识条目").strip()
        item_id = str(payload.get("id") or slugify(title)).strip()
        body_markdown = str(payload.get("body_markdown") or "").strip()
        sections = payload.get("content_sections") or split_markdown_sections(body_markdown)
        normalized = {
            "id": item_id,
            "title": title,
            "category": str(payload.get("category") or "审计通识").strip(),
            "industries": split_list(payload.get("industries") or payload.get("industry") or ["通用"]),
            "difficulty": str(payload.get("difficulty") or "中级").strip(),
            "tags": split_list(payload.get("tags")),
            "summary": str(payload.get("summary") or "").strip(),
            "learning_objectives": split_list(payload.get("learning_objectives")),
            "content_sections": [
                {
                    "heading": str(section.get("heading") or "实践说明").strip(),
                    "body": str(section.get("body") or "").strip(),
                }
                for section in sections
                if str(section.get("body") or "").strip()
            ],
            "checklist": split_list(payload.get("checklist")),
            "red_flags": split_list(payload.get("red_flags")),
            "common_mistakes": split_list(payload.get("common_mistakes")),
            "questions": [
                {
                    "q": str(item.get("q") or "").strip(),
                    "a": str(item.get("a") or "").strip(),
                }
                for item in (payload.get("questions") or [])
                if str(item.get("q") or "").strip() and str(item.get("a") or "").strip()
            ],
            "modalities": payload.get("modalities") or {"visuals": [], "videos": [], "tables": []},
            "related_ids": split_list(payload.get("related_ids")),
            "updated_at": str(payload.get("updated_at") or now_iso()),
        }
        normalized["body_markdown"] = self._compose_markdown(normalized["content_sections"])
        return normalized

    def _normalize_scenario(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = str(payload.get("title") or "未命名案例").strip()
        scenario_id = str(payload.get("id") or slugify(title)).strip()
        normalized_stages: list[dict[str, Any]] = []
        for index, stage in enumerate(payload.get("stages") or [], start=1):
            normalized_stages.append(
                {
                    "id": str(stage.get("id") or f"stage-{index}").strip(),
                    "title": str(stage.get("title") or f"阶段 {index}").strip(),
                    "task": str(stage.get("task") or "").strip(),
                    "evidence": split_list(stage.get("evidence")),
                    "must_have": split_list(stage.get("must_have")),
                    "excellent_signals": split_list(stage.get("excellent_signals")),
                    "coach_tip": str(stage.get("coach_tip") or "").strip(),
                }
            )
        return {
            "id": scenario_id,
            "title": title,
            "industry": str(payload.get("industry") or "通用").strip(),
            "difficulty": str(payload.get("difficulty") or "中级").strip(),
            "background": str(payload.get("background") or "").strip(),
            "goals": split_list(payload.get("goals")),
            "references": split_list(payload.get("references")),
            "stages": normalized_stages,
            "updated_at": str(payload.get("updated_at") or now_iso()),
        }

    def _compose_markdown(self, sections: list[dict[str, str]]) -> str:
        blocks: list[str] = []
        for section in sections:
            heading = section.get("heading", "实践说明").strip()
            body = section.get("body", "").strip()
            if not body:
                continue
            blocks.append(f"## {heading}\n{body}")
        return "\n\n".join(blocks)

    def rebuild_index(self) -> dict[str, int]:
        conn = self._connect()
        try:
            conn.executescript(
                """
                DROP TABLE IF EXISTS items;
                DROP TABLE IF EXISTS scenarios;
                DROP TABLE IF EXISTS docs;
                CREATE TABLE items (
                    item_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT,
                    industries TEXT,
                    difficulty TEXT,
                    tags TEXT,
                    summary TEXT,
                    payload TEXT NOT NULL
                );
                CREATE TABLE scenarios (
                    scenario_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    industry TEXT,
                    difficulty TEXT,
                    payload TEXT NOT NULL
                );
                CREATE VIRTUAL TABLE docs USING fts5(
                    item_id UNINDEXED,
                    title,
                    summary,
                    body,
                    tags,
                    industries,
                    tokenize = 'unicode61'
                );
                """
            )
            item_count = 0
            for path in sorted(self.config.knowledge_dir.glob("*.json")):
                payload = self._normalize_item(self._read_json(path))
                joined_body = "\n\n".join(
                    section["body"] for section in payload["content_sections"] if section["body"]
                )
                conn.execute(
                    """
                    INSERT INTO items(item_id, title, category, industries, difficulty, tags, summary, payload)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload["id"],
                        payload["title"],
                        payload["category"],
                        json.dumps(payload["industries"], ensure_ascii=False),
                        payload["difficulty"],
                        json.dumps(payload["tags"], ensure_ascii=False),
                        payload["summary"],
                        json.dumps(payload, ensure_ascii=False),
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO docs(item_id, title, summary, body, tags, industries)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload["id"],
                        payload["title"],
                        payload["summary"],
                        joined_body,
                        " ".join(payload["tags"]),
                        " ".join(payload["industries"]),
                    ),
                )
                item_count += 1
            scenario_count = 0
            for path in sorted(self.config.scenario_dir.glob("*.json")):
                payload = self._normalize_scenario(self._read_json(path))
                conn.execute(
                    """
                    INSERT INTO scenarios(scenario_id, title, industry, difficulty, payload)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        payload["id"],
                        payload["title"],
                        payload["industry"],
                        payload["difficulty"],
                        json.dumps(payload, ensure_ascii=False),
                    ),
                )
                scenario_count += 1
            conn.commit()
        finally:
            conn.close()
        return {"items": item_count, "scenarios": scenario_count}

    def list_items(self) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT payload FROM items ORDER BY title COLLATE NOCASE"
            ).fetchall()
            return [json.loads(row["payload"]) for row in rows]
        finally:
            conn.close()

    def get_item(self, item_id: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT payload FROM items WHERE item_id = ?",
                (item_id,),
            ).fetchone()
            return json.loads(row["payload"]) if row else None
        finally:
            conn.close()

    def list_scenarios(self) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT payload FROM scenarios ORDER BY title COLLATE NOCASE"
            ).fetchall()
            return [json.loads(row["payload"]) for row in rows]
        finally:
            conn.close()

    def get_scenario(self, scenario_id: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT payload FROM scenarios WHERE scenario_id = ?",
                (scenario_id,),
            ).fetchone()
            return json.loads(row["payload"]) if row else None
        finally:
            conn.close()

    def search(
        self,
        query: str = "",
        industry: str = "",
        tags: list[str] | None = None,
        limit: int = 6,
    ) -> list[dict[str, Any]]:
        tags = tags or []
        all_items = self.list_items()
        if not query.strip():
            filtered = [
                item
                for item in all_items
                if (not industry or industry in item["industries"])
                and (not tags or set(tags).issubset(set(item["tags"])))
            ]
            return filtered[:limit]
        conn = self._connect()
        try:
            match_expr = build_match_expression(query.strip())
            rows = []
            if match_expr:
                rows = conn.execute(
                    """
                    SELECT items.payload, bm25(docs) AS rank
                    FROM docs
                    JOIN items ON items.item_id = docs.item_id
                    WHERE docs MATCH ?
                    ORDER BY rank
                    LIMIT 24
                    """,
                    (match_expr,),
                ).fetchall()
        finally:
            conn.close()
        fts_positions: dict[str, int] = {}
        for index, row in enumerate(rows):
            payload = json.loads(row["payload"])
            fts_positions[payload["id"]] = index

        query_tokens = tokenize_for_search(query)
        ranked: list[tuple[float, dict[str, Any]]] = []
        lower_query = query.lower()
        tag_set = set(tags)
        for item in all_items:
            if industry and industry not in item["industries"] and "通用" not in item["industries"]:
                continue
            if tag_set and not tag_set.issubset(set(item["tags"])):
                continue
            search_text = " ".join(
                [
                    item["title"],
                    item["summary"],
                    " ".join(item["tags"]),
                    " ".join(item["industries"]),
                    " ".join(section["heading"] for section in item["content_sections"]),
                    " ".join(section["body"] for section in item["content_sections"]),
                ]
            )
            item_tokens = tokenize_for_search(search_text)
            overlap = len(query_tokens & item_tokens)
            score = 15 + (overlap * 4)
            if item["id"] in fts_positions:
                score += 50 - (fts_positions[item["id"]] * 4)
            if industry and industry in item["industries"]:
                score += 8
            if any(tag in item["tags"] for tag in tag_set):
                score += 6
            if lower_query in item["title"].lower():
                score += 8
            if any(lower_query in section["body"].lower() for section in item["content_sections"]):
                score += 4
            if any(tag in query for tag in item["tags"]):
                score += 10
            if any(industry_name in query for industry_name in item["industries"]):
                score += 6
            if any(keyword in query for keyword in item["title"].split()):
                score += 3
            if overlap or item["id"] in fts_positions or not query_tokens:
                ranked.append((score, item))
        if not ranked:
            ranked = [
                (
                    10 + sum(1 for tag in item["tags"] if tag in lower_query),
                    item,
                )
                for item in all_items
                if lower_query in json.dumps(item, ensure_ascii=False).lower()
            ]
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in ranked[:limit]]

    def upsert_item(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = self._normalize_item(payload)
        path = self.config.knowledge_dir / f"{normalized['id']}.json"
        self._write_json(path, normalized)
        self.rebuild_index()
        return normalized

    def delete_item(self, item_id: str) -> bool:
        path = self.config.knowledge_dir / f"{item_id}.json"
        if not path.exists():
            return False
        path.unlink()
        self.rebuild_index()
        return True
