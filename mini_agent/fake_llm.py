"""Scripted LLM for offline tests: returns pre-baked responses in order."""

import json


class ScriptedLLM:
    def __init__(self, responses: list[dict]):
        self.responses = list(responses)
        self.calls: list[dict] = []

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        self.calls.append({"messages": [dict(m) for m in messages], "tools": tools})
        if not self.responses:
            raise AssertionError("ScriptedLLM ran out of scripted responses")
        return self.responses.pop(0)


def text_message(text: str) -> dict:
    return {"role": "assistant", "content": text}


def tool_call_message(call_id: str, name: str, arguments: dict) -> dict:
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": call_id,
            "type": "function",
            "function": {"name": name, "arguments": json.dumps(arguments)},
        }],
    }
