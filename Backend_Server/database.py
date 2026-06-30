import sqlite3
conn = sqlite3.connect('PhishGuard.db')
cursor = conn.cursor()
cursor.execute("ALTER TABLE users ADD COLUMN current_level INTEGER DEFAULT 1")
conn.commit()
conn.close()

def init_db():
    # Create database PhishGuard.db
    conn = sqlite3.connect('PhishGuard.db')
    cursor = conn.cursor()

    # 1.Store student information Table (Users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT,
            risk_score FLOAT DEFAULT 0.0
        )
    ''')

    # 2. Store Gamified Score Table (Scores)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            level_1_score INTEGER DEFAULT 0,
            level_2_score INTEGER DEFAULT 0,
            level_3_score INTEGER DEFAULT 0,
            total_xp INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 3. Behavioral Profiling data Table 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS behavior_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            missed_url_check INTEGER DEFAULT 0,
            fooled_by_urgency INTEGER DEFAULT 0,
            clicked_attachment INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')


    conn.commit()
    conn.close()
    print("Database and Tables created successfully!")

if __name__ == "__main__":
    init_db()