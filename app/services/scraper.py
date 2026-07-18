import httpx
from bs4 import BeautifulSoup


class ScrapeError(Exception):
    """抓取或清理網頁內容失敗時拋出。"""


def fetch_and_clean(url: str) -> str:
    try:
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ScrapeError(f"failed to fetch {url}: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    if not text:
        raise ScrapeError(f"no readable text extracted from {url}")
    return text
