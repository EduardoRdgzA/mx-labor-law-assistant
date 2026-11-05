import re
from .config import observe

@observe(name="validation", as_type="guardrail")
def validate(answer: str, ids: list[str]) -> dict:
    """Etapa 1: Revisa que cada id citado [F#] esté entre los fragmentos dados."""
    cited = set(re.findall(r"\[(F\d+)\]", answer))
    unknown = sorted(cited - set(ids))

    return {
        "cited": sorted(cited),
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

