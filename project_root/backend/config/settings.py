from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    REQUEST_TIMEOUT: int = 10
    MAX_CONTENT_BYTES: int = 5 * 1024 * 1024  # 5 MB
    USER_AGENTS: List[str] = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36',
    ]

settings = Settings()
