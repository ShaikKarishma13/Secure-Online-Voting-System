from flask import Flask, render_template, request
import sqlite3

from crypto.aes_utils import *
from crypto.rsa_utils import *
from crypto.hash_utils import *

app = Flask(__name__)

# Generate Admin RSA Keys
admin_private_key, admin_public_key = generate_rsa_keys()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():

    if request.method == 'POST':

        voter_id = request.form['voter_id']
        selected_candidate = request.form['candidate']

        # AES Key Generation
        aes_key = generate_aes_key()

        # Encrypt Vote
        encrypted_vote = encrypt_vote(
            selected_candidate,
            aes_key
        )

        # Encrypt AES Key using RSA
        encrypted_key = encrypt_aes_key(
            aes_key,
            admin_public_key
        )

        # Generate SHA-256 Hash
        vote_hash = generate_hash(
            encrypted_vote
        )

        # Store in Database
        conn = sqlite3.connect('database.db')

        cursor = conn.cursor()

        cursor.execute('''

        INSERT INTO votes(
            voter_id,
            encrypted_vote,
            encrypted_key,
            vote_hash
        )

        VALUES (?, ?, ?, ?)

        ''', (

            voter_id,
            encrypted_vote,
            encrypted_key,
            vote_hash

        ))

        conn.commit()
        conn.close()

        return f"""

        <h2>Vote Cast Successfully!</h2>

        <p><b>Encrypted Vote:</b> {encrypted_vote}</p>

        <p><b>SHA-256 Hash:</b> {vote_hash}</p>

        <a href='/'>Go Back</a>

        """

    return render_template('vote.html')

@app.route('/admin')
def admin():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM votes")

    votes = cursor.fetchall()

    decrypted_votes = []

    for vote in votes:

        encrypted_vote = vote[2]

        encrypted_key = vote[3]

        stored_hash = vote[4]

        # Verify Integrity
        if verify_hash(
            encrypted_vote,
            stored_hash
        ):

            aes_key = decrypt_aes_key(
                encrypted_key,
                admin_private_key
            )

            decrypted_vote = decrypt_vote(
                encrypted_vote,
                aes_key
            )

            decrypted_votes.append(
                decrypted_vote
            )

    results = {}

    for candidate in decrypted_votes:

        results[candidate] = results.get(
            candidate,
            0
        ) + 1

    return render_template(
        'results.html',
        results=results
    )

if __name__ == '__main__':

    app.run(debug=True)
    