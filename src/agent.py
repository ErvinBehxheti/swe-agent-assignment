import json
from typing import Any

import anthropic

from src.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS
from src.tools.calculator import calculate
from src.tools.file_reader import read_file
from src.tools.web_search import web_search

# Tool schemas sent to Claude so it knows what it can call
TOOL_DEFINITIONS = [
    {
        "name": "calculator",
        "description": (
            "Evaluate a mathematical expression. Supports +, -, *, /, **, %, "
            "floor division, and functions: sqrt, abs, round, ceil, floor, "
            "log, log2, log10, sin, cos, tan. Constants: pi, e."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate, e.g. 'sqrt(144) + 2**8'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "file_reader",
        "description": (
            "Read the contents of a .txt, .csv, or .md file from the local filesystem. "
            "CSV files are formatted as a readable table."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Relative or absolute path to the file, e.g. 'examples/sample_files/notes.txt'",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "web_search",
        "description": (
            "Search the web using DuckDuckGo and return the top results with titles, "
            "URLs, and short snippets. Use this for current information or topics "
            "not covered by other tools."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5, max 10)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
]

_TOOL_HANDLERS: dict[str, Any] = {
    "calculator": lambda inp: calculate(inp["expression"]),
    "file_reader": lambda inp: read_file(inp["file_path"]),
    "web_search": lambda inp: web_search(inp["query"], inp.get("max_results", 5)),
}

SYSTEM_PROMPT = """You are a helpful AI Study Assistant. You help users understand topics, \
solve math problems, analyse files, and find information on the web.

You have three tools available:
- calculator: for any numeric or mathematical computation
- file_reader: to read and analyse local text or CSV files
- web_search: to look up current information on the internet

Always use a tool when it would produce a more accurate or complete answer. \
After receiving tool results, synthesise the information into a clear, concise response."""


class StudyAssistant:
    """
    Conversational AI agent that uses Claude with tool use.

    Maintains a running message history so the user can ask follow-up
    questions within the same session.
    """

    def __init__(self):
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self._history: list[dict] = []

    def chat(self, user_message: str) -> str:
        """
        Send a user message, run the tool-use loop, and return the final reply.
        """
        self._history.append({"role": "user", "content": user_message})

        while True:
            response = self._client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=self._history,
            )

            # Collect all content blocks from the response
            assistant_content = response.content
            self._history.append({"role": "assistant", "content": assistant_content})

            if response.stop_reason == "end_turn":
                # Extract plain text from the final response
                text_blocks = [b.text for b in assistant_content if hasattr(b, "text")]
                return "\n".join(text_blocks)

            if response.stop_reason == "tool_use":
                tool_results = self._run_tools(assistant_content)
                self._history.append({"role": "user", "content": tool_results})
                continue

            # Unexpected stop reason — return whatever text is available
            text_blocks = [b.text for b in assistant_content if hasattr(b, "text")]
            return "\n".join(text_blocks) if text_blocks else "(no response)"

    def _run_tools(self, content_blocks) -> list[dict]:
        """Execute every tool_use block and return tool_result blocks."""
        results = []
        for block in content_blocks:
            if block.type != "tool_use":
                continue

            handler = _TOOL_HANDLERS.get(block.name)
            if handler is None:
                output = {"error": f"Unknown tool: {block.name}"}
            else:
                try:
                    output = handler(block.input)
                except Exception as exc:
                    output = {"error": str(exc)}

            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(output),
            })

        return results

    def reset(self):
        """Clear conversation history to start a fresh session."""
        self._history = []
