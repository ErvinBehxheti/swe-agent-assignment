"""
Integration tests for the StudyAssistant agent.
The Anthropic client is fully mocked — no API key or network access needed.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.agent import StudyAssistant


def _make_text_response(text: str, stop_reason: str = "end_turn"):
    """Build a fake Claude response that contains a single text block."""
    block = MagicMock()
    block.type = "text"
    block.text = text

    response = MagicMock()
    response.content = [block]
    response.stop_reason = stop_reason
    return response


def _make_tool_use_response(tool_name: str, tool_input: dict, tool_use_id: str = "tu_001"):
    """Build a fake Claude response that requests a tool call."""
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = tool_name
    tool_block.input = tool_input
    tool_block.id = tool_use_id

    response = MagicMock()
    response.content = [tool_block]
    response.stop_reason = "tool_use"
    return response


# ---------------------------------------------------------------------------
# Basic conversation
# ---------------------------------------------------------------------------

class TestStudyAssistantBasic:
    @patch("src.agent.anthropic.Anthropic")
    def test_simple_text_reply(self, MockAnthropic):
        client = MockAnthropic.return_value
        client.messages.create.return_value = _make_text_response("Hello there!")

        assistant = StudyAssistant()
        reply = assistant.chat("Hi")
        assert reply == "Hello there!"

    @patch("src.agent.anthropic.Anthropic")
    def test_history_grows_per_turn(self, MockAnthropic):
        client = MockAnthropic.return_value
        client.messages.create.return_value = _make_text_response("answer")

        assistant = StudyAssistant()
        assistant.chat("first question")
        assistant.chat("second question")
        # After two turns: 2 user + 2 assistant messages
        assert len(assistant._history) == 4

    @patch("src.agent.anthropic.Anthropic")
    def test_reset_clears_history(self, MockAnthropic):
        client = MockAnthropic.return_value
        client.messages.create.return_value = _make_text_response("ok")

        assistant = StudyAssistant()
        assistant.chat("hello")
        assistant.reset()
        assert assistant._history == []


# ---------------------------------------------------------------------------
# Tool-use loop
# ---------------------------------------------------------------------------

class TestStudyAssistantToolUse:
    @patch("src.agent.anthropic.Anthropic")
    def test_calculator_tool_called(self, MockAnthropic):
        client = MockAnthropic.return_value
        client.messages.create.side_effect = [
            _make_tool_use_response("calculator", {"expression": "6 * 7"}),
            _make_text_response("6 multiplied by 7 is 42."),
        ]

        assistant = StudyAssistant()
        reply = assistant.chat("What is 6 times 7?")

        assert reply == "6 multiplied by 7 is 42."
        # Two API calls: one that triggered tool use, one after the result
        assert client.messages.create.call_count == 2

    @patch("src.agent.anthropic.Anthropic")
    def test_tool_result_sent_back(self, MockAnthropic):
        client = MockAnthropic.return_value
        client.messages.create.side_effect = [
            _make_tool_use_response("calculator", {"expression": "sqrt(144)"}, tool_use_id="tu_123"),
            _make_text_response("The square root of 144 is 12."),
        ]

        assistant = StudyAssistant()
        assistant.chat("What is the square root of 144?")

        # The history must contain a user message with a tool_result block.
        # We inspect history directly rather than call_args (list is mutated after the call).
        tool_result_messages = [
            m for m in assistant._history
            if m["role"] == "user" and isinstance(m["content"], list)
        ]
        assert any(
            block.get("type") == "tool_result"
            for msg in tool_result_messages
            for block in msg["content"]
        )

    @patch("src.agent.anthropic.Anthropic")
    def test_file_reader_tool_called(self, MockAnthropic, tmp_path):
        f = tmp_path / "notes.txt"
        f.write_text("Important note: study hard.", encoding="utf-8")

        client = MockAnthropic.return_value
        client.messages.create.side_effect = [
            _make_tool_use_response("file_reader", {"file_path": str(f)}),
            _make_text_response("The file says: study hard."),
        ]

        assistant = StudyAssistant()
        reply = assistant.chat(f"Read the file {f}")
        assert "study hard" in reply

    @patch("src.agent.anthropic.Anthropic")
    def test_web_search_tool_called(self, MockAnthropic):
        client = MockAnthropic.return_value
        client.messages.create.side_effect = [
            _make_tool_use_response("web_search", {"query": "latest AI news"}),
            _make_text_response("Here are the latest AI developments..."),
        ]

        with patch("src.tools.web_search.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = [
                {"title": "AI News", "href": "https://example.com", "body": "AI is advancing."}
            ]
            assistant = StudyAssistant()
            reply = assistant.chat("What is the latest in AI?")

        assert "AI" in reply

    @patch("src.agent.anthropic.Anthropic")
    def test_unknown_tool_returns_error(self, MockAnthropic):
        client = MockAnthropic.return_value
        client.messages.create.side_effect = [
            _make_tool_use_response("nonexistent_tool", {"param": "value"}),
            _make_text_response("I encountered an issue with that tool."),
        ]

        assistant = StudyAssistant()
        reply = assistant.chat("Use the mystery tool")

        # Should still reach a final response without crashing
        assert isinstance(reply, str)

    @patch("src.agent.anthropic.Anthropic")
    def test_multi_turn_with_tool(self, MockAnthropic):
        client = MockAnthropic.return_value
        client.messages.create.side_effect = [
            _make_text_response("Sure, what topic?"),
            _make_tool_use_response("calculator", {"expression": "2 ** 10"}),
            _make_text_response("2 to the power of 10 is 1024."),
        ]

        assistant = StudyAssistant()
        assistant.chat("Can you help me with math?")
        reply = assistant.chat("What is 2 to the power of 10?")
        assert "1024" in reply
