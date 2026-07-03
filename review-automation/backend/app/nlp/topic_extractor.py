import yake

_TAXONOMY = [
    "shipping",
    "pricing",
    "quality",
    "customer_service",
    "packaging",
    "returns",
    "usability",
    "performance",
    "reliability",
    "design",
    "value_for_money",
    "onboarding",
    "documentation",
    "features",
    "bugs",
]

_ALIASES = {
    "shipping": ["ship", "deliver", "delivery", "arrival", "courier", "transit", "dispatch"],
    "pricing": ["price", "pric", "cost", "expensive", "cheap", "afford", "fee", "charge", "paid"],
    "quality": ["quality", "build", "material", "craft", "durable", "durability", "broke", "sturdy"],
    "customer_service": [
        "customer service",
        "support",
        "rep",
        "agent",
        "staff",
        "team",
        "response",
        "help",
        "assist",
    ],
    "packaging": ["packag", "box", "wrap", "pack", "container", "packing"],
    "returns": ["return", "refund", "exchange", "money back", "send back", "replacement"],
    "usability": ["easy to use", "usab", "intuitive", "interface", "ui", "ux", "navigation", "setup"],
    "performance": ["fast", "slow", "speed", "lag", "performance", "quick", "responsive", "latency"],
    "reliability": ["reliable", "reliab", "crash", "fail", "broke", "stopped working", "unreliable", "consistent"],
    "design": ["design", "look", "aesthetic", "beautiful", "ugly", "color", "style", "sleek"],
    "value_for_money": ["value", "worth", "money", "bang for", "overpriced", "reasonable", "deal"],
    "onboarding": ["onboard", "getting started", "first time", "initial", "setup", "sign up", "register"],
    "documentation": ["document", "doc", "manual", "instruction", "guide", "readme", "tutorial", "how to"],
    "features": ["feature", "function", "capabilit", "option", "setting", "mode", "tool"],
    "bugs": ["bug", "glitch", "error", "issue", "problem", "defect", "broken", "not working", "wrong"],
}

_kw_extractor = yake.KeywordExtractor(lan="en", n=2, dedupLim=0.9, top=10)


def extract_topics(text: str) -> list[str]:
    keywords = _kw_extractor.extract_keywords(text)
    keyword_strings = [kw.lower() for kw, _ in keywords]
    full_text_lower = text.lower()

    matched = set()
    for topic in _TAXONOMY:
        aliases = _ALIASES.get(topic, [topic])
        for alias in aliases:
            if alias in full_text_lower:
                matched.add(topic)
                break
        if topic not in matched:
            for kw in keyword_strings:
                for alias in aliases:
                    if alias in kw or kw in alias:
                        matched.add(topic)
                        break

    return sorted(matched)


def topic_labels(topics: list[str]) -> list[str]:
    return [t.replace("_", " ").title() for t in topics]
