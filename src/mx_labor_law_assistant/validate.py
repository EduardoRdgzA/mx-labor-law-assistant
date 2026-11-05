import re
from .config import observe

@observe(name="validation", as_type="guardrail")
def validate(answer: str, found: list[dict]) -> dict:
    """Etapa 1: Revisa que cada artículo citado esté entre los que dieron."""
    given = {(r["law"], r["article"].removeprefix("p. ")): r["article"] for r in found}
    laws = "|".join(re.escape(law) for law in {r["law"] for r in found})

    cited  = set()

    law_rx = re.compile(rf"\(({laws})\b([^)]*)\)")
    article_rx = re.compile(r"\d+(?:-[A-ZÑ])?(?: (?:Bis|Ter|Quáter))?")

    for law, rest in law_rx.findall(answer):
        for article in article_rx.findall(rest):
            cited.add((law, article))

    unknown = sorted(cited - given.keys())
    return {
        "cited": sorted((law, given.get((law, article), article)) for law, article in cited),
        "unknown": unknown,
        "valid": not unknown,
    }

if __name__ == "__main__":
    from rich import print

    found = [
        {"law": "LFT", "article": "76"},
        {"law": "LFT", "article": "77"},
        {"law": "LFT", "article": "81"},
    ]
    print(validate("Son 12 días (LFT, arts. 76 y 81).", found))
    print(validate("Son 12 días (LFT, art. 76) y también (LFT, art. 90).", found))    

