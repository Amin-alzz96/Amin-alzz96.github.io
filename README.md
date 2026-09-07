# Amin-alzz96.github.io — Personal Website

My personal CV / portfolio site: **[amin-alzz96.github.io](https://amin-alzz96.github.io/)**

Dark, minimal, single-column design with tab navigation — About, Experience, Education, Skills, Projects, and a CSS-only bookshelf of what I'm reading.

## Stack

- **Frontend** (`docs/`): hand-written HTML/CSS/vanilla JS, no build step, served by GitHub Pages
- **Chat backend** (`app.py`, `main.py`): FastAPI + OpenAI — an AI twin that answers questions as me, with my profile loaded directly into the model context (deliberately no vector DB). Not deployed yet; the chat UI is parked for a future release.

## Run locally

```bash
uv sync
uv run uvicorn app:app --port 8000   # serves the site + chat API at localhost:8000
```

> The `context/` knowledge-base folder and `.env` are intentionally untracked.

---

Built with [Claude Code](https://claude.com/claude-code).
