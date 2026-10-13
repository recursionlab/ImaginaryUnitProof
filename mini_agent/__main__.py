"""Run the agent loop against a real model.

    python -m mini_agent "What is 2 + 2? Use the add tool."
    python -m mini_agent --model nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free "..."
"""

import argparse

from .agent import Agent
from .llm import OpenRouterClient


def print_step(step) -> None:
    if step.final_text is not None:
        print(f"[step {step.number}] FINAL: {step.final_text}")
        return
    for call in step.tool_calls:
        function = call["function"]
        print(f"[step {step.number}] CALL: {function['name']}({function.get('arguments')})")
    for result in step.tool_results:
        status = "ERROR" if result["is_error"] else "OK"
        print(f"[step {step.number}] RESULT ({status}): {result['content']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal agent loop")
    parser.add_argument("task", nargs="?", default="What is 2 + 2? Use the add tool, then answer with just the number.")
    parser.add_argument("--model", default=None, help="OpenRouter model id (default: free nemotron)")
    parser.add_argument("--max-steps", type=int, default=10)
    args = parser.parse_args()

    agent = Agent(
        llm=OpenRouterClient(model=args.model),
        max_steps=args.max_steps,
        on_step=print_step,
    )
    final = agent.run(args.task)
    print(f"\nAgent finished: {final}")


if __name__ == "__main__":
    main()
