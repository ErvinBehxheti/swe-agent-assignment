# Deployment Strategy

## Current deployment model

The AI Study Assistant is deployed as a **local command-line application**.
This is the appropriate model for a controlled, single-user environment where
the user has Python installed and holds their own Anthropic API key.

### Why local CLI

- No server infrastructure is required.
- The API key stays on the user's machine and is never transmitted to a third party.
- Installation is a single `pip install -r requirements.txt` step.
- The system is fully reproducible from the repository.

## How to deploy to a new machine

```bash
# 1. Clone the repository
git clone <repo-url>
cd agent_assignment

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the API key
cp .env.example .env
# Open .env and set ANTHROPIC_API_KEY=<your-key>

# 5. Run
python main.py
```

## Data flow and conversion

| Stage | Format | Transformation |
|-------|--------|---------------|
| User input | Plain string (CLI) | Passed as a `user` message to Claude |
| Claude tool request | Anthropic `ToolUseBlock` | Extracted and dispatched to the matching Python function |
| Calculator result | Python `dict` | Serialised to JSON, sent back as a `tool_result` block |
| File reader result | Python `dict` with `content` string | Same — JSON-serialised |
| Web search result | Python `dict` with `results` list | Same — JSON-serialised |
| Final Claude reply | `TextBlock` list | Joined into a single string and printed to stdout |

All data travels through a single `json.dumps()` serialisation step before
being returned to Claude, ensuring consistent UTF-8 text regardless of which
tool produced the result.

## Proposed staged release strategy

If this system were to be released more broadly, the recommended stages are:

1. **Alpha (local)** — developer runs it locally, verifies all tools work with real API calls.
2. **Beta (shared machine)** — install on a shared server, expose via a simple FastAPI endpoint,
   restrict access to trusted users with an HTTP API key header.
3. **Production (web service)** — containerise with Docker, deploy behind a reverse proxy (nginx),
   rotate API keys via environment secrets in the CI/CD pipeline (e.g. GitHub Actions → cloud VM).
   Add request logging and rate limiting at the API gateway level.

For this assignment the system remains in **Alpha / local** stage, which is
sufficient for a controlled demonstration.
