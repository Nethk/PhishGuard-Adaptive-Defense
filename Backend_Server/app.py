from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, urllib.parse
from flask_cors import CORS
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            static_folder=os.path.join(current_dir, 'static'),
            static_url_path='/static')

app.secret_key = 'super_secret_cyber_key'

# 🚨 කුකීස් සහ ක්‍රොස්-සයිට් රිකුවෙස්ට් වලට ඉඩ දෙන රහස:
CORS(app, supports_credentials=True) 

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax', 
    SESSION_COOKIE_SECURE=False     
)

def get_db_connection():
    db_path = os.path.join(current_dir, 'PhishGuard.db')
    # timeout=10 means to wait 10 seconds if the database is locked
    conn = sqlite3.connect(db_path, timeout=10) 
    conn.row_factory = sqlite3.Row
    return conn

# 1. Home/Login Page
@app.route('/')
def index():
    return render_template('login.html')

# 2. Authentication (Login)
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email').strip()
    password = request.form.get('password').strip()
    
    db = get_db_connection()
    user = db.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
    db.close()

    if user:
        session['user_id'] = user['id']
        session['email'] = user['email']
        return redirect(url_for('dashboard'))
    else:
        return "Invalid login credentials. Please check your email and password!", 401
    
@app.route('/signup')
def signup():
    return render_template('signup.html')

# 3. Main Dashboard ( The current_level is now correctly displayed here
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if not user_id:
        return redirect(url_for('index'))

    db = get_db_connection()
    # missed_url_check / fooled_by_urgency
    user_data = db.execute('''
        SELECT u.username, u.avatar, u.risk_score, u.current_level, s.total_xp,
               bp.missed_url_check, bp.fooled_by_urgency
        FROM users u
        LEFT JOIN scores s ON u.id = s.user_id 
        LEFT JOIN behavior_profile bp ON u.id = bp.user_id
        WHERE u.id = ?
    ''', (user_id,)).fetchone()
    db.close()

    if user_data:
        curr_lvl = user_data['current_level'] if (user_data['current_level'] and user_data['current_level'] > 0) else 1
        
        r_score = user_data['risk_score'] if user_data['risk_score'] else 1.0
        r_pct = int(r_score * 100) 

        u_miss = user_data['missed_url_check'] if user_data['missed_url_check'] else 0
        urg_miss = user_data['fooled_by_urgency'] if user_data['fooled_by_urgency'] else 0

        return render_template('dashboard.html', 
                               email=session.get('email'),
                               username=user_data['username'], 
                               avatar=user_data['avatar'].lower() if user_data['avatar'] else 'ghost', 
                               risk_score=r_score,
                               risk_pct=r_pct,
                               level=curr_lvl, 
                               xp=user_data['total_xp'] if user_data['total_xp'] else 0,
                               url_miss=u_miss, urg_miss=urg_miss) # <--- වැරදි ටික යැව්වා
    return redirect(url_for('index'))

# 4. Registration
@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    username = request.form.get('username') # 🚨 අලුතින් ගත්තා
    avatar = request.form.get('avatar', 'guardian')
    
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute('INSERT INTO users (email, password, username, avatar, risk_score, current_level) VALUES (?, ?, ?, ?, ?, ?)', 
                       (email, password, username, avatar, 60, 1))
        user_id = cursor.lastrowid
        
        cursor.execute('INSERT INTO scores (user_id, total_xp) VALUES (?, 0)', (user_id,))
        cursor.execute('INSERT INTO behavior_profile (user_id, missed_url_check, fooled_by_urgency) VALUES (?, 0, 0)', (user_id,))
        
        db.commit()
        session['user_id'] = user_id
        session['email'] = email
        return redirect(url_for('dashboard'))
    except sqlite3.IntegrityError:
        return "Email already exists!", 400
    finally:
        db.close()


#ADAPTIVE MISSION ENGINE (LEVEL LOCK)


@app.route('/start_mission')
@app.route('/start_mission/<int:level>')
def start_mission(level=1):
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('index'))

    db = get_db_connection()
    user = db.execute('SELECT current_level FROM users WHERE id = ?', (user_id,)).fetchone()
    user_max_lvl = user['current_level'] if (user and user['current_level']) else 1

    if level > user_max_lvl:
        db.close()
        return "Level Locked! Please complete previous levels first.", 403

    # Only 5 questions of the exact same level (difficulty = 1, 2, or 3) are selected
    questions = db.execute('SELECT * FROM questions WHERE difficulty = ? ORDER BY RANDOM() LIMIT 5', (level,)).fetchall()
    
    db.close()

    if not questions:
        return f"Level {level} සඳහා ප්‍රශ්න Database එකේ නැත! python setup_adaptive_db.py run කරන්න.", 404

    session['mission_questions'] = [dict(q) for q in questions]
    session['current_q_index'] = 0 
    session['playing_level'] = level 
    return redirect(url_for('level1'))

@app.route('/level1', methods=['GET', 'POST'])
def level1():
    questions = session.get('mission_questions')
    try:
        index = int(session.get('current_q_index', 0))
    except (ValueError, TypeError):
        index = 0

    if questions and index < len(questions):
        current_q = questions[index] 
        return render_template('level1.html', 
                               question=current_q, 
                               current_num=index + 1, 
                               total_num=len(questions))
    else:
        # finish level 3, you will be sent directly to the Victory page
        played_lvl = session.get('playing_level', 1)
        if played_lvl == 3:
            return redirect(url_for('victory'))
            
        return redirect(url_for('dashboard'))

@app.route('/check_level1', methods=['POST'])
def check_level1():
    user_answer = request.form.get('answer')
    user_id = session.get('user_id') 
    
    if not user_id: return redirect(url_for('index'))

    questions = session.get('mission_questions', [])
    index = session.get('current_q_index', 0)
    played_lvl = session.get('playing_level', 1) 

    if not questions or index >= len(questions):
        return redirect(url_for('dashboard'))

    current_q = questions[index]
    correct_val = "phishing" if current_q['is_phishing'] == 1 else "safe"

    db = get_db_connection()
    
    if user_answer == correct_val:
        score_column = f"level_{played_lvl}_score" if played_lvl in [1, 2, 3] else "level_1_score"
        
        # 1. Gives +10 to XP in the game
        db.execute(f'UPDATE scores SET {score_column} = {score_column} + 10, total_xp = total_xp + 10 WHERE user_id = ?', (user_id,))
        
        # 2. Browser score (risk_score) is given +10! (Limited to maximum 60)
        db.execute('UPDATE users SET risk_score = MIN(60, risk_score + 10) WHERE id = ?', (user_id,))
        
        msg = "Excellent! Correct Identification! +10 XP"
        color = "#4CAF50"
        emoji = "🛡️"
    else:
        # give an incorrect answer, 5 points will be deducted from the browser score (minimum value 0)
        db.execute('UPDATE users SET risk_score = MAX(0, risk_score - 5) WHERE id = ?', (user_id,))
        
        if current_q['is_phishing'] == 1:
            db.execute('UPDATE behavior_profile SET missed_url_check = missed_url_check + 1 WHERE user_id = ?', (user_id,))
            if "URGENT" in current_q['subject'].upper():
                db.execute('UPDATE behavior_profile SET fooled_by_urgency = fooled_by_urgency + 1 WHERE user_id = ?', (user_id,))

        msg = "Oops! That was a Phishing threat. Your vulnerability profile was updated."
        color = "#e94560"
        emoji = "🚨"

    # Level Unlock
    if (index + 1) >= len(questions):
        user_row = db.execute('SELECT current_level FROM users WHERE id = ?', (user_id,)).fetchone()
        curr = user_row['current_level'] if (user_row and user_row['current_level']) else 1
        
        if played_lvl == curr and played_lvl < 3:
            db.execute('UPDATE users SET current_level = current_level + 1 WHERE id = ?', (user_id,))

    db.commit()
    db.close()

    session['current_q_index'] = index + 1
    return render_template('result.html', message=msg, color=color, emoji=emoji, next_url="/level1")

@app.route('/leaderboard')
def leaderboard():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('index'))

    db = get_db_connection()
    top_players = db.execute('''
        SELECT u.email, s.total_xp, u.avatar 
        FROM users u 
        JOIN scores s ON u.id = s.user_id 
        ORDER BY s.total_xp DESC LIMIT 5
    ''').fetchall()
    db.close()

    return render_template('leaderboard.html', players=top_players)

@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('index'))  

@app.route('/victory')
def victory():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('index'))

    db = get_db_connection()
    
    #  ast game was won, the browser score is back to the maximum of 60!
    db.execute('UPDATE users SET risk_score = 60 WHERE id = ?', (user_id,))
    db.commit() 

    user_data = db.execute('''
        SELECT s.total_xp, u.risk_score, bp.missed_url_check, bp.fooled_by_urgency 
        FROM scores s
        JOIN users u ON s.user_id = u.id
        JOIN behavior_profile bp ON u.id = bp.user_id
        WHERE s.user_id = ?
    ''', (user_id,)).fetchone()
    db.close()

    total_xp = user_data['total_xp'] if user_data else 0
    risk_score = user_data['risk_score'] if user_data else 60
    url_miss = user_data['missed_url_check'] if user_data else 0
    urg_miss = user_data['fooled_by_urgency'] if user_data else 0

    return render_template('victory.html', email=session.get('email'), xp=total_xp, 
                           risk=risk_score, url_miss=url_miss, urg_miss=urg_miss)

@app.route('/reset_progress')
def reset_progress():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('index'))

    db = get_db_connection()
    # points and progress 0
    db.execute('UPDATE scores SET total_xp = 0, level_1_score = 0, level_2_score = 0, level_3_score = 0 WHERE user_id = ?', (user_id,))
    db.execute('UPDATE users SET current_level = 1, risk_score = 1.0 WHERE id = ?', (user_id,))
    db.execute('UPDATE behavior_profile SET missed_url_check = 0, fooled_by_urgency = 0 WHERE user_id = ?', (user_id,))
    
    db.commit()
    db.close()
    return redirect(url_for('dashboard'))


@app.route('/api/inspect_url', methods=['GET'])
def inspect_url():
    target_url = request.args.get('url', '')
    user_id = request.args.get('user_id')

    if not target_url:
        return jsonify({"status": "error", "message": "No URL provided"})

    # 1. List of trusted and safe websites(White-list) 
    safe_domains = ['google.com', 'youtube.com', 'facebook.com', 'linkedin.com', 'github.com', 'stackoverflow.com', '127.0.0.1', 'localhost']
    
    parsed = urllib.parse.urlparse(target_url)
    domain = parsed.netloc.lower()

    for safe_site in safe_domains:
        if safe_site in domain:
            return jsonify({"is_suspicious": False, "risk_level": "SAFE"})

    # 2. Key suspicious words in phishing links (Keywords)
    phishing_keywords = ['login', 'verify', 'update', 'secure', 'bank', 'account', 'bonus', 'free', 'confirm', 'signin', 'gift']
    
    risk_points = 0
    detected_reasons = []

    # Test A: Are there any suspicious words in the URL?

    for kw in phishing_keywords:
        if kw in target_url.lower():
            risk_points += 1
            detected_reasons.append(f"Suspicious keyword found: '{kw}'")

    # Test B: Is the URL much longer than usual? (> 75 chars)
    if len(target_url) > 75:
        risk_points += 1
        detected_reasons.append("URL length is abnormally long")

    # Test C: Is there a dash (-) in the domain? (Example: paypal-secure-login.com)
    if '-' in domain:
        risk_points += 1
        detected_reasons.append("Domain contains hyphens (Typosquatting pattern)")

    # Test D: Is it just 'http'? (No SSL Security)
    if parsed.scheme == 'http' and '127.0.0.1' not in domain:
        risk_points += 1
        detected_reasons.append("Insecure HTTP connection")

    # Decision: If 2 or more risk points are reached, this is considered a 'Phishing Attack'!
    if risk_points >= 2:
        db = get_db_connection()
        # (total_xp) 
        s_row = db.execute("SELECT total_xp FROM scores WHERE user_id=?", (user_id,)).fetchone()
        db.close()
        
        user_game_xp = int(s_row['total_xp']) if (s_row and s_row['total_xp']) else 0

        # If the game's XP is less than 40, a very strict "CRITICAL_PHISHING_STRICT" warning will be issued!
        warning_severity = "CRITICAL_PHISHING_STRICT" if user_game_xp < 40 else "CRITICAL_PHISHING"

        return jsonify({
            "is_suspicious": True,
            "risk_level": warning_severity,
            "game_xp": user_game_xp,
            "reasons": detected_reasons
        })
    else:
        return jsonify({
            "is_suspicious": False,
            "risk_level": "NORMAL"
        })
    
@app.route('/api/handle_adaptive_interception', methods=['POST'])
def handle_adaptive_interception():
    data = request.json
    u_id = data.get('user_id')
    action = data.get('action') # 'PROCEED' or 'GO_BACK'
    
    db = get_db_connection()
    
    # 1. Took 'risk_score' (browser score) from the correct table
    user_row = db.execute("SELECT risk_score FROM users WHERE id=?", (u_id,)).fetchone()
    current_score = int(user_row['risk_score']) if (user_row and user_row['risk_score'] > 1.0) else 60

    if action == 'PROCEED':
        # Deduction of 15 points
        new_score = current_score - 15
        
        # The correct column (risk_score) was updated.
        db.execute("UPDATE users SET risk_score=? WHERE id=?", (new_score, u_id))
        db.commit() 
        
        # Lockdown if score is 30 or less
        if new_score <= 30:
            db.close()
            return jsonify({
                "status": "LOCKED",
                "current_score": new_score,
                "msg": "⚠️ Your Real-World Score is below 30! This is due to normal browsing. Please complete the PhishGuard Training and come back."
            })
            
        db.close()
        return jsonify({"status": "DEDUCTED", "current_score": new_score})

    elif action == 'GO_BACK':
        db.close()
        return jsonify({"status": "SAFE", "current_score": current_score})
        
@app.route('/api/get_adaptive_status', methods=['GET'])
def get_adaptive_status():
    u_id = request.args.get('user_id')
    db = get_db_connection()
    
    # Pulls both the user's browser score (risk_score) and the game's XP (total_xp)
    user_data = db.execute('''
        SELECT u.risk_score, s.total_xp 
        FROM users u
        LEFT JOIN scores s ON u.id = s.user_id
        WHERE u.id = ?
    ''', (u_id,)).fetchone()
    db.close()

    if user_data:
        b_score = int(user_data['risk_score']) if (user_data['risk_score'] and user_data['risk_score'] > 1.0) else 60
        game_xp = int(user_data['total_xp']) if user_data['total_xp'] else 0

        # ---------------------------------------------------------
        #Rule A: If the browser score is below 30, show it first (LOCKDOWN)
        # ---------------------------------------------------------
        if b_score <= 30:
            return jsonify({"color": "#e94560", "message": f"🚨 LOCKED! (Score: {b_score})"})

        # ---------------------------------------------------------
        # Rule B: If the browser is not locked, the color is determined by game XP!
        # ---------------------------------------------------------
        # 1. haven't played the game yet (Neutral)
        if game_xp == 0:
            return jsonify({"color": "#feca57", "message": f"⚠️ Score: {b_score} (Game Pending)"})
        
        # 2. If the game score is very low (e.g. less than 40 XP) -> RED!
        elif game_xp < 40:
            return jsonify({"color": "#ff4757", "message": f"🚨 HIGH RISK! (Score: {b_score})"})

        # 3. If the game score is moderate (between 40 and 80 XP) -> ORANGE!
        elif game_xp < 80:
            return jsonify({"color": "#ffa502", "message": f"⚠️ CAUTION (Score: {b_score})"})

        # 4. played the game perfectly and scored more than 80 points -> GREEN!
        else:
            return jsonify({"color": "#2ed573", "message": f"🛡️ SECURE (Score: {b_score})"})
    
    return jsonify({"color": "#2ed573", "message": f"🛡️ SECURE (Score: 60)"})


@app.route('/api/inspect_email', methods=['POST'])
def inspect_email():
    data = request.json
    body = data.get('body', '')
    sender = data.get('sender', '')
    
    # 
    score = 0
    if "urgent" in body.lower(): score += 2
    if "login" in body.lower(): score += 2
    
    is_phishing = score >= 3
    return jsonify({"is_phishing": is_phishing, "reasons": ["Urgent language detected", "Suspicious link structure"]})

# API Endpoint that sends the User ID to the extension
@app.route('/api/get_current_user', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        return jsonify({"status": "success", "user_id": session['user_id']})
    else:
        return jsonify({"status": "error", "user_id": None}), 401

@app.route('/api/restore_score', methods=['POST'])
def restore_score():
    data = request.json
    u_id = data.get('user_id')
    
    db = get_db_connection()
    # Reset points to default 60
    db.execute("UPDATE users SET risk_score = 60 WHERE id=?", (u_id,))
    db.commit()
    db.close()
    
    return jsonify({"status": "UNLOCKED", "msg": "Score successfully restored to 60!"})

if __name__ == '__main__':
    app.run(debug=True)