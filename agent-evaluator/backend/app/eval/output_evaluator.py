import json
from app.core.config import settings


def _build_llm():
    if settings.ACTIVE_LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.JUDGE_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
        )
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=settings.JUDGE_TEMPERATURE,
        google_api_key=settings.GEMINI_API_KEY,
    )


def evaluate_output(goal: str, final_output: str, trace: list[dict]) -> dict:
    llm = _build_llm()
    prompt = (
        f"Goal: {goal}\n\n"
        f"Final output: {final_output}\n\n"
        "Rate the following on a scale from 0.0 to 1.0:\n"
        "1. task_completion: how well the final output accomplishes the goal\n"
        "2. hallucination_detected: true if the output contains fabricated facts not supported by any step in the trace, false otherwise\n\n"
        f"Trace summary (step names and statuses): {json.dumps([{'step': s.get('step'), 'status': s.get('status')} for s in trace])}\n\n"
        'Respond ONLY with valid JSON in this exact format: {"task_completion_score": <float>, "hallucination_detected": <bool>}'
    )
    response = llm.invoke(prompt)
    text = response.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    parsed = json.loads(text)
    return {
        "task_completion_score": float(parsed["task_completion_score"]),
        "hallucination_detected": bool(parsed["hallucination_detected"]),
    }
