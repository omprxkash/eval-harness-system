import json
from typing import Optional
from app.core.config import settings

_TARGETS = {
    "hallucination": "system_prompt",
    "incomplete_plan": "retry_config",
    "wrong_tool": "tool_definition",
    "bad_arguments": "tool_definition",
    "off_topic": "system_prompt",
    "format_error": "system_prompt",
}

_PROMPTS = {
    "hallucination": (
        "The agent hallucinated facts not present in its retrieved context. "
        "Suggest a specific system prompt constraint that instructs the agent to only state facts "
        "it can cite from its retrieved sources. Be concrete and brief."
    ),
    "incomplete_plan": (
        "The agent failed to complete its plan — one or more steps timed out or errored. "
        "Suggest a retry strategy configuration (e.g. max retries, backoff, step timeout values) "
        "to make the plan more resilient. Be concrete and brief."
    ),
    "wrong_tool": (
        "The agent used the wrong tool for the task. "
        "Suggest a specific update to the tool definitions or tool selection instructions "
        "so the agent picks the correct tool for this type of goal. Be concrete and brief."
    ),
    "bad_arguments": (
        "The agent called a tool with incorrect arguments. "
        "Suggest a specific improvement to the tool definition (parameter descriptions, examples, or types) "
        "to prevent this. Be concrete and brief."
    ),
    "off_topic": (
        "The agent's output was off-topic relative to the goal despite completing its steps successfully. "
        "Suggest a system prompt addition that keeps the agent focused on the goal. Be concrete and brief."
    ),
    "format_error": (
        "The agent produced output in the wrong format. "
        "Suggest a system prompt instruction that specifies the exact required output format. Be concrete and brief."
    ),
}


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


def generate_correction(failure_type: str, goal: str, trace: list[dict], final_output: str) -> Optional[dict]:
    if failure_type == "none":
        return None

    llm = _build_llm()
    failure_instruction = _PROMPTS.get(failure_type, _PROMPTS["format_error"])
    prompt = (
        f"Goal: {goal}\n\n"
        f"Final output: {final_output}\n\n"
        f"Failure type: {failure_type}\n\n"
        f"{failure_instruction}\n\n"
        "Respond with a single plain-text suggestion (2-4 sentences, no JSON, no markdown)."
    )
    response = llm.invoke(prompt)
    suggestion = response.content.strip()
    return {
        "type": failure_type,
        "suggestion": suggestion,
        "target": _TARGETS.get(failure_type, "system_prompt"),
    }
