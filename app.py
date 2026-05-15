from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    send_file
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import sqlite3
import json
import base64
import re
import io
from datetime import datetime

from crypto.aes_utils import (
    generate_aes_key,
    encrypt_vote,
    decrypt_vote
)

from crypto.rsa_utils import (
    generate_rsa_keys,
    encrypt_aes_key,
    decrypt_aes_key,
    save_keys,
    load_keys
)

from crypto.hash_utils import (
    generate_hash,
    verify_hash
)


app = Flask(__name__)

app.secret_key = "super_secure_secret_key"


# =========================
# RSA KEYS
# =========================

import os


# =========================
# LOAD OR CREATE RSA KEYS
# =========================

if not os.path.exists(
    "keys/admin_private.pem"
):

    admin_private_key, admin_public_key = (
        generate_rsa_keys()
    )

    save_keys(
        admin_private_key,
        admin_public_key
    )

else:

    admin_private_key, admin_public_key = (
        load_keys()
    )





# =========================
# VALIDATION
# =========================

def validate_username(username):

    username_regex = r'^[A-Za-z]{3,}$'

    return re.match(
        username_regex,
        username
    )


def validate_password(password):

    password_regex = (
        r'^(?=.*[a-z])'
        r'(?=.*[A-Z])'
        r'(?=.*\d)'
        r'(?=.*[@$!%*?&])'
        r'[A-Za-z\d@$!%*?&]{8,}$'
    )

    return re.match(
        password_regex,
        password
    )


# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():

    return render_template(
        'login.html'
    )


# =========================
# LOGIN
# =========================

@app.route('/login', methods=['POST'])
def login():

    username = (
        request.form['username']
        .strip()
    )

    password = (
        request.form['password']
    )

    # =====================
    # VALIDATION
    # =====================

    if not validate_username(username):

        return render_template(
            'login.html',
            error=(
                "Username must contain "
                "only letters and "
                "minimum 3 characters."
            )
        )

    if not validate_password(password):

        return render_template(
            'login.html',
            error=(
                "Password must contain "
                "uppercase, lowercase, "
                "number and special character."
            )
        )

    conn = sqlite3.connect(
        'database.db'
    )

    cursor = conn.cursor()

    # =====================
    # CHECK USER
    # =====================

    cursor.execute("""

    SELECT * FROM users
    WHERE username = ?

    """, (username,))

    user = cursor.fetchone()

    # =====================
    # NEW USER
    # =====================

    if not user:

        role = 'voter'

        if username.lower() == 'admin':

            role = 'admin'

        # HASH PASSWORD
        hashed_password = (
            generate_password_hash(
                password
            )
        )

        cursor.execute("""

        INSERT INTO users (
            username,
            password,
            role,
            has_voted
        )

        VALUES (?, ?, ?, ?)

        """, (
            username,
            hashed_password,
            role,
            0
        ))

        conn.commit()

        cursor.execute("""

        SELECT * FROM users
        WHERE username = ?

        """, (username,))

        user = cursor.fetchone()

    # =====================
    # EXISTING USER
    # =====================

    else:

        stored_password = user[2]

        # CHECK HASHED PASSWORD
        password_correct = (
            check_password_hash(
                stored_password,
                password
            )
        )

        if not password_correct:

            conn.close()

            return render_template(
                'login.html',
                error="Incorrect password."
            )

    conn.close()

    # =====================
    # SESSION
    # =====================

    session['username'] = user[1]

    session['role'] = user[3]

    session['has_voted'] = user[4]

    # =====================
    # ADMIN LOGIN
    # =====================

    if user[3] == 'admin':

        return redirect('/admin')

    # =====================
    # VOTER LOGIN
    # =====================

    return redirect('/vote')


# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


# =========================
# VOTE PAGE
# =========================

@app.route('/vote', methods=['GET', 'POST'])
def vote():

    # MUST LOGIN
    if 'username' not in session:

        return redirect('/')

    # ADMIN CANNOT VOTE
    if session['role'] != 'voter':

        return redirect('/admin')

    # ONE VOTE ONLY
    if session['has_voted'] == 1:

        return render_template(
            'dashboard.html',
            message="You have already voted."
        )

    if request.method == 'POST':

        voter_id = (
            session['username']
        )

        selected_candidate = (
            request.form['candidate']
        )

        # =====================
        # AES KEY
        # =====================

        aes_key = generate_aes_key()

        # =====================
        # ENCRYPT VOTE
        # =====================

        encrypted_vote = encrypt_vote(
            selected_candidate,
            aes_key
        )

        encrypted_vote_json = (
            json.dumps(
                encrypted_vote
            )
        )

        # =====================
        # ENCRYPT AES KEY
        # =====================

        encrypted_key = encrypt_aes_key(
            aes_key,
            admin_public_key
        )

        encrypted_key_b64 = (
            base64.b64encode(
                encrypted_key
            ).decode()
        )

        # =====================
        # HASH
        # =====================

        vote_hash = generate_hash(
            encrypted_vote_json
        )

        # =====================
        # DATABASE
        # =====================

        conn = sqlite3.connect(
            'database.db'
        )

        cursor = conn.cursor()

        cursor.execute("""

        INSERT INTO votes (
            voter_id,
            encrypted_vote,
            encrypted_key,
            vote_hash
        )

        VALUES (?, ?, ?, ?)

        """, (
            voter_id,
            encrypted_vote_json,
            encrypted_key_b64,
            vote_hash
        ))

        # =====================
        # UPDATE USER
        # =====================

        cursor.execute("""

        UPDATE users
        SET has_voted = 1
        WHERE username = ?

        """, (voter_id,))

        conn.commit()

        conn.close()

        session['has_voted'] = 1

        return render_template(
            'dashboard.html',
            encrypted_vote=encrypted_vote_json,
            vote_hash=vote_hash
        )

    return render_template(
        'vote.html'
    )


# =========================
# ADMIN PANEL
# =========================

@app.route('/admin')
def admin():

    # MUST LOGIN
    if 'username' not in session:

        return redirect('/')

    # ONLY ADMIN
    if session['role'] != 'admin':

        return redirect('/vote')

    conn = sqlite3.connect(
        'database.db'
    )

    cursor = conn.cursor()

    # =====================
    # TOTAL USERS
    # =====================

    cursor.execute("""

    SELECT COUNT(*)
    FROM users
    WHERE role = 'voter'

    """)

    total_voters = cursor.fetchone()[0]

    # =====================
    # TOTAL VOTES
    # =====================

    cursor.execute("""

    SELECT COUNT(*)
    FROM votes

    """)

    total_votes = cursor.fetchone()[0]

    # =====================
    # GET ALL VOTES
    # =====================

    cursor.execute(
        "SELECT * FROM votes"
    )

    votes = cursor.fetchall()

    conn.close()

    decrypted_votes = []

    # =====================
    # DECRYPT VOTES
    # =====================

    for vote in votes:

        encrypted_vote_json = (
            vote[2]
        )

        encrypted_key_b64 = (
            vote[3]
        )

        stored_hash = (
            vote[4]
        )

        # VERIFY HASH
        if verify_hash(
            encrypted_vote_json,
            stored_hash
        ):

            encrypted_key = (
                base64.b64decode(
                    encrypted_key_b64
                )
            )

            aes_key = decrypt_aes_key(
                encrypted_key,
                admin_private_key
            )

            encrypted_vote = (
                json.loads(
                    encrypted_vote_json
                )
            )

            decrypted_vote = decrypt_vote(
                encrypted_vote,
                aes_key
            )

            decrypted_votes.append(
                decrypted_vote
            )

    # =====================
    # COUNT RESULTS
    # =====================

    results = {}

    for candidate in decrypted_votes:

        results[candidate] = (
            results.get(candidate, 0) + 1
        )

    # =====================
    # SORT RANKINGS
    # =====================

    rankings = sorted(
        results.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # =====================
    # CALCULATE PERCENTAGES
    # =====================

    percentages = {}

    for candidate, votes_count in results.items():

        if total_votes > 0:

            percentage = (
                votes_count / total_votes
            ) * 100

        else:

            percentage = 0

        percentages[candidate] = round(
            percentage,
            2
        )

    # =====================
    # RENDER DASHBOARD
    # =====================

    return render_template(
        'results.html',

        results=results,

        rankings=rankings,

        percentages=percentages,

        total_voters=total_voters,

        total_votes=total_votes,

        admin_name=session['username']
    )

    # =====================
    # DECRYPT VOTES
    # =====================

    for vote in votes:

        encrypted_vote_json = (
            vote[2]
        )

        encrypted_key_b64 = (
            vote[3]
        )

        stored_hash = (
            vote[4]
        )

        # VERIFY HASH
        if verify_hash(
            encrypted_vote_json,
            stored_hash
        ):

            encrypted_key = (
                base64.b64decode(
                    encrypted_key_b64
                )
            )

            aes_key = decrypt_aes_key(
                encrypted_key,
                admin_private_key
            )

            encrypted_vote = (
                json.loads(
                    encrypted_vote_json
                )
            )

            decrypted_vote = decrypt_vote(
                encrypted_vote,
                aes_key
            )

            decrypted_votes.append(
                decrypted_vote
            )

    # =====================
    # COUNT RESULTS
    # =====================

    results = {}

    for candidate in decrypted_votes:

        results[candidate] = (
            results.get(candidate, 0) + 1
        )

    return render_template(
        'results.html',
        results=results
    )

# =========================
# DOWNLOAD RECEIPT
# =========================

@app.route('/download_receipt')
def download_receipt():

    # MUST LOGIN

    if 'username' not in session:

        return redirect('/')

    voter_id = session['username']

    conn = sqlite3.connect(
        'database.db'
    )

    cursor = conn.cursor()

    cursor.execute("""

    SELECT encrypted_vote,
           vote_hash

    FROM votes

    WHERE voter_id = ?

    ORDER BY id DESC

    LIMIT 1

    """, (voter_id,))

    vote = cursor.fetchone()

    conn.close()

    if not vote:

        return "No receipt found."

    encrypted_vote = vote[0]

    vote_hash = vote[1]

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # =====================
    # RECEIPT CONTENT
    # =====================

    receipt_content = f"""

====================================

 SECURE ONLINE VOTING RECEIPT

====================================

Voter ID:
{voter_id}

Timestamp:
{timestamp}

------------------------------------

Encrypted Vote:

{encrypted_vote}

------------------------------------

SHA-256 Integrity Hash:

{vote_hash}

------------------------------------

Security Status:
VERIFIED & SECURE

====================================

Generated By:
Secure Online Voting System

====================================

"""

    # =====================
    # CREATE TXT FILE
    # =====================

    receipt_file = io.BytesIO()

    receipt_file.write(
        receipt_content.encode()
    )

    receipt_file.seek(0)

    return send_file(

        receipt_file,

        as_attachment=True,

        download_name=
        f"{voter_id}_receipt.txt",

        mimetype='text/plain'
    )
# =========================
# VERIFY RECEIPT
# =========================

@app.route('/verify', methods=['GET', 'POST'])
def verify_receipt():

    verification_result = None

    if request.method == 'POST':

        encrypted_vote = request.form[
            'encrypted_vote'
        ]

        vote_hash = request.form[
            'vote_hash'
        ]

        # GENERATE NEW HASH

        generated_hash = generate_hash(
            encrypted_vote
        )

        # VERIFY

        if generated_hash == vote_hash:

            verification_result = (
                "VERIFIED"
            )

        else:

            verification_result = (
                "TAMPERED"
            )

    return render_template(
        'verify.html',
        verification_result=
        verification_result
    )

# =========================
# RUN APP
# =========================

if __name__ == '__main__':

    app.run(debug=True)

    
    