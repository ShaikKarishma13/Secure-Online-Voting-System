from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

import os


# =========================
# GENERATE & SAVE RSA KEYS
# =========================

def generate_rsa_keys():

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    return private_key, public_key


# =========================
# SAVE KEYS
# =========================

def save_keys(private_key, public_key):

    # CREATE FOLDER

    if not os.path.exists("keys"):

        os.makedirs("keys")

    # PRIVATE KEY

    with open(
        "keys/admin_private.pem",
        "wb"
    ) as private_file:

        private_file.write(

            private_key.private_bytes(

                encoding=serialization.Encoding.PEM,

                format=serialization.PrivateFormat.PKCS8,

                encryption_algorithm=
                serialization.NoEncryption()
            )
        )

    # PUBLIC KEY

    with open(
        "keys/admin_public.pem",
        "wb"
    ) as public_file:

        public_file.write(

            public_key.public_bytes(

                encoding=serialization.Encoding.PEM,

                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )


# =========================
# LOAD KEYS
# =========================

def load_keys():

    with open(
        "keys/admin_private.pem",
        "rb"
    ) as private_file:

        private_key = serialization.load_pem_private_key(

            private_file.read(),

            password=None
        )

    with open(
        "keys/admin_public.pem",
        "rb"
    ) as public_file:

        public_key = serialization.load_pem_public_key(

            public_file.read()
        )

    return private_key, public_key


# =========================
# ENCRYPT AES KEY
# =========================

def encrypt_aes_key(aes_key, public_key):

    encrypted_key = public_key.encrypt(

        aes_key,

        padding.OAEP(

            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),

            algorithm=hashes.SHA256(),

            label=None
        )
    )

    return encrypted_key


# =========================
# DECRYPT AES KEY
# =========================

def decrypt_aes_key(encrypted_key, private_key):

    decrypted_key = private_key.decrypt(

        encrypted_key,

        padding.OAEP(

            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),

            algorithm=hashes.SHA256(),

            label=None
        )
    )

    return decrypted_key