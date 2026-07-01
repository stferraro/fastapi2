import hashlib
import os


def hash_api_key(raw_api_key: str) -> str:
	pepper = os.getenv("API_KEY_PEPPER", "")
	payload = f"{pepper}:{raw_api_key}".encode("utf-8")
	return hashlib.sha256(payload).hexdigest()