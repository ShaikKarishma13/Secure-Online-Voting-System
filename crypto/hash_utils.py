import hashlib

# Generate SHA256 Hash
def generate_hash(data):

    return hashlib.sha256(
        data.encode()
    ).hexdigest()


# Verify Hash
def verify_hash(data, old_hash):

    new_hash = hashlib.sha256(
        data.encode()
    ).hexdigest()

    return new_hash == old_hash