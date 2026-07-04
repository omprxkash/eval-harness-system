from __future__ import annotations
import json
import re
import os
from langchain_core.messages import HumanMessage, SystemMessage


def _get_llm():
    provider = os.getenv("ACTIVE_LLM_PROVIDER", "gemini")
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                          temperature=0.0, openai_api_key=os.getenv("OPENAI_API_KEY", ""))
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
                                  temperature=0.0,
                                  google_api_key=os.getenv("GEMINI_API_KEY", ""))


CRITERIA = [
    {
        "name": "answer_relevance",
        "description": "Does the final output directly address the stated goal?",
    },
    {
        "name": "completeness",
        "description": "Does the output cover all aspects of the goal without missing key parts?",
    },
    {
        "name": "groundedness",
        "description": "Is the output supported by the information gathered in the trace steps? Does it avoid fabricating facts not present in the trace?",
    },
    {
        "name": "conciseness",
        "description": "Is the output appropriately concise — not padded with irrelevant information?",
    },
]


def evaluate_with_geval(goal: str, final_output: str, trace: list[dict]) -> dict:
    """
    Score the agent output on 4 criteria using LLM-as-judge (G-Eval pattern).
    Each criterion scored 0.0–1.0. Returns per-criterion scores + weighted average.
    """
    trace_summary = "\n".join(
        f"Step {i+1} ({s.get('step', '?')}): {str(s.get('output', ''))[:300]}"
        for i, s in enumerate(trace)
    )

    scores = {}
    for criterion in CRITERIA:
        prompt = [
            SystemMessage(content=(
                "You are an objective evaluator of AI agent outputs. "
                "Rate the output on a single criterion. "
                "Return only a JSON object with keys 'score' (float 0.0–1.0) and 'reason' (one sentence)."
            )),
            HumanMessage(content=f"""Goal: {goal}

Trace summary:
{trace_summary}

Final output:
{final_output}

Criterion: {criterion['name']}
Definition: {criterion['description']}

Return JSON: {{"score": 0.0–1.0, "reason": "one sentence"}}"""),
        ]
        try:
            llm = _get_llm()
            resp = llm.invoke(prompt)
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", resp.content.strip(), flags=re.MULTILINE)
            parsed = json.loads(raw)
            scores[criterion["name"]] = {
                "score": float(parsed.get("score", 0.0)),
                "reason": parsed.get("reason", ""),
            }
        except Exception:
            scores[criterion["name"]] = {"score": 0.0, "reason": "evaluation failed"}

    weights = {"answer_relevance": 0.35, "completeness": 0.25, "groundedness": 0.25, "conciseness": 0.15}
    weighted = sum(scores[c["name"]]["score"] * weights[c["name"]] for c in CRITERIA)

    return {
        "geval_scores": scores,
        "geval_weighted": round(weighted, 4),
    }
