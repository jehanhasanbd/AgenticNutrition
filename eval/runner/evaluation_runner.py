import argparse
import json
from typing import List, Dict, Any

from eval.io import (
    read_jsonl,
    write_jsonl,
    write_json
)

from eval.aggregator.summary_aggregator import (
    aggregate
)

from eval.core.agent_runner import (
    run_agent_case
)

from eval.metrics.structural_metrics import (
    structure_score,
    constraint_adherence,
)
from eval.metrics.safety_metrics import (
    safety_rule_flags,
)
from eval.metrics.tool_metrics import (
    tool_usage_score,
    strict_tool_value_usage
)

from eval.metrics.retrieval_metrics import (
    precision_recall_at_k,
    keyword_recall
)

from eval.judges.llm_judges import run_judges

def evaluate(
        cases: List[Dict[str,Any]],
        use_llm_judge: bool,
        judge_model: str
    ) -> List[Dict[str, Any]]:

    results: List[Dict[str, Any]]
    for case in cases:
        case_id = case.get("case_id", "unknown_case")
        user_message = str(case["user_message"])

        user_profile = case.get("user_profile", {}) or {}
        ehr_json = case.get("ehr_json", {}) or {}
        hard_constraints = case.get("hard_constraints", []) or []

        must_avoid = case.get("must_avoid", []) or []

        require_weather = bool(case.get("require_weather", True))
        require_prices = bool(case.get("require_prices", True))

        expected_relevant_ids = case.get("expected_relevant_ids", []) or []
        expected_keywords = case.get("expected_keywords", []) or []
        k = int(case.get("k", 6))

        agent_out = run_agent_case(
            user_message=user_message,
            user_profile=user_profile,
            ehr_json=ehr_json,
            hard_constraints=hard_constraints
        )

        answer = agent_out['answer']
        ehr_context = agent_out['ehr_context']
        tool_context = agent_out['tool_context']
        retrieved_ids = agent_out['retrieved_ids']

        m_structure = structure_score(answer)
        m_constraints = constraint_adherence(answer, must_avoid)
        m_safety = safety_rule_flags(answer)
        m_tool = tool_usage_score(
            answer=answer,
            require_weather=require_weather,
            require_prices=require_prices
        )
        m_strict_tool = strict_tool_value_usage(
            answer=answer,
            tool_context=tool_context
        )

        retrieval_metrics: Dict[str, Any] = {}
        pre_recall = precision_recall_at_k(
            retrieved_ids=retrieved_ids,
            expected_relevant_ids=expected_relevant_ids
        )
        retrieval_metrics['precision_at_k'] = pre_recall.get("precision")
        retrieval_metrics['recall_at_k'] = pre_recall.get("recall")

        kw_recall = keyword_recall(
            retrieved_ids=retrieved_ids,
            expected_relevant_ids=expected_relevant_ids
        )
        retrieval_metrics['keyword_recall'] = kw_recall.get("score")

        llm_scores: Dict[str, Any] = {}
        if use_llm_judge:
            llm_scores = run_judges(
                judge_model=judge_model,
                user_message=user_message,
                answer=answer,
                retrieved_context=ehr_context
            )
        results.append(
            {
                "case_id": case_id,
                "latency_ms": agent_out['latency_ms'],
                "metrics": {
                    "structure": m_structure,
                    "constraints": m_constraints,
                    "safety_rules": m_safety,
                    "tool_usage": m_tool,
                    "strict_tool": m_strict_tool,
                    "retrieval": retrieval_metrics,
                    "llm_judge": llm_scores,
                },
                "artifacts": {
                    "user_message": user_message,
                    "answer": answer,
                    "ehr_context": ehr_context,
                    "tool_context": tool_context,
                    "retrieved_ids": retrieved_ids,
                },
            }
        )
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=str,default="eval/test_file/test_cases.jsonl")
    parser.add_argument("--out", type=str,default="eval/test_file/results.jsonl")
    parser.add_argument("--summary_out", type=str,default="eval/test_file/summary.jsonl")
    parser.add_argument("--no_llm_judge",action="store_true")
    parser.add_argument("--judge_model", type=str,default="gpt-4o-mini")
    args = parser.parse_args()

    cases = read_jsonl(args.cases)

    results = evaluate(
        cases=cases,
        use_llm_judge=not args.no_llm_judge,
        judge_model=args.judge_model
    )

    write_jsonl(args.out, results)
    summary = aggregate(results)
    write_json(args.summary_out, summary)


    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
        main()
