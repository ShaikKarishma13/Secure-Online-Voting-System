import sqlite3

from werkzeug.security import (
    generate_password_hash
)

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# =========================
# USERS TABLE
# =========================

cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE,

    password TEXT,

    role TEXT,

    has_voted INTEGER DEFAULT 0
)

""")

# =========================
# VOTES TABLE
# =========================

cursor.execute("""

CREATE TABLE IF NOT EXISTS votes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    voter_id TEXT,

    encrypted_vote TEXT,

    encrypted_key TEXT,

    vote_hash TEXT
)

""")

# =========================
# HASHED PASSWORDS
# =========================

admin_password = generate_password_hash(
    "Admin@123"
)

voter_password = generate_password_hash(
    "Vote@123"
)

# =========================
# ADMIN USER
# =========================

cursor.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES (?, ?, ?)

""", (
    'admin',
    admin_password,
    'admin'
))

# =========================
# VOTER 1
# =========================

cursor.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES (?, ?, ?)

""", (
    'voterone',
    voter_password,
    'voter'
))

# =========================
# VOTER 2
# =========================

cursor.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES (?, ?, ?)

""", (
    'votertwo',
    voter_password,
    'voter'
))

conn.commit()

conn.close()

print("Database created successfully")
