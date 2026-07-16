from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """摘要與標籤產生的抽象層,實作留給第 2 週(Ollama)與第 4 週(Claude)。"""

    @abstractmethod
    def summarize(self, text: str) -> str: ...

    @abstractmethod
    def extract_tags(self, text: str) -> list[str]: ...
