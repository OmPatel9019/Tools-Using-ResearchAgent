"""
CLI Runner for the Tool-Using Research Agent powered by Google Gemini & Tavily.
"""

import argparse
import sys
import os

# Ensure robust UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from agent import ResearchAgent, console
from rich.panel import Panel
from rich.prompt import Prompt


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Tool-Using Research Agent using Google Gemini & Tavily Search."
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        help="Research question or topic to investigate."
    )
    parser.add_argument(
        "--max-steps", "-s",
        type=int,
        default=5,
        help="Hard step limit to prevent infinite tool loops (default: 5)."
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="Gemini model identifier (e.g. gemini-2.5-flash, gemini-1.5-flash, gemini-2.5-pro)."
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in mock/offline mode to test the agent loop without API keys."
    )

    args = parser.parse_args()

    console.print(Panel(
        "[bold cyan]Tool-Using Autonomous Research Agent (Gemini + Tavily)[/bold cyan]\n"
        "[dim]Multi-Tool Routing | Hard Step Limits | Real-World Citations | Fault-Tolerant[/dim]",
        border_style="cyan"
    ))

    query = args.query
    if not query:
        query = Prompt.ask(
            "[bold yellow]Enter your research question[/bold yellow]",
            default="What are the key architectural improvements in Transformer reasoning models like DeepSeek-R1?"
        )

    agent = ResearchAgent(
        model=args.model,
        max_steps=args.max_steps,
        mock_mode=args.mock
    )

    agent.run(query)


if __name__ == "__main__":
    main()
