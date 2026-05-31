from flask import Flask, render_template, request, redirect
import os
from datetime import datetime

app = Flask(__name__)

# ── Database setup ────────────────────────────────────────────────────────────
# On Render: DATABASE_URL env var is set → uses PostgreSQL
# Locally:   no env var → uses SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    import psycopg2
    # Render gives "postgres://" but psycopg2 needs "postgresql://"
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    USE_PG = True
else:
    import sqlite3
    DB_PATH = 'submissions.db'
    USE_PG = False


def get_conn():
    if USE_PG:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    if USE_PG:
        c.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id   SERIAL PRIMARY KEY,
                type TEXT,
                link TEXT,
                author TEXT,
                created_at TEXT
            )
        """)
    else:
        c.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                link TEXT,
                author TEXT,
                created_at TEXT
            )
        """)
    conn.commit()
    conn.close()


init_db()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM submissions ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return render_template('index.html', rows=rows)


@app.route('/submit', methods=['POST'])
def submit():
    type_      = request.form['type']
    link       = request.form['link'].strip()
    author     = request.form['author'].strip()
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_conn()
    c = conn.cursor()
    ph = '%s' if USE_PG else '?'   # placeholder differs between PG and SQLite
    c.execute(f"""
        INSERT INTO submissions (type, link, author, created_at)
        VALUES ({ph}, {ph}, {ph}, {ph})
    """, (type_, link, author, created_at))
    conn.commit()
    conn.close()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=False)
