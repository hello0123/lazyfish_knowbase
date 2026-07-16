# 個人知識庫 API + AI 摘要

規劃文件見 [`../專案A_個人知識庫API_規劃.md`](../專案A_個人知識庫API_規劃.md)。

## 開發

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## 測試

```bash
pytest -v
ruff check .
```
