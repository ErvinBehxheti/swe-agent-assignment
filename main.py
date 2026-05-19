"""
AI Study Assistant — command-line entry point.

Usage:
    python main.py

Type your question and press Enter. Type 'exit', 'quit', or Ctrl-C to stop.
Type 'reset' to clear the conversation history and start fresh.
"""

from src.agent import StudyAssistant


def main():
    print("=" * 60)
    print("  AI Study Assistant")
    print("  Powered by Claude | Tools: calculator, file reader, web search")
    print("  Type 'exit' to quit | 'reset' to clear history")
    print("=" * 60)
    print()

    assistant = StudyAssistant()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if user_input.lower() == "reset":
            assistant.reset()
            print("Conversation history cleared.\n")
            continue

        try:
            reply = assistant.chat(user_input)
            print(f"\nAssistant: {reply}\n")
        except Exception as exc:
            print(f"\n[Error] {exc}\n")


if __name__ == "__main__":
    main()
