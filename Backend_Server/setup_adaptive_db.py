import sqlite3

def seed_all_levels():
    conn = sqlite3.connect('PhishGuard.db')
    cursor = conn.cursor()

    # delete all the old questions and set the correct questions for all 3 levels
    cursor.execute("DELETE FROM questions")

    questions_data = [
        # --- LEVEL 1: URL Check (difficulty = 1) ---
        ('security@kiu.lk', 'Login Notice', 'Please verify your KIU account.', 'http://fake-kiu-login.com', 1, 'URL_Check', 1),
        ('admin@kiu.ac.lk', 'Library Portal', 'Access online research papers.', 'https://library.kiu.ac.lk', 0, 'URL_Check', 1),
        ('it@kiu.lk', 'Password Reset', 'Click here to reset LMS password.', 'http://bit.ly/secure-reset-portal', 1, 'URL_Check', 1),
        ('student.affairs@kiu.ac.lk', 'Exam Timetable', 'Download final exam schedule.', 'https://kiu.ac.lk/exams', 0, 'URL_Check', 1),
        ('support@google-security.lk', 'Security Alert', 'Your Gmail was accessed from Russia.', 'http://login-google-account-fix.com', 1, 'URL_Check', 1),

        # --- LEVEL 2: Urgency Analysis (difficulty = 2) ---
        ('rector@kiu.lk', 'URGENT: Suspension Notice', 'Your student ID will be blocked in 2 hours!', 'http://kiu-appeal-verify.com', 1, 'Urgency_Check', 2),
        ('finance@kiu.ac.lk', 'Fee Payment Reminder', 'Please settle semester fees before Friday.', 'https://kiu.ac.lk/payments', 0, 'Urgency_Check', 2),
        ('helpdesk@kiu.lk', 'IMMEDIATE ACTION REQUIRED', 'Server maintenance: Update profile now or lose data!', 'http://kiu-server-update.net', 1, 'Urgency_Check', 2),
        ('scholarships@kiu.ac.lk', 'Interview Call', 'You are selected for the dean list interview tomorrow.', 'https://kiu.ac.lk/scholars', 0, 'Urgency_Check', 2),
        ('admin@lms-kiu.com', 'WARNING: Assignment Deleted', 'Your research proposal draft was flagged. Re-verify!', 'http://lms-recovery-portal.org', 1, 'Urgency_Check', 2),

        # --- LEVEL 3: Attachment & File Shield (difficulty = 3) ---
        ('ravishanka.silva@kiu.ac.lk', 'Research Feedback', 'Reviewed your proposal. Check attached comments.', 'http://kiu-staff-storage.com/feedback_draft.exe', 1, 'Attachment_Check', 3),
        ('supervisor@kiu.ac.lk', 'Thesis Guidelines', 'Please use the attached Word template for chapter 1.', 'https://kiu.ac.lk/downloads/thesis_template.docx', 0, 'Attachment_Check', 3),
        ('careers@top-bank.lk', 'Internship Offer', 'Congratulations! Download your offer letter slip.', 'http://top-bank-careers.io/offer_letter.pdf.scr', 1, 'Attachment_Check', 3),
        ('journal_editor@ieee.org', 'Paper Revision', 'See attached PDF for reviewer comments.', 'https://ieee.org/portal/reviews/paper_11472.pdf', 0, 'Attachment_Check', 3),
        ('exam_unit@kiu.lk', 'Admit Card Release', 'Print the attached e-admit card to enter the hall.', 'http://bad-hacker-server.com/admit_card.zip', 1, 'Attachment_Check', 3)
    ]

    cursor.executemany('''INSERT INTO questions (sender, subject, body, link, is_phishing, category, difficulty) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''', questions_data)
    conn.commit()
    conn.close()
    print(" Successful! 15 new questions were added to all 3 levels.")

if __name__ == '__main__':
    seed_all_levels()