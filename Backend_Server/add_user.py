import sqlite3

def add_test_user():
    conn = sqlite3.connect('PhishGuard.db')
    cursor = conn.cursor()
    
    email = "test@kiu.ac.lk"
    password = "123"

    try:
        # 1. Inserting data into the users table
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        user_id = cursor.lastrowid  # The newly created user's ID is taken from here

        # 2. Creating the corresponding row in the scores table
        cursor.execute("INSERT INTO scores (user_id, total_xp) VALUES (?, 0)", (user_id,))

        # 3. Creating the corresponding row in the behavior_profile table
        cursor.execute("INSERT INTO behavior_profile (user_id, missed_url_check) VALUES (?, 0)", (user_id,))

        conn.commit()
        print(f"User, Score, and Profile for {email} created successfully!")
    except sqlite3.IntegrityError:
        print("User already exists.")
    except Exception as e:
        print(f"Error: {e}")
    
    conn.close()

if __name__ == "__main__":
    add_test_user()