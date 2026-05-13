from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import sqlite3
import json
import base64
import re

from crypto.aes_utils import (
    generate_aes_key,
    encrypt_vote,
    decrypt_vote
)

from crypto.rsa_utils import (
    generate_rsa_keys,
    encrypt_aes_key,
    decrypt_aes_key
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

admin_private_key, admin_public_key = (
    generate_rsa_keys()
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

    return render_template(
        'results.html',
        results=results
    )


# =========================
# RUN APP
# =========================

if __name__ == '__main__':

    app.run(debug=True)
    