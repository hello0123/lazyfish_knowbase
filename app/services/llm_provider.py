from abc import ABC, abstractmethod

import httpx


class LLMProvider(ABC):
    """摘要與標籤產生的抽象層,實作留給第 2 週(Ollama)與第 4 週(Claude)。"""

    @abstractmethod
    def summarize(self, text: str) -> str: ...

    @abstractmethod
    def extract_tags(self, text: str) -> list[str]: ...


class OllamaProvider(LLMProvider):
    """開發期使用的本地 LLM provider,透過 Ollama 的 HTTP API 呼叫模型。"""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def summarize(self, text: str) -> str:
        prompt = "用一到兩句話摘要以下內容,只回傳摘要文字,不要加其他說明:\n\n" + text[:4000]
        return self._generate(prompt)

    def extract_tags(self, text: str) -> list[str]:
        prompt = (
            "從以下內容整理出 3 到 5 個中文關鍵字標籤,用逗號分隔,不要加其他文字或編號:\n\n"
            + text[:4000]
        )
        raw = self._generate(prompt)
        return [tag.strip() for tag in raw.split(",") if tag.strip()]

    def _generate(self, prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["response"].strip()
