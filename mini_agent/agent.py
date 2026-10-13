"""The agent loop itself.

    messages -> llm -> tool_calls? -> execute tools, append results -> repeat
             -> no tool_calls (plain text) -> return the answer
"""

from dataclasses import dataclass, field

from .tools import ToolRegistry, default_registry


@dataclass
class Step:
    number: int
    tool_calls: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)
    final_text: str | None = None


class Agent:
    def __init__(
        self,
        llm,
        tools: ToolRegistry | None = None,
        system_prompt: str | None = None,
        max_steps: int = 10,
        on_step=None,
    ) -> None:
        self.llm = llm
        self.tools = tools or default_registry()
        self.system_prompt = system_prompt or (
            "You are an agent. Use the add tool for any arithmetic, then reply "
            "with only the final answer as plain text."
        )
        self.max_steps = max_steps
        self.on_step = on_step
        self.messages: list[dict] = []
        self.trace: list[Step] = []

    def run(self, task: str) -> str:
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task},
        ]
        self.trace = []

        for number in range(1, self.max_steps + 1):
            message = self.llm.chat(self.messages, tools=self.tools.schemas())
            self.messages.append(message)

            tool_calls = message.get("tool_calls") or []
            if not tool_calls:
                step = Step(number=number, final_text=message.get("content") or "")
                self.trace.append(step)
                self._emit(step)
                return step.final_text

            step = Step(number=number, tool_calls=tool_calls)
            for call in tool_calls:
                function = call["function"]
                result = self.tools.execute(function["name"], function.get("arguments") or "")
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": result.content,
                })
                step.tool_results.append({
                    "name": function["name"],
                    "call_id": call["id"],
                    "content": result.content,
                    "is_error": result.is_error,
                })
            self.trace.append(step)
            self._emit(step)

        return f"[stopped] max_steps={self.max_steps} reached without a final answer"

    def _emit(self, step: Step) -> None:
        if self.on_step is not None:
            self.on_step(step)
