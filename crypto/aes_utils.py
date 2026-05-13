from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

# Generate AES Key
def generate_aes_key():
    return get_random_bytes(16)

# Encrypt Vote
def encrypt_vote(vote, key):

    cipher = AES.new(key, AES.MODE_EAX)

    ciphertext, tag = cipher.encrypt_and_digest(
        vote.encode()
    )

    encrypted_data = {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(cipher.nonce).decode(),
        "tag": base64.b64encode(tag).decode()
    }

    return encrypted_data

# Decrypt Vote
def decrypt_vote(encrypted_data, key):

    nonce = base64.b64decode(
        encrypted_data["nonce"]
    )

    ciphertext = base64.b64decode(
        encrypted_data["ciphertext"]
    )

    tag = base64.b64decode(
        encrypted_data["tag"]
    )

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    decrypted_vote = cipher.decrypt_and_verify(
        ciphertext,
        tag
    )

    return decrypted_vote.decode()
