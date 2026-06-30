import sqlite3

def clean_and_reset_questions():
    conn = sqlite3.connect('PhishGuard.db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS questions")
    
    cursor.execute('''
        CREATE TABLE questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            body TEXT,
            link TEXT,
            is_phishing INTEGER,
            category TEXT,
            difficulty INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Questions table reset successfully! 🚀")

if __name__ == "__main__":
    clean_and_reset_questions()