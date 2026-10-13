"""Offline validation of the loop mechanics (no API key needed).

Run: python -m unittest mini_agent.test_agent -v
"""

import unittest

from .agent import Agent
from .fake_llm import ScriptedLLM, text_message, tool_call_message
from .tools import default_registry


def make_agent(responses: list[dict], max_steps: int = 10) -> Agent:
    return Agent(llm=ScriptedLLM(responses), tools=default_registry(), max_steps=max_steps)


class LoopMechanicsTests(unittest.TestCase):
    def test_tool_call_then_final_answer(self):
        agent = make_agent([
            tool_call_message("call_1", "add", {"a": 2, "b": 2}),
            text_message("4"),
        ])
        final = agent.run("What is 2 + 2?")
        self.assertEqual(final, "4")
        self.assertEqual([s.number for s in agent.trace], [1, 2])
        self.assertIsNone(agent.trace[0].final_text)
        self.assertEqual(agent.trace[0].tool_results[0]["content"], "4")

        tool_messages = [m for m in agent.messages if m["role"] == "tool"]
        self.assertEqual(len(tool_messages), 1)
        self.assertEqual(tool_messages[0]["tool_call_id"], "call_1")
        self.assertEqual(tool_messages[0]["content"], "4")

    def test_multi_step_chain(self):
        agent = make_agent([
            tool_call_message("call_1", "add", {"a": 2, "b": 2}),
            tool_call_message("call_2", "add", {"a": 4, "b": 6}),
            text_message("10"),
        ])
        final = agent.run("Compute 2+2, then add 6 to the result.")
        self.assertEqual(final, "10")
        self.assertEqual(len(agent.trace), 3)
        self.assertEqual(agent.trace[1].tool_results[0]["content"], "10")

    def test_unknown_tool_error_is_fed_back_and_loop_continues(self):
        agent = make_agent([
            tool_call_message("call_1", "teleport", {"x": 1}),
            text_message("I cannot do that."),
        ])
        final = agent.run("Teleport me to Mars.")
        self.assertEqual(final, "I cannot do that.")
        result = agent.trace[0].tool_results[0]
        self.assertTrue(result["is_error"])
        self.assertIn("unknown tool", result["content"])
        tool_messages = [m for m in agent.messages if m["role"] == "tool"]
        self.assertEqual(tool_messages[0]["tool_call_id"], "call_1")

    def test_bad_arguments_error_is_fed_back(self):
        agent = make_agent([
            tool_call_message("call_1", "add", {"a": "two"}),
            text_message("Bad input."),
        ])
        final = agent.run("Add 'two' and 3.")
        self.assertEqual(final, "Bad input.")
        self.assertTrue(agent.trace[0].tool_results[0]["is_error"])

    def test_max_steps_guard_stops_endless_looping(self):
        endless = [tool_call_message(f"call_{i}", "get_time", {}) for i in range(50)]
        agent = make_agent(endless, max_steps=5)
        final = agent.run("What time is it? Keep checking.")
        self.assertIn("max_steps=5", final)
        self.assertEqual(len(agent.trace), 5)
        self.assertEqual(len(agent.llm.calls), 5)

    def test_tools_and_system_prompt_are_advertised_to_llm(self):
        llm = ScriptedLLM([text_message("done")])
        Agent(llm=llm, tools=default_registry()).run("hi")
        names = [t["function"]["name"] for t in llm.calls[0]["tools"]]
        self.assertIn("add", names)
        self.assertIn("get_time", names)
        self.assertEqual(llm.calls[0]["messages"][0]["role"], "system")

    def test_plain_question_answers_in_one_step(self):
        agent = make_agent([text_message("Hello!")])
        final = agent.run("Say hello.")
        self.assertEqual(final, "Hello!")
        self.assertEqual(len(agent.trace), 1)
        self.assertEqual(agent.trace[0].final_text, "Hello!")

    def test_tool_result_visible_in_next_llm_call(self):
        llm = ScriptedLLM([
            tool_call_message("call_1", "add", {"a": 20, "b": 22}),
            text_message("42"),
        ])
        Agent(llm=llm, tools=default_registry()).run("What is 20 + 22?")
        second_call_messages = llm.calls[1]["messages"]
        tool_messages = [m for m in second_call_messages if m["role"] == "tool"]
        self.assertEqual(tool_messages[0]["content"], "42")


if __name__ == "__main__":
    unittest.main()
