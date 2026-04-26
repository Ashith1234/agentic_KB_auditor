import uuid

def generate_id(prefix: str = "") -> str:
    """Generates a unique ID with an optional prefix."""
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id
