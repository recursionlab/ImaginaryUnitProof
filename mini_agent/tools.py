"""Tool layer: schemas the model sees, plus local execution."""

import json
import time
from dataclasses import dataclass


@dataclass
class ToolResult:
    content: str
    is_error: bool = False


class Tool:
    def __init__(self, name: str, description: str, parameters: dict, handler):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def execute(self, arguments_json: str) -> ToolResult:
        try:
            args = json.loads(arguments_json) if arguments_json else {}
            result = self.handler(**args)
            return ToolResult(content=json.dumps(result))
        except Exception as exc:
            return ToolResult(content=f"ERROR: {exc}", is_error=True)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def schemas(self) -> list[dict]:
        return [tool.schema() for tool in self._tools.values()]

    def execute(self, name: str, arguments_json: str) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(content=f"ERROR: unknown tool '{name}'", is_error=True)
        return tool.execute(arguments_json)


def default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    def add(a: float, b: float) -> float:
        return a + b

    def get_time() -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S")

    registry.register(Tool(
        name="add",
        description="Add two numbers and return the sum.",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First addend"},
                "b": {"type": "number", "description": "Second addend"},
            },
            "required": ["a", "b"],
        },
        handler=add,
    ))
    registry.register(Tool(
        name="get_time",
        description="Get the current local date and time.",
        parameters={"type": "object", "properties": {}},
        handler=get_time,
    ))
    return registry
