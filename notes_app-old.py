"""Lesson 1: a FastAPI app with a real database (SQLite).

Run:  uvicorn notes_app:app --reload
Open: http://127.0.0.1:8000/docs   (FastAPI builds a test page for you)
"""
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_FILE = "notes.db"          # created automatically next to this file

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
                   done BOOLEAN NOT NULL DEFAULT 0
               )"""
        )


setup()


class NoteIn(BaseModel):
    """The shape of data we accept from the browser."""
    title: str
    body: str = ""
    done: bool = False


@app.post("/notes", status_code=201)       # CREATE
def add_note(note: NoteIn):
    with get_db() as db:
        cur = db.execute("INSERT INTO notes (title, body, done) VALUES (?, ?, ?)", (note.title, note.body, int(note.done)))
        return {"id": cur.lastrowid, **note.model_dump()}


@app.get("/notes")                          # READ (all)
def list_notes():
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM notes ORDER BY id DESC")]


@app.get("/notes/{note_id}")                # READ (one)
def get_note(note_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Note not found")
    return dict(row)


@app.put("/notes/{note_id}")                # UPDATE
def update_note(note_id: int, note: NoteIn):
    with get_db() as db:
        cur = db.execute("UPDATE notes SET title = ?, body = ?, done = ? WHERE id = ?", (note.title, note.body, int(note.done), note_id))
    if cur.rowcount == 0:
        raise HTTPException(404, "Note not found")
    return {"id": note_id, **note.model_dump()}


@app.delete("/notes/{note_id}", status_code=204)   # DELETE
def delete_note(note_id: int):
    with get_db() as db:
        cur = db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    if cur.rowcount == 0:
        raise HTTPException(404, "Note not found")
