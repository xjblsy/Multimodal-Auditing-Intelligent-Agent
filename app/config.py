from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
SCENARIO_DIR = DATA_DIR / "scenarios"
MEDIA_DIR = DATA_DIR / "media"
GENERATED_DIR = DATA_DIR / "generated"
WEB_DIR = ROOT_DIR / "web"
IMPORT_DIR = DATA_DIR / "imports"
IMPORT_ARCHIVE_DIR = IMPORT_DIR / "archive"
PROFILE_PATH = DATA_DIR / "agent_profile.json"


def load_env_file(path: Path, *, override: bool = True) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        if not override and key in os.environ:
            continue
        os.environ[key] = value.strip().strip("'").strip('"')


def env_flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class AppConfig:
    root_dir: Path
    data_dir: Path
    knowledge_dir: Path
    scenario_dir: Path
    media_dir: Path
    generated_dir: Path
    web_dir: Path
    import_dir: Path
    import_archive_dir: Path
    profile_path: Path
    host: str
    port: int
    default_industry: str
    model_provider: str
    model_name: str
    api_key: str
    openai_base_url: str
    model_temperature: float
    doc_model_name: str
    vision_model_name: str
    enable_remote_import: bool

    @property
    def index_db_path(self) -> Path:
        return self.generated_dir / "knowledge.db"


def ensure_directories() -> None:
    for path in (
        GENERATED_DIR,
        KNOWLEDGE_DIR,
        SCENARIO_DIR,
        MEDIA_DIR,
        IMPORT_DIR,
        IMPORT_ARCHIVE_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def build_config() -> AppConfig:
    load_env_file(ROOT_DIR / ".env", override=True)
    ensure_directories()
    return AppConfig(
        root_dir=ROOT_DIR,
        data_dir=DATA_DIR,
        knowledge_dir=KNOWLEDGE_DIR,
        scenario_dir=SCENARIO_DIR,
        media_dir=MEDIA_DIR,
        generated_dir=GENERATED_DIR,
        web_dir=WEB_DIR,
        import_dir=IMPORT_DIR,
        import_archive_dir=IMPORT_ARCHIVE_DIR,
        profile_path=PROFILE_PATH,
        host=os.getenv("AUDIT_AGENT_HOST", "127.0.0.1"),
        port=int(os.getenv("AUDIT_AGENT_PORT", "7860")),
        default_industry=os.getenv("AUDIT_AGENT_DEFAULT_INDUSTRY", "制造业"),
        model_provider=os.getenv("AUDIT_AGENT_MODEL_PROVIDER", "dashscope").strip().lower(),
        model_name=os.getenv("AUDIT_AGENT_MODEL_NAME", "qwen-flash").strip(),
        api_key=os.getenv("AUDIT_AGENT_API_KEY", "").strip(),
        openai_base_url=os.getenv(
            "AUDIT_AGENT_OPENAI_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ).strip(),
        model_temperature=float(os.getenv("AUDIT_AGENT_MODEL_TEMPERATURE", "0.2")),
        doc_model_name=os.getenv("AUDIT_AGENT_DOC_MODEL_NAME", "qwen-doc-turbo").strip(),
        vision_model_name=os.getenv("AUDIT_AGENT_VISION_MODEL_NAME", "qwen-vl-ocr-latest").strip(),
        enable_remote_import=env_flag("AUDIT_AGENT_ENABLE_REMOTE_IMPORT", "false"),
    )
