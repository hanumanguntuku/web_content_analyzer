import hashlib

def short_hash(s: str) -> str:
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:10]
