import hashlib
import base64
import uuid


def md5(data: bytes) -> str:
    """Generate an MD5 hash for the given data."""
    return hashlib.md5(data).hexdigest()


def sha1(data: bytes) -> str:
    """Generate a SHA-1 hash for the given data."""
    return hashlib.sha1(data).hexdigest()


def sha256(data: bytes) -> str:
    """Generate a SHA-256 hash for the given data."""
    return hashlib.sha256(data).hexdigest()


def sha512(data: bytes) -> str:
    """Generate a SHA-512 hash for the given data."""
    return hashlib.sha512(data).hexdigest()


def hmac_sha256(key: bytes, data: bytes) -> str:
    """Generate an HMAC-SHA256 hash for the given data using the provided key."""
    return hashlib.pbkdf2_hmac("sha256", data, key, 100000).hex()


def hmac_sha512(key: bytes, data: bytes) -> str:
    """Generate an HMAC-SHA512 hash for the given data using the provided key."""
    return hashlib.pbkdf2_hmac("sha512", data, key, 100000).hex()


def hmac(key: bytes, data: bytes, algorithm: str = "sha256") -> str:
    """Generate an HMAC hash for the given data using the provided key and algorithm."""
    try:
        return hashlib.pbkdf2_hmac(algorithm, data, key, 100000).hex()
    except ValueError:
        return ""


def blake2b(data: bytes) -> str:
    """Generate a BLAKE2b hash for the given data."""
    return hashlib.blake2b(data).hexdigest()


def blake2s(data: bytes) -> str:
    """Generate a BLAKE2s hash for the given data."""
    return hashlib.blake2s(data).hexdigest()


def sha3_256(data: bytes) -> str:
    """Generate a SHA3-256 hash for the given data."""
    return hashlib.sha3_256(data).hexdigest()


def uuid5(namespace: uuid.UUID, name: str) -> str:
    return str(uuid.uuid5(namespace, name))


def uuid4() -> str:
    return str(uuid.uuid4())


def uuid3(namespace: uuid.UUID, name: str) -> str:
    return str(uuid.uuid3(namespace, name))


def uuid1() -> str:
    return str(uuid.uuid1())


def base64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def base64_decode(data: str) -> bytes:
    try:
        return base64.b64decode(data)
    except Exception:
        return b""


def apply_hash_algorithm(algorithm: str, data: bytes) -> str:
    """Apply the specified hash algorithm to the given data."""
    algorithms = {
        "md5": md5,
        "sha1": sha1,
        "sha256": sha256,
        "sha512": sha512,
        "blake2b": blake2b,
        "blake2s": blake2s,
        "sha3_256": sha3_256,
    }
    func = algorithms.get(algorithm.lower())
    if func:
        return func(data)
    return ""
