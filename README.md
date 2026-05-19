# AI Study Assistant

An intelligent agent powered by Claude that helps users research and understand topics using multiple tools.

## What it does

The assistant receives a natural-language question or task from the user and autonomously decides which tools to call — calculator, file reader, or web search — to produce a well-informed answer.

## Tools

| Tool | Purpose |
|------|---------|
| `calculator` | Evaluate mathematical expressions and perform numeric computations |
| `file_reader` | Read and extract text from `.txt` and `.csv` files |
| `web_search` | Search the web via DuckDuckGo and return relevant results |

## Project Structure

```
agent_assignment/
├── src/
│   ├── agent.py        # Main agent loop and tool orchestration
│   ├── config.py       # Environment and model configuration
│   └── tools/
│       ├── calculator.py
│       ├── file_reader.py
│       └── web_search.py
├── tests/
│   ├── test_tools.py
│   └── test_agent.py
├── examples/
│   └── sample_files/   # Sample input files for demo
├── main.py             # CLI entry point
├── requirements.txt
└── .env.example
```

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd agent_assignment
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

Get your key at https://console.anthropic.com/

## Running the assistant

```bash
python main.py
```

You will be prompted to enter your question. Type `exit` or `quit` to stop.

### Example session

```
You: What is the square root of 1764?
Assistant: The square root of 1764 is 42.

You: What are the latest developments in quantum computing?
Assistant: [performs web search and summarises results]

You: Summarise the file examples/sample_files/notes.txt
Assistant: [reads the file and summarises it]
```

## Running tests

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | — | Your Anthropic API key |
| `CLAUDE_MODEL` | No | `claude-sonnet-4-6` | Claude model to use |

## Deployment

This project is designed as a **local command-line application**. To deploy it on any machine:

1. Follow the Setup steps above.
2. Run `python main.py`.

For a staged deployment: test on a local machine first, then transfer to a controlled server environment using the same setup steps. No cloud infrastructure is required.
