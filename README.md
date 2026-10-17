# Amin Alizadeh: AI & Data Engineer

Personal portfolio: **[amin-alzz96.github.io](https://amin-alzz96.github.io/)**

Enterprise AI work, data engineering experience, skills, credentials, personal projects, and a bookshelf. Built with HTML, CSS, and vanilla JavaScript, using the existing dark teal design.

## Website

- Static files live in `docs/`, served by GitHub Pages from `main`.
- Tabs support direct section links, keyboard navigation, and browser history.
- Enterprise project descriptions distinguish individual and team contributions. Personal projects and learning labs have their own section.
- Credential cards link to the supplied credential pages. SQLBI Mastering DAX is listed as professional development without a link.

Preview the public website without running the backend:

```sh
python3 -m http.server 8000 --directory docs
```

## Backend

The existing FastAPI chat backend (`app.py`, `main.py`) is paused. It is not deployed and no chat interface is exposed on the website. Its local profile context loads directly into the model context.

Private context, environment files, project instructions, and Obsidian backups are excluded from version control. The public portfolio does not include personal documents.
