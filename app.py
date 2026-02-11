"""Flask API and web UI for ticket listing dashboard."""
import sqlite3
from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = "tickets.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/matches", methods=["GET"])
def list_matches():
    """Return distinct match names from the database."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT match_name FROM seen_tickets ORDER BY match_name")
    rows = cur.fetchall()
    conn.close()
    return jsonify([r["match_name"] for r in rows])


@app.route("/api/matches/<path:match_name>/tickets", methods=["GET"])
def get_tickets(match_name):
    """Return tickets for a match: first_seen, price, quantity, section, row."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT first_seen, price, quantity, section, row
        FROM seen_tickets
        WHERE match_name = ?
        ORDER BY first_seen
    """,
        (match_name,),
    )
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
