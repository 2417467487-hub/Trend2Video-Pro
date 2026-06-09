# Contributing

Thanks for helping improve Trend2Video Pro.

This project is an execution engine, not a dashboard. Contributions should keep the core promise intact: turn a trend into a publish-ready short video package with quality control.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

## Good First Issues

- Add a new video template.
- Improve topic scoring heuristics.
- Add a collector with mock fallback.
- Improve subtitle layout or keyword highlighting.
- Add tests for edge cases.

## Pull Requests

- Keep changes focused.
- Add or update tests when behavior changes.
- Do not require real API keys for tests.
- Keep generated media, databases, and local `.env` files out of commits.
