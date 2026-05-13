import sqlite3

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
# DEFAULT USERS
# =========================
cursor.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES
('admin', 'admin123', 'admin')

""")

cursor.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES
('voter1', 'vote123', 'voter')

""")

cursor.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES
('voter2', 'vote123', 'voter')

""")

conn.commit()

conn.close()

print("Database created successfully")
