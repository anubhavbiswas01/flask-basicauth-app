from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

DB_NAME = "messages.db"


def init_db():
    """Create database and table if not exists."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", success=None)


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    # Basic validation
    if not name or not email or not message:
        return render_template(
            "index.html",
            success="Please fill all the fields properly."
        )

    # Insert into SQLite database
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
            (name, email, message),
        )

    return render_template(
        "index.html",
        success="Thank you! Your message has been received."
    )


@app.route("/messages")
def view_messages():
    """Simple page to view all messages (for you only)."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, name, email, message, created_at FROM messages ORDER BY created_at DESC"
        ).fetchall()

    return render_template("messages.html", messages=rows)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
