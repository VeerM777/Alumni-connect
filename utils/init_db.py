import sqlite3

def init_db():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    # Alumni table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            batch TEXT,
            branch TEXT,
            phone TEXT,
            linkedin TEXT,
            job_title TEXT,
            company TEXT
        )
    ''')
    # Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            date TEXT,
            time TEXT,
            location TEXT
        )
    ''')
    # Invitations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumni_id INTEGER,
            event_id INTEGER,
            FOREIGN KEY(alumni_id) REFERENCES alumni(id),
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    ''')
    # Mentorship requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mentorship_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mentor_id INTEGER,
            student_name TEXT,
            message TEXT,
            FOREIGN KEY(mentor_id) REFERENCES alumni(id)
        )
    ''')
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            role TEXT CHECK(role IN ('student', 'teacher'))
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()