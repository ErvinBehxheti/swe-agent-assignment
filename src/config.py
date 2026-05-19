import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

MAX_TOKENS = 4096
MAX_SEARCH_RESULTS = 5
MAX_FILE_SIZE_BYTES = 1_000_000  # 1 MB

if not ANTHROPIC_API_KEY:
    raise EnvironmentError(
        "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
    )
