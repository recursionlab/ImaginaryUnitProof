from gradio_client import Client
import os

HF_TOKEN = os.environ.get("HF_TOKEN")
client = Client("autotrust/jev-9b-decision-demo", token=HF_TOKEN)

def decide(state: str, questions: list[dict]):
    """
    Ask multiple typed questions about one piece of state text.
    
    questions = [
        {"type": "choice", "instructions": "Is this positive?", "options": "yes,no"},
        {"type": "score", "instructions": "Rate 1-10", "options": ""},
        {"type": "noul", "instructions": "", "options": ""},
        {"type": "noul", "instructions": "", "options": ""},
    ]
    Types: "noul" (no question), "choice", "score"
    """
    params = {"state": state}
    for i, q in enumerate(questions[:4], 1):
        params[f"param_{3*i-2}"] = q.get("type", "noul")
        params[f"param_{3*i-1}"] = q.get("instructions", "")
        params[f"param_{3*i}"] = q.get("options", "")
    return client.predict(**params, api_name="/decide")

def escalate(state: str, question: str, options: str = "", threshold: float = 0.9, 
             always_system2: bool = False, thinking: bool = True, max_tokens: int = 1024):
    """
    Confidence-gated decision: System 1 answers fast; System 2 reasons if unsure.
    
    Returns: (system1_answer, system2_answer, reasoning, markdown, code)
    """
    result = client.predict(
        state=state,
        question=question,
        options_text=options,
        threshold=threshold,
        always_system2=always_system2,
        thinking=thinking,
        max_new_tokens=max_tokens,
        api_name="/escalate"
    )
    # Returns: (html_sys1, markdown_1, html_sys2, markdown_reasoning, code)
    return result

if __name__ == "__main__":
    # Example usage
    # Set HF_TOKEN env var first
    
    # Simple decision
    result = decide(
        "Our Q3 revenue dropped 15% but user engagement increased 23%",
        [
            {"type": "choice", "instructions": "Is this a crisis?", "options": "yes,no,unclear"},
            {"type": "score", "instructions": "Urgency 1-10", "options": ""},
            {"type": "noul", "instructions": "", "options": ""},
            {"type": "noul", "instructions": "", "options": ""},
        ]
    )
    print("Decide result:", result)
    
    # Escalated decision
    sys1, sys2, reasoning = escalate(
        state="Should we acquire competitor X for $50M?",
        question="Is this a good strategic move?",
        options="yes,no",
        threshold=0.85
    )
    print("System 1:", sys1)
    print("System 2:", sys2)
    print("Reasoning:", reasoning)