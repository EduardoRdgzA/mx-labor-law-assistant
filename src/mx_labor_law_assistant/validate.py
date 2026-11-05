import re
from .config import observe

@observe(name="validation", as_type="guardrail")
def validate(answer: str, labels: dict) -> dict:
    """Etapa 1: Revisa que cada fragmento citado [F#] esté entre los que se dieron."""
    cited = sorted(set(re.findall(r"\[(F\d+)\]", answer)))
    unknown = [fid for fid in cited if fid not in labels]

    return {
        "cited": {f"Fragmento {fid[1:]}": labels[fid] for fid in cited if fid in labels},
        "not_cited": {f"Fragmento {fid[1:]}": label for fid, label in labels.items() if fid not in cited},
        "unknown": [f"Fragmento {fid[1:]}" for fid in unknown],
        "valid": not unknown,
    }


if __name__ == "__main__":
    from rich import print

    labels = {"F1": "LFT, art. 76", "F2": "LFT, art. 81", "F3": "contrato.pdf, p. 2"}
    print(validate("Son 12 días de vacaciones. [F1][F3]", labels))
    print(validate("Son 12 días [F1] y también [F7].", labels))   

