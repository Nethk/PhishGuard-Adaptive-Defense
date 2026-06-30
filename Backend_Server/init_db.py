import sqlite3

def force_init():
    connection = None
    try:
        # timeout 
        connection = sqlite3.connect('PhishGuard.db', timeout=20)
        cursor = connection.cursor()

        sample_questions = [
            ('university-support@gmail.com', '🚨 URGENT: LMS Verification', 'Verify your account in 2 hours.', 'http://kiu-lms-verify.xyz/login', 1),
            ('library@kiu.ac.lk', 'Book Overdue', 'Please return the book by Friday.', 'https://library.kiu.ac.lk/portal', 0),
            ('admin@kiu-portal.net', 'Scholarship 2026', 'Apply for the new scholarship.', 'http://kiu-scholarship-apply.net/form', 1)
        ]

        cursor.executemany('INSERT INTO questions (sender, subject, body, link, is_phishing) VALUES (?, ?, ?, ?, ?)', sample_questions)
        connection.commit()
        print("Sample questions added successfully! 🚀")

    except sqlite3.OperationalError as e:
        print(f"Still locked: {e}. Try restarting your computer if this continues.")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    force_init()