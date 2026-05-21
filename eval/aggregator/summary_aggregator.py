from typing import Any, List, Dict,Optional

def avg(values: List[Optional[float]]) -> Optional[float]:
    vals = [v for v in values if isinstance(v, (int,float))]
    if not vals:
        return None
    return round(sum(vals) / len(vals), 4)
def aggregate(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    latency_ms = [r["latency_ms"] for r in results]

    structure = [r["metrics"]["structure"]["score"] for r in results]
    constraints = [r["metrics"]["constraints"]["score"] for r in results]
    safety_rules = [r["metrics"]["safety_rules"]["score"] for r in results]
    tool_usage = [r["metrics"]["tool_usage"]["score"] for r in results]
    strict_tool = [r["metrics"]["strict_tool"]["score"] for r in results]

    # llm-judge
    grounding = [
        r["metrics"]["llm_judge"].get("grounding", {}) for r in results
    ]
    safety = [
        r["metrics"]["llm_judge"].get("safety", {}) for r in results
    ]
    personalization = [
        r["metrics"]["llm_judge"].get("personalization", {}) for r in results
    ]

    # retrieval
    precision_at_k = [
        r["metrics"]["retrieval"].get("precision_at_k", {}) for r in results
    ]
    recall_at_k = [
        r["metrics"]["retrieval"].get("recall_at_k", {}) for r in results
    ]
    keyword_recall = [
        r["metrics"]["retrieval"].get("keyword_recall", {}) for r in results
    ]

    return {
        "n": len(results),
        "avg_latency_ms": round(sum(latency_ms) / max(1, len(latency_ms)), 2),
        "avg_structure": avg(structure),
        "avg_constraint_adherence": avg(constraints),
        "avg_safety_rules": avg(safety_rules),
        "avg_tool_usage": avg(tool_usage),
        "avg_strict_tool_usage": avg(strict_tool),
        "avg_precision_at_k": avg(precision_at_k),
        "avg_recall_at_k": avg(recall_at_k),
        "avg_keyword_recall": avg(keyword_recall),
        "avg_grounding_llm": avg(grounding),
        "avg_safety_llm": avg(safety),
        "avg_personalization_llm": avg(personalization),
    }
