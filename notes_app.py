"""Lesson 2: the same notes API, now with a web page.

Run:  uvicorn notes_app:app --reload
Open: http://127.0.0.1:8000/        (the notes page)
      http://127.0.0.1:8000/docs    (automatic API test page)
"""
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from pwdlib import PasswordHash
ph = PasswordHash.recommended()

# The database file always sits next to this script,
# no matter which folder you start the app from.
DB_FILE = Path(__file__).with_name("notes.db")

app = FastAPI(title="Notes app")


def get_db():
    """Open a connection to the database file."""
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row      # lets us read columns by name
    return db


def setup():
    """Create the table the first time the app starts."""
    with get_db() as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS notes (
                   id    INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   body  TEXT NOT NULL DEFAULT '',
                   done  BOOLEAN NOT NULL DEFAULT 0
               )"""
        )

#create a table for user and password
    #with get_db() as db:
        db.execute(
                    """CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          email TEXT NOT NULL UNIQUE,
                          password_hash TEXT NOT NULL
                      )"""
                )


setup()


class NoteIn(BaseModel):
    """The shape of data we accept from the browser."""
    title: str
    body: str = ""
    done: bool = False

# class for user login and registration
class SignupIn(BaseModel):
    """The shape of data we accept for user registration and login."""
    email: str
    password: str


def to_dict(row):
    """Turn a database row into a dict, with done as true/false."""
    note = dict(row)
    note["done"] = bool(note["done"])
    return note


# ---------------------------------------------------------------- API

@app.post("/notes", status_code=201)       # CREATE
def add_note(note: NoteIn):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO notes (title, body, done) VALUES (?, ?, ?)",
            (note.title, note.body, int(note.done)),
        )
        return {"id": cur.lastrowid, **note.model_dump()}


# A route for user registration
@app.post("/users", status_code=201)
def register_user(user: SignupIn):
    hashed = ph.hash(user.password)          # hash first, outside the database block
    try:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (user.email, hashed),
            )
    except sqlite3.IntegrityError:           # the UNIQUE email rule was broken
        raise HTTPException(409, "Email already registered")
    return {"id": cur.lastrowid, "email": user.email}


@app.get("/notes")                          # READ (all)
def list_notes():
    with get_db() as db:
        return [to_dict(r) for r in db.execute("SELECT * FROM notes ORDER BY id DESC")]


@app.get("/notes/{note_id}")                # READ (one)
def get_note(note_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Note not found")
    return to_dict(row)


@app.put("/notes/{note_id}")                # UPDATE
def update_note(note_id: int, note: NoteIn):
    with get_db() as db:
        cur = db.execute(
            "UPDATE notes SET title = ?, body = ?, done = ? WHERE id = ?",
            (note.title, note.body, int(note.done), note_id),
        )
    if cur.rowcount == 0:
        raise HTTPException(404, "Note not found")
    return {"id": note_id, **note.model_dump()}


@app.delete("/notes/{note_id}", status_code=204)   # DELETE
def delete_note(note_id: int):
    with get_db() as db:
        cur = db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    if cur.rowcount == 0:
        raise HTTPException(404, "Note not found")


# --------------------------------------------------------------- PAGE

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Notes</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: system-ui, "Segoe UI", Arial, sans-serif;
         background: #f4f1ec; color: #1c2230; }
  main { max-width: 640px; margin: 0 auto; padding: 32px 16px 64px; }
  h1 { font-size: 30px; margin: 0 0 4px; letter-spacing: -0.5px; }
  .sub { color: #5b6474; margin: 0 0 24px; }
  form, .note { background: #fff; border: 1px solid #e3ded5; border-radius: 14px; padding: 16px; }
  form { display: grid; gap: 10px; margin-bottom: 24px; }
  input[type=text], textarea { width: 100%; font: inherit; padding: 10px 12px;
         border: 1px solid #cfc9bd; border-radius: 10px; background: #fff; }
  textarea { min-height: 70px; resize: vertical; }
  input:focus, textarea:focus { outline: 2px solid #0f6b5a; border-color: transparent; }
  button { font: inherit; cursor: pointer; border: 0; border-radius: 10px; padding: 10px 16px; }
  .submit { background: #0f6b5a; color: #fff; font-weight: 700; justify-self: start; }
  .submit:disabled { opacity: .6; cursor: default; }
  .note { display: grid; grid-template-columns: auto 1fr auto; gap: 12px; align-items: start;
          margin-bottom: 10px; }
  .note input[type=checkbox] { width: 20px; height: 20px; margin-top: 3px; accent-color: #0f6b5a; }
  .note h3 { margin: 0; font-size: 17px; }
  .note p { margin: 4px 0 0; color: #5b6474; white-space: pre-wrap; }
  .note.done h3 { text-decoration: line-through; color: #8a93a3; }
  .del { background: #f6e4e1; color: #a33a2c; padding: 6px 12px; font-size: 14px; }
  .msg { color: #a33a2c; min-height: 20px; margin: 0; }
  .empty { color: #8a93a3; text-align: center; padding: 24px 0; }
</style>
</head>
<body>
<main>
  <h1>Notes</h1>
  <p class="sub">Add a note, tick it when it is done.</p>
  
  <p class="sub" id="count"></p>
  
  <form id="form">
    <input type="text" id="title" placeholder="Title" required maxlength="120">
    <textarea id="body" placeholder="Details (optional)"></textarea>
    <button class="submit" id="submit" type="submit">Submit</button>
    <p class="msg" id="msg"></p>
  </form>

  <div id="list"></div>
</main>

<script>
  const form = document.getElementById("form");
  const titleEl = document.getElementById("title");
  const bodyEl = document.getElementById("body");
  const submitEl = document.getElementById("submit");
  const msgEl = document.getElementById("msg");
  const listEl = document.getElementById("list");
  const countEl = document.getElementById("count");

  function showError(text) { msgEl.textContent = text || ""; }

  // Ask the API for all notes and draw them.
  async function loadNotes() {
    const res = await fetch("/notes");
    const notes = await res.json();
    
  //adding counter for done notes
  const doneCount = notes.filter(n => n.done).length;
  countEl.textContent = `${doneCount} of ${notes.length} done`; 

    listEl.innerHTML = "";
    if (notes.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty";
      empty.textContent = "No notes yet. Add your first one above.";
      listEl.appendChild(empty);
      return;
    }
    for (const n of notes) listEl.appendChild(drawNote(n));
  }

  // Build one note card. textContent keeps user text safe (never run as HTML).
  function drawNote(n) {
    const card = document.createElement("div");
    card.className = "note" + (n.done ? " done" : "");

    const box = document.createElement("input");
    box.type = "checkbox";
    box.checked = n.done;
    box.setAttribute("aria-label", "Mark as done");
    box.addEventListener("change", () => toggleDone(n, box.checked));

    const text = document.createElement("div");
    const h = document.createElement("h3");
    h.textContent = n.title;
    text.appendChild(h);
    if (n.body) {
      const p = document.createElement("p");
      p.textContent = n.body;
      text.appendChild(p);
    }

    const del = document.createElement("button");
    del.className = "del";
    del.textContent = "Delete";
    del.addEventListener("click", () => removeNote(n.id));

    card.append(box, text, del);
    return card;
  }

  // The Submit button: send the form to the API as a new note.
  form.addEventListener("submit", async (event) => {
    event.preventDefault();            // stop the browser reloading the page
    showError("");
    submitEl.disabled = true;
    try {
      const res = await fetch("/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: titleEl.value.trim(), body: bodyEl.value.trim(), done: false }),
      });
      if (!res.ok) throw new Error("Could not save the note.");
      form.reset();
      titleEl.focus();
      await loadNotes();
    } catch (err) {
      showError(err.message);
    } finally {
      submitEl.disabled = false;
    }
  });

  async function toggleDone(n, done) {
    const res = await fetch("/notes/" + n.id, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: n.title, body: n.body, done: done }),
    });
    if (!res.ok) showError("Could not update the note.");
    await loadNotes();
  }

  async function removeNote(id) {
    const res = await fetch("/notes/" + id, { method: "DELETE" });
    if (!res.ok) showError("Could not delete the note.");
    await loadNotes();
  }

  loadNotes();
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE
