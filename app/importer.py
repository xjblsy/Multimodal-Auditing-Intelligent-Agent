from __future__ import annotations

import json
import mimetypes
import shutil
import time
import urllib.error
import urllib.request
import uuid
import zipfile
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from .config import AppConfig
from .kb import KnowledgeBase, slugify


TEXT_SUFFIXES = {".txt", ".md"}
DOCX_SUFFIXES = {".docx"}
REMOTE_SUFFIXES = {
    ".txt",
    ".md",
    ".doc",
    ".docx",
    ".pdf",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


class ImportError(RuntimeError):
    pass


@dataclass(slots=True)
class ImportOptions:
    category: str = "资料导入"
    industry: str = "通用"
    tags: list[str] | None = None
    difficulty: str = "中级"
    use_remote: bool = False
    keep_remote_file: bool = False


class ImportManager:
    def __init__(self, config: AppConfig, kb: KnowledgeBase) -> None:
        self.config = config
        self.kb = kb

    def ingest_path(self, source: Path, options: ImportOptions) -> list[dict[str, Any]]:
        if not source.exists():
            raise ImportError(f"导入源不存在: {source}")
        if source.is_dir():
            results: list[dict[str, Any]] = []
            for path in sorted(source.iterdir()):
                if path.is_file() and not self._is_sidecar(path):
                    results.append(self.ingest_file(path, options))
            return results
        return [self.ingest_file(source, options)]

    def ingest_file(self, source: Path, options: ImportOptions) -> dict[str, Any]:
        suffix = source.suffix.lower()
        if options.use_remote and suffix in REMOTE_SUFFIXES:
            entry = self._ingest_with_dashscope(source, options)
        elif suffix in TEXT_SUFFIXES:
            entry = self._ingest_text_like(source, options)
        elif suffix in DOCX_SUFFIXES:
            entry = self._ingest_docx(source, options)
        elif suffix in IMAGE_SUFFIXES:
            entry = self._ingest_image_stub(source, options)
        else:
            raise ImportError(
                f"暂不支持直接导入 {suffix or '无扩展名'} 文件。"
                "可以使用 --remote 走百炼文档抽取，或提供同名 .txt/.md 说明文件。"
            )

        saved = self.kb.upsert_item(entry)
        return {
            "id": saved["id"],
            "title": saved["title"],
            "source": str(source),
            "mode": "remote" if options.use_remote and suffix in REMOTE_SUFFIXES else "local",
        }

    def _ingest_text_like(self, source: Path, options: ImportOptions) -> dict[str, Any]:
        text = source.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            raise ImportError(f"文件内容为空: {source}")
        title = source.stem.replace("_", " ").replace("-", " ").strip() or source.stem
        asset = self._copy_media_if_needed(source)
        notes = self._load_sidecar_text(source)
        content = text if len(text) > len(notes) else notes
        return self._build_entry_from_text(title, content, options, source, asset)

    def _ingest_docx(self, source: Path, options: ImportOptions) -> dict[str, Any]:
        text = self._extract_docx_text(source)
        if not text.strip():
            raise ImportError(f"未能从 DOCX 提取文本: {source}")
        title = source.stem.replace("_", " ").replace("-", " ").strip() or source.stem
        asset = self._copy_media_if_needed(source)
        return self._build_entry_from_text(title, text, options, source, asset)

    def _ingest_image_stub(self, source: Path, options: ImportOptions) -> dict[str, Any]:
        asset = self._copy_media_if_needed(source)
        notes = self._load_sidecar_text(source)
        title = source.stem.replace("_", " ").replace("-", " ").strip() or source.stem
        body = notes or (
            "## 图片资料说明\n"
            "这是一个已接入知识库的图片资料。建议补充同名 `.txt` 或 `.md` 说明文件，"
            "写明图片对应的业务背景、审计任务、证据含义和应用场景。"
        )
        entry = self._build_entry_from_text(title, body, options, source, asset)
        entry["summary"] = entry["summary"] or "图片资料已接入，建议补充说明文本以提升问答效果。"
        return entry

    def _build_entry_from_text(
        self,
        title: str,
        text: str,
        options: ImportOptions,
        source: Path,
        asset: dict[str, Any] | None,
    ) -> dict[str, Any]:
        clean_text = text.strip()
        summary = self._build_summary(clean_text)
        entry_id = slugify(f"{title}-{source.stem}")
        body_markdown = clean_text if clean_text.lstrip().startswith("## ") else f"## 导入原文\n{clean_text}"
        modalities = {"visuals": [], "videos": [], "tables": []}
        if asset:
            target_group = "visuals" if asset.get("type") == "image" else "videos"
            modalities[target_group].append(asset)
        return {
            "id": entry_id,
            "title": title,
            "category": options.category,
            "industries": [options.industry],
            "difficulty": options.difficulty,
            "tags": list(options.tags or []) + ["资料导入"],
            "summary": summary,
            "learning_objectives": [
                "理解导入资料对应的业务背景",
                "将资料内容映射到审计风险和程序设计",
            ],
            "body_markdown": body_markdown,
            "checklist": [
                f"核实资料来源与版本：{source.name}",
                "补充与该资料配套的项目背景、制度或底稿说明",
                "将关键判断转化为可执行的审计程序",
            ],
            "red_flags": [
                "资料缺少业务背景或版本信息",
                "材料只有截图，没有说明其与审计结论的关系",
            ],
            "common_mistakes": [
                "把原始资料直接丢进知识库，却没有补充解释和适用场景",
                "没有区分制度说明、底稿样例和项目复盘三类资料",
            ],
            "questions": [
                {
                    "q": "这份资料最适合拿来训练什么能力？",
                    "a": "优先训练资料解读、风险识别和将原始材料转化为审计动作的能力。",
                }
            ],
            "modalities": modalities,
            "related_ids": [],
        }

    def _ingest_with_dashscope(self, source: Path, options: ImportOptions) -> dict[str, Any]:
        if self.config.model_provider != "dashscope":
            raise ImportError("远程资料抽取当前仅支持阿里云百炼（dashscope）配置。")
        if not self.config.api_key:
            raise ImportError("未配置阿里云百炼 API Key，无法使用远程资料抽取。")

        file_id = self._upload_remote_file(source)
        try:
            self._wait_until_remote_ready(file_id)
            extracted = self._ask_remote_doc_model(file_id, source, options)
        finally:
            if not options.keep_remote_file:
                self._delete_remote_file(file_id)

        asset = self._copy_media_if_needed(source)
        return self._normalize_remote_entry(extracted, source, options, asset)

    def _upload_remote_file(self, source: Path) -> str:
        boundary = f"----CodexBoundary{uuid.uuid4().hex}"
        file_bytes = source.read_bytes()
        mime_type = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
        body = b"".join(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                b'Content-Disposition: form-data; name="purpose"\r\n\r\n',
                b"file-extract\r\n",
                f"--{boundary}\r\n".encode("utf-8"),
                (
                    f'Content-Disposition: form-data; name="file"; filename="{source.name}"\r\n'
                    f"Content-Type: {mime_type}\r\n\r\n"
                ).encode("utf-8"),
                file_bytes,
                b"\r\n",
                f"--{boundary}--\r\n".encode("utf-8"),
            ]
        )
        request = urllib.request.Request(
            url=f"{self.config.openai_base_url.rstrip('/')}/files",
            data=body,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ImportError(f"文件上传到百炼失败: {exc.code} {detail}") from exc

        file_id = payload.get("id")
        if not file_id:
            raise ImportError(f"文件上传成功但未返回 file_id: {payload}")
        return str(file_id)

    def _wait_until_remote_ready(self, file_id: str) -> None:
        url = f"{self.config.openai_base_url.rstrip('/')}/files/{file_id}"
        for _ in range(15):
            request = urllib.request.Request(
                url=url,
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                method="GET",
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            status = str(payload.get("status") or "").lower()
            if status in {"processed", "ready", "success"}:
                return
            if status in {"error", "failed"}:
                raise ImportError(f"百炼文件处理失败: {payload}")
            time.sleep(2)
        raise ImportError(f"百炼文件处理超时: {file_id}")

    def _ask_remote_doc_model(
        self,
        file_id: str,
        source: Path,
        options: ImportOptions,
    ) -> dict[str, Any]:
        system_prompt = (
            "你是一名会计审计知识工程师。"
            "请从文件中提炼适合审计训练的结构化知识，返回严格 JSON。"
            "字段包括 title, summary, tags, learning_objectives, body_markdown, checklist, red_flags, common_mistakes。"
            "内容必须面向会计审计场景，不能输出额外解释。"
        )
        user_prompt = (
            f"请整理文件《{source.name}》。"
            f"行业默认按“{options.industry}”，分类按“{options.category}”。"
            "若原文偏制度、底稿或项目复盘，请在正文中明确其适用场景。"
        )
        payload = {
            "model": self.config.doc_model_name,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"fileid://{file_id}"},
                {"role": "user", "content": user_prompt},
            ],
        }
        request = urllib.request.Request(
            url=f"{self.config.openai_base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ImportError(f"百炼文档抽取失败: {exc.code} {detail}") from exc

        content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        if isinstance(content, list):
            content = "\n".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("text")
            )
        parsed = self._extract_json_object(str(content))
        if not isinstance(parsed, dict):
            raise ImportError(f"百炼文档抽取返回的不是 JSON 对象: {content}")
        return parsed

    def _delete_remote_file(self, file_id: str) -> None:
        request = urllib.request.Request(
            url=f"{self.config.openai_base_url.rstrip('/')}/files/{file_id}",
            headers={"Authorization": f"Bearer {self.config.api_key}"},
            method="DELETE",
        )
        try:
            urllib.request.urlopen(request, timeout=30).read()
        except Exception:
            return

    def _normalize_remote_entry(
        self,
        extracted: dict[str, Any],
        source: Path,
        options: ImportOptions,
        asset: dict[str, Any] | None,
    ) -> dict[str, Any]:
        title = str(extracted.get("title") or source.stem).strip()
        tags = self._normalize_list(extracted.get("tags")) + list(options.tags or [])
        learning_objectives = self._normalize_list(extracted.get("learning_objectives"))
        checklist = self._normalize_list(extracted.get("checklist"))
        red_flags = self._normalize_list(extracted.get("red_flags"))
        mistakes = self._normalize_list(extracted.get("common_mistakes"))
        body_markdown = str(extracted.get("body_markdown") or "").strip()
        summary = str(extracted.get("summary") or self._build_summary(body_markdown)).strip()

        modalities = {"visuals": [], "videos": [], "tables": []}
        if asset:
            group = "visuals" if asset.get("type") == "image" else "videos"
            modalities[group].append(asset)

        return {
            "id": slugify(f"{title}-{source.stem}"),
            "title": title,
            "category": options.category,
            "industries": [options.industry],
            "difficulty": options.difficulty,
            "tags": list(OrderedDict.fromkeys([*tags, "远程抽取"])),
            "summary": summary,
            "learning_objectives": learning_objectives or ["从导入文件中提炼审计判断和执行动作"],
            "body_markdown": body_markdown or "## 导入摘要\n模型未返回正文，请补充。",
            "checklist": checklist or ["复核模型提炼结果与原文是否一致"],
            "red_flags": red_flags,
            "common_mistakes": mistakes,
            "questions": [
                {
                    "q": "这份资料是如何进入知识库的？",
                    "a": f"该条目来自文件《{source.name}》，由阿里云百炼文档抽取模型整理后生成，建议人工复核后再用于正式训练。",
                }
            ],
            "modalities": modalities,
            "related_ids": [],
        }

    def _extract_docx_text(self, source: Path) -> str:
        with zipfile.ZipFile(source) as archive:
            try:
                xml_content = archive.read("word/document.xml")
            except KeyError as exc:
                raise ImportError(f"DOCX 文件缺少 word/document.xml: {source}") from exc
        root = ElementTree.fromstring(xml_content)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs: list[str] = []
        for para in root.findall(".//w:p", ns):
            texts = [node.text for node in para.findall(".//w:t", ns) if node.text]
            line = "".join(texts).strip()
            if line:
                paragraphs.append(line)
        return "\n".join(paragraphs)

    def _build_summary(self, text: str) -> str:
        normalized = " ".join(text.replace("\r", "\n").split())
        return normalized[:140] + ("..." if len(normalized) > 140 else "")

    def _copy_media_if_needed(self, source: Path) -> dict[str, Any] | None:
        if not source.suffix:
            return None
        destination_dir = self.config.media_dir / "imports"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / source.name
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
        if source.suffix.lower() in IMAGE_SUFFIXES:
            return {
                "type": "image",
                "title": source.stem,
                "path": f"/media/imports/{destination.name}",
                "caption": f"导入自文件 {source.name}",
            }
        if source.suffix.lower() in VIDEO_SUFFIXES:
            return {
                "type": "video",
                "title": source.stem,
                "path": f"/media/imports/{destination.name}",
                "caption": f"导入自文件 {source.name}",
            }
        return None

    def _load_sidecar_text(self, source: Path) -> str:
        for suffix in (".md", ".txt"):
            candidate = source.with_suffix(suffix)
            if candidate.exists() and candidate.resolve() != source.resolve():
                return candidate.read_text(encoding="utf-8", errors="ignore").strip()
        return ""

    def _extract_json_object(self, text: str) -> Any:
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = stripped.strip("`")
            if "\n" in stripped:
                stripped = stripped.split("\n", 1)[1]
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            return None
        return json.loads(stripped[start : end + 1])

    def _normalize_list(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [line.strip("- ").strip() for line in value.splitlines() if line.strip()]
        return []

    def _is_sidecar(self, path: Path) -> bool:
        suffix = path.suffix.lower()
        if suffix not in {".txt", ".md"}:
            return False
        stem_source_candidates = [path.with_suffix(ext) for ext in REMOTE_SUFFIXES.union(IMAGE_SUFFIXES)]
        return any(candidate.exists() and candidate.resolve() != path.resolve() for candidate in stem_source_candidates)
