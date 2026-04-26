import hashlib

def generate_hash(content: str) -> str:
    """Generates a SHA-256 hash of the given content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
