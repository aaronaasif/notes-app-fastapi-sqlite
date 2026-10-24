# Notes App (FastAPI + SQLite)

A small full-stack notes app built with Python and FastAPI. It has a web page for adding, ticking off and deleting notes, a JSON API behind it, and a SQLite database so notes survive restarts. User sign-up with safely hashed passwords is in place, and login is being added step by step.

FastAPI also builds an interactive test page for the API automatically, so every endpoint can be tried from the browser.

## Features

- Web page at `/`: add a note with the **Submit** button, tick it as done, delete it
- Live counter showing how many notes are done (for example "2 of 3 done")
- Full CRUD API for notes, with a `done` flag
- Data saved in SQLite (`notes.db`, created automatically next to `notes_app.py`)
- User sign-up: passwords are hashed with Argon2 and never stored as plain text
- Input checks: a note without a title is rejected, a duplicate email returns `409 Conflict`
- Proper errors: asking for a missing note returns `404 Not Found`
- Automatic API documentation at `/docs`

## Endpoints

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/` | The notes web page |
| POST | `/notes` | Add a note - requires login |
| GET | `/notes` | List all notes, newest first - requires login |
| GET | `/notes/{id}` | Get one note - requires login |
| PUT | `/notes/{id}` | Change a note - requires login |
| DELETE | `/notes/{id}` | Delete a note - requires login |
| POST | `/users` | Sign up with an email and password |
| POST | `/login` | Sign in with an email and password |
| GET | `/me` | Verify the current logged in user |

Example body for `POST` and `PUT` on `/notes`:

```json
{
  "title": "Buy milk",
  "body": "Two litres",
  "done": false
}
```

Example body for `POST /users`:

```json
{
  "email": "ali@example.com",
  "password": "secret123"
}
```

The response contains only the user's `id` and `email`. The password hash is never returned.

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Mac/Linux: source .venv/bin/activate)
python -m pip install fastapi uvicorn "pwdlib[argon2]"
uvicorn notes_app:app --reload
```

Then open:

- http://127.0.0.1:8000/ for the notes page
- http://127.0.0.1:8000/docs to try the API

Run the command from the project folder. The database file always sits next to `notes_app.py`, wherever you start the app from.

## Notes

- `notes.db` is listed in `.gitignore`, so your data and users are never uploaded to GitHub.
- Notes are not tied to users yet. Login, and showing each person only their own notes, comes next. Do not put this on the internet before that is done.
- If you change the structure of a table that already exists while practising, delete `notes.db` and restart so a new table is created.
- The web page’s login form is the next step, because the page can’t call the protected routes yet.

## Roadmap

- [x] SQLite database with CRUD API
- [x] Web page with submit form, done tick box and counter
- [x] User sign-up with hashed passwords
- [x] Login with a token
- [x] Each user sees only their own notes
- [ ] Deploy online with a hosted database

## Built with

Python, FastAPI, SQLite (Python's built-in `sqlite3` module), Pydantic, pwdlib (Argon2), plain HTML, CSS and JavaScript.



