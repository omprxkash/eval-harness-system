from pathlib import Path
from jinja2 import Environment, FileSystemLoader

_TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=False)


def _pick_template(sentiment: str, topics: list[str]) -> str:
    if sentiment == "negative":
        return "negative_support.j2"
    if sentiment == "positive":
        return "positive.j2"
    return "neutral.j2"


def generate_response(
    sentiment: str,
    topics: list[str],
    author: str | None,
    brand_name: str = "Acme",
) -> str:
    template_name = _pick_template(sentiment, topics)
    template = _env.get_template(template_name)
    rendered = template.render(
        author=author or "there",
        brand_name=brand_name,
        topics=topics,
        sentiment=sentiment,
    )
    return rendered.strip()
