# Trend2Video Pro Chrome Extension

This lightweight extension adds a `Generate Video` button on GitHub, Product Hunt, and Hacker News pages.

It sends the current page title and URL to your local API:

```bash
uvicorn api:app --reload
```

Endpoint used:

```text
POST http://127.0.0.1:8000/api/generate
```

Load it in Chrome:

1. Open `chrome://extensions`.
2. Enable Developer mode.
3. Click `Load unpacked`.
4. Select the `extension/` folder.
