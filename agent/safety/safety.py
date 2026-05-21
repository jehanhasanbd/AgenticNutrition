from typing import Dict, Any, List

HIGH_RISK_SIGNS = [
    "insulin overdose",
    "stop taking medication",
    "replace your doctor",
    "cure diabetes",
    "miracle cure",
    "no need dialysis",
]

def basic_safety_scan(text: str) -> Dict[str, Any]:
    """
    Lightweight safety scan for harmful medical directions.
    """
    text_lower = text.lower()
    hints = [word for word in HIGH_RISK_SIGNS if word in text_lower]
    return {"ok": len(hints)==0 , "hits": hints}


def medical_disclaimer() -> str:
    return (
        "⚠️ **Medical note:** I can provide nutrition education and meal-planning support, "
        "but this doesn’t replace professional medical advice. If you have urgent symptoms "
        "or complex conditions (pregnancy, severe kidney disease, insulin adjustments, etc.), "
        "please consult a clinician/dietitian."
    )

def enforce_dietary_constraints(plan_text: str, hard_constraints: List[str]) -> Dict[str, Any]:
    """
        Simple constraint check: ensures forbidden items are not suggested.
        hard_constraints examples: ["no grapefruit", "low potassium", "no alcohol"]
    """
    plan_text_lower = plan_text.lower()
    violated = []
    for c in hard_constraints:
        # naive mapping: treat constraint keyword(s) as must-not-appear
        tokens = [tok.strip() for tok in c.replace("no","").split(",")]
        for tok in tokens:
            if tok and tok in plan_text_lower and c.lower().startswith("no "):
                violated.append(c)
                break
    return {"ok": len(violated) == 0, "violated": violated}