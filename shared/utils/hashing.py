import hashlib

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def cache_key(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()