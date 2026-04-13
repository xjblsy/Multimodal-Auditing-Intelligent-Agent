from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from .config import AppConfig


class ModelError(RuntimeError):
    pass


@dataclass(slots=True)
class ModelResult:
    text: str
    provider: str
    model: str


class BaseProvider:
    provider_name = "mock"

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    @property
    def available(self) -> bool:
        return False

    def generate(self, system_prompt: str, user_prompt: str) -> ModelResult:
        raise ModelError("No live model configured.")


class MockProvider(BaseProvider):
    provider_name = "mock"


class OpenAICompatibleProvider(BaseProvider):
    provider_name = "openai-compatible"

    @property
    def available(self) -> bool:
        return bool(self.config.api_key and self.config.model_name)

    def generate(self, system_prompt: str, user_prompt: str) -> ModelResult:
        payload = {
            "model": self.config.model_name,
            "temperature": self.config.model_temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }
        if self.config.model_provider == "openrouter":
            headers["HTTP-Referer"] = "https://local.audit-agent.demo"
            headers["X-Title"] = "Accounting Audit Smart Coach"
        request = urllib.request.Request(
            url=f"{self.config.openai_base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ModelError(f"模型请求失败: {exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise ModelError(f"模型网络请求失败: {exc.reason}") from exc

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelError(f"模型响应格式异常: {body}") from exc

        if isinstance(content, list):
            text = "\n".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("text")
            ).strip()
        else:
            text = str(content).strip()

        return ModelResult(
            text=text,
            provider=self.config.model_provider,
            model=self.config.model_name,
        )


class OllamaProvider(BaseProvider):
    provider_name = "ollama"

    @property
    def available(self) -> bool:
        return bool(self.config.model_name)

    def generate(self, system_prompt: str, user_prompt: str) -> ModelResult:
        payload = {
            "model": self.config.model_name,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        request = urllib.request.Request(
            url=self.config.openai_base_url.rstrip("/") + "/api/chat",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ModelError(f"Ollama 请求失败: {exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise ModelError(f"Ollama 网络请求失败: {exc.reason}") from exc

        content = body.get("message", {}).get("content", "").strip()
        if not content:
            raise ModelError(f"Ollama 响应格式异常: {body}")
        return ModelResult(text=content, provider="ollama", model=self.config.model_name)


def build_provider(config: AppConfig) -> BaseProvider:
    provider = config.model_provider
    if provider in {"mock", "demo"}:
        return MockProvider(config)
    if provider in {"openrouter", "openai-compatible", "dashscope", "siliconflow"}:
        return OpenAICompatibleProvider(config)
    if provider == "ollama":
        return OllamaProvider(config)
    return MockProvider(config)
