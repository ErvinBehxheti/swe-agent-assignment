import os

# Provide a dummy key so config.py does not raise during test collection.
# Real API calls are never made — the Anthropic client is mocked in every test.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-for-pytest")
