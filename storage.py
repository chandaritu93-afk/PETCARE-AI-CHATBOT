import sqlite3

# ------------------- INIT DB -------------------
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        session_id TEXT,
        role TEXT,
        message TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        user_id TEXT,
        session_id TEXT PRIMARY KEY,
        title TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS pet_profile (
        user_id TEXT PRIMARY KEY,
        pet_name TEXT,
        species TEXT,
        breed TEXT,
        age_months INTEGER,
        weight_kg REAL,
        gender TEXT
    )
    """)

    conn.commit()
    conn.close()


# ------------------- CHAT -------------------
def save_message(user_id, role, message, session_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO chats (user_id, session_id, role, message) VALUES (?, ?, ?, ?)",
        (user_id, session_id, role, message)
    )

    conn.commit()
    conn.close()


def load_messages(user_id, session_id, limit=50):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
    SELECT role, message FROM chats
    WHERE user_id=? AND session_id=?
    ORDER BY id ASC LIMIT ?
    """, (user_id, session_id, limit))

    rows = c.fetchall()
    conn.close()

    return [{"role": r[0], "content": r[1]} for r in rows]


# ------------------- SESSION -------------------
def create_session(user_id, session_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute(
        "INSERT OR IGNORE INTO sessions (user_id, session_id, title) VALUES (?, ?, ?)",
        (user_id, session_id, "New Chat")
    )

    conn.commit()
    conn.close()


def get_all_sessions(user_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute(
        "SELECT session_id, title FROM sessions WHERE user_id=? ORDER BY rowid DESC",
        (user_id,)
    )

    rows = c.fetchall()
    conn.close()

    return [{"session_id": r[0], "title": r[1]} for r in rows]


def delete_session(session_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("DELETE FROM sessions WHERE session_id=?", (session_id,))
    c.execute("DELETE FROM chats WHERE session_id=?", (session_id,))

    conn.commit()
    conn.close()


def update_session_title(user_id, session_id, title):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    # पहले current title check करो
    c.execute(
        "SELECT title FROM sessions WHERE session_id=? AND user_id=?",
        (session_id, user_id)
    )
    row = c.fetchone()

    # अगर title अभी भी "New Chat" है तभी update करो
    if row and row[0] == "New Chat":
        c.execute(
            "UPDATE sessions SET title=? WHERE session_id=? AND user_id=?",
            (title, session_id, user_id)
        )

    conn.commit()
    conn.close()

# ------------------- PET PROFILE -------------------
def save_pet_profile(user_id, data):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
    INSERT OR REPLACE INTO pet_profile 
    (user_id, pet_name, species, breed, age_months, weight_kg, gender)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data.get("pet_name"),
        data.get("species"),
        data.get("breed"),
        data.get("age_months"),
        data.get("weight_kg"),
        data.get("gender")
    ))

    conn.commit()
    conn.close()


def load_pet_profile(user_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("SELECT * FROM pet_profile WHERE user_id=?", (user_id,))
    row = c.fetchone()

    conn.close()

    if row:
        return {
            "user_id": row[0],
            "pet_name": row[1],
            "species": row[2],
            "breed": row[3],
            "age_months": row[4],
            "weight_kg": row[5],
            "gender": row[6],
        }
    return None