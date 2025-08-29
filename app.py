from flask import Flask, request, jsonify
import os, sqlite3
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "revenue.db")

app = Flask(__name__, static_folder="static", static_url_path="/")

# ---------------- DB helpers ----------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Create database file and table if not exists
    conn = get_conn()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS revenues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                revenue_id TEXT NOT NULL UNIQUE,
                date TEXT NOT NULL,           -- ISO YYYY-MM-DD
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)
    conn.close()

# --------------- Serve UI -------------------
@app.route("/")
def index():
    return app.send_static_file("index.html")

# --------------- API ------------------------
@app.route("/api/revenues", methods=["GET"])
def list_revenues():
    conn = get_conn()
    with conn:
        rows = conn.execute("SELECT * FROM revenues ORDER BY date DESC, id DESC").fetchall()
        data = [dict(r) for r in rows]
    return jsonify(data), 200

@app.route("/api/revenues", methods=["POST"])
def create_revenue():
    data = request.get_json(force=True)
    required = ["revenue_id", "date", "source", "amount", "category"]
    for k in required:
        if k not in data or data[k] in ("", None):
            return jsonify({"error": f"Missing field: {k}"}), 400

    # validate
    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
        amt = float(data["amount"])
    except Exception:
        return jsonify({"error": "Invalid date or amount format"}), 400

    conn = get_conn()
    try:
        with conn:
            conn.execute(
                """INSERT INTO revenues (revenue_id, date, source, amount, category)
                   VALUES (?,?,?,?,?)""",
                (data["revenue_id"], data["date"], data["source"], amt, data["category"])
            )
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "revenue_id must be unique"}), 409
    finally:
        conn.close()
    return jsonify({"message": "Created"}), 201

@app.route("/api/revenues/<int:item_id>", methods=["PUT"])
def update_revenue(item_id):
    data = request.get_json(force=True)
    fields = ["revenue_id", "date", "source", "amount", "category"]
    if not all(k in data for k in fields):
        return jsonify({"error": f"Expecting all fields: {fields}"}), 400
    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
        amt = float(data["amount"])
    except Exception:
        return jsonify({"error": "Invalid date or amount format"}), 400

    conn = get_conn()
    with conn:
        cur = conn.execute(
            """UPDATE revenues
               SET revenue_id=?, date=?, source=?, amount=?, category=?
               WHERE id=?""",
            (data["revenue_id"], data["date"], data["source"], amt, data["category"], item_id)
        )
        updated = cur.rowcount
    conn.close()
    if updated == 0:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"message": "Updated"}), 200

@app.route("/api/revenues/<int:item_id>", methods=["DELETE"])
def delete_revenue(item_id):
    conn = get_conn()
    with conn:
        cur = conn.execute("DELETE FROM revenues WHERE id=?", (item_id,))
        deleted = cur.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"message": "Deleted"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)

@app.route("/")
def home():
    return "Welcome to RevUp Revenue CRUD App"
