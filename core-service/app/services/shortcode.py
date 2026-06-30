import secrets
import string

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase


def generate_short_code(length: int = 7) -> str:
    """Generate a random base62 string. Using `secrets` (not `random`) since
    short codes are unguessable identifiers, not just unique ones - a
    predictable PRNG would let someone enumerate other users' links."""
    return "".join(secrets.choice(BASE62_ALPHABET) for _ in range(length))
