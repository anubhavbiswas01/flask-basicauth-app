from flask import Flask, render_template, request
import sqlite3
import os
from flask_basicauth import BasicAuth

app = Flask(__name__)

DB_NAME = "messages.db"

# ---------- Basic Auth ----------
app.config['BASIC_AUTH_USERNAME'] = os.getenv("BASIC_AUTH_USERNAME")
app.config['BASIC_AUTH_PASSWORD'] = os.getenv("BASIC_AUTH_PASSWORD")
app.config['BASIC_AUTH_FORCE'] = False

basic_auth = BasicAuth(app)


# ---------- DB INIT ----------
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


# ---------- ROUTES ----------
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", success=None)


@app.route("/contact", methods=["POST"])
def contact():
    """Handle contact form submissions and save to DB."""
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    if not name or not email or not message:
        return render_template(
            "index.html",
            success="Please fill all fields"
        )

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
            (name, email, message)
        )

    print("New message:", name, email, message)  # appears in Render logs

    return render_template(
        "index.html",
        success="Thank you! Your message has been received."
    )


# ---------- ADMIN INBOX ----------
@app.route("/admin/messages")
@basic_auth.required
def admin_messages():
    """Admin-only inbox to view all contact form messages."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, name, email, message, created_at FROM messages ORDER BY created_at DESC"
        ).fetchall()

    return render_template("messages.html", messages=rows)


# ---------- RUN ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
