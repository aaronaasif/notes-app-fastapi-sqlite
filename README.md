# Notes App (FastAPI + SQLite)

A small notes API built with Python and FastAPI. Notes are stored in a SQLite database file, so they are still there after the app restarts. It supports the four basic database actions (create, read, update, delete) and each note can be marked as done.

FastAPI builds an interactive test page automatically, so you can try every endpoint from the browser with no extra tools.

## Features

- Create, read, update and delete notes (CRUD)
- A `done` flag on each note
- Data saved in SQLite (`notes.db`, created automatically on first run)
- Input checks: a note without a title is rejected
- Proper errors: asking for a missing note returns `404 Not Found`
- Automatic API documentation at `/docs`

## Endpoints

| Method | Path | What it does |
| --- | --- | --- |
| POST | `/notes` | Add a note |
| GET | `/notes` | List all notes, newest first |
| GET | `/notes/{id}` | Get one note |
| PUT | `/notes/{id}` | Change a note |
| DELETE | `/notes/{id}` | Delete a note |

Example request body for POST and PUT:

```json
{
  "title": "Buy milk",
  "body": "Two litres",
  "done": false
}
```

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Mac/Linux: source .venv/bin/activate)
python -m pip install fastapi uvicorn
uvicorn notes_app:app --reload
```

Then open http://127.0.0.1:8000/docs and try the endpoints.

Start the app from the project folder. The database file is created in the folder you start it from.

## Notes

- `notes.db` is listed in `.gitignore`, so your data is never uploaded to GitHub.
- There is no login or user accounts yet. Add authentication before putting it on the internet.
- If you change the table structure while practising, delete `notes.db` and restart the app so a new table is created.

## Built with

Python, FastAPI, SQLite (Python's built-in `sqlite3` module).
