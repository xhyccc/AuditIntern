"""
OpenCode CLI - Main orchestrator for the AI Audit System.
Reads a JSON instruction file and dispatches to appropriate skill scripts.

Usage:
    python -m src.cli.main --instruction /path/to/instruction.json
    or via stdin:
    echo '{"intent": "..."}' | python -m src.cli.main
"""

import argparse
import json
import sys

from src.skills import (
    skill_casting_check,
    skill_fraud_detection,
    skill_auto_mapping,
    skill_cross_reference_check,
    skill_ocr_extraction,
    skill_llm_contract_parser,
    skill_rag_legal_search,
    skill_analytical_review,
    skill_wp_generator,
)


def _run_casting_check(params: dict) -> dict:
    return skill_casting_check.run(
        file_path=params["file_path"],
        output_path=params.get("output_path", "casting_check_result.json"),
    )


def _run_fraud_scan(params: dict) -> dict:
    return skill_fraud_detection.run(
        file_path=params["file_path"],
        output_path=params.get("output_path", "fraud_detection_result.json"),
    )


def _run_auto_mapping(params: dict) -> dict:
    return skill_auto_mapping.run(
        tb_file=params["tb_file"],
        standard_coa_file=params["standard_coa_file"],
        output_path=params.get("output_path", "auto_mapping_result.json"),
    )


def _run_cross_reference(params: dict) -> dict:
    return skill_cross_reference_check.run(
        rules_file=params["rules_file"],
        data_files=params["data_files"],
        output_path=params.get("output_path", "cross_reference_result.json"),
    )


def _run_ocr(params: dict) -> dict:
    return skill_ocr_extraction.run(
        file_path=params["file_path"],
        output_path=params.get("output_path", "ocr_result.json"),
    )


def _run_contract_parse(params: dict) -> dict:
    return skill_llm_contract_parser.run(
        text=params["text"],
        output_path=params.get("output_path", "contract_parse_result.json"),
        api_key=params.get("api_key"),
    )


def _run_rag_search(params: dict) -> dict:
    return skill_rag_legal_search.run(
        query=params["query"],
        knowledge_base_path=params["knowledge_base_path"],
        output_path=params.get("output_path", "rag_search_result.json"),
    )


def _run_analytical_review(params: dict) -> dict:
    return skill_analytical_review.run(
        current_file=params["current_file"],
        prior_file=params["prior_file"],
        output_path=params.get("output_path", "analytical_review_result.json"),
        threshold_pct=params.get("threshold_pct", 15.0),
        threshold_amount=params.get("threshold_amount", 500000),
    )


def _run_wp_generate(params: dict) -> dict:
    return skill_wp_generator.run(
        template_path=params["template_path"],
        data_file=params["data_file"],
        output_path=params.get("output_path", "wp_output"),
    )


INTENT_MAP = {
    "run_casting_check": _run_casting_check,
    "run_fraud_scan": _run_fraud_scan,
    "run_auto_mapping": _run_auto_mapping,
    "run_cross_reference": _run_cross_reference,
    "run_ocr": _run_ocr,
    "run_contract_parse": _run_contract_parse,
    "run_rag_search": _run_rag_search,
    "run_analytical_review": _run_analytical_review,
    "run_wp_generate": _run_wp_generate,
}


def dispatch(instruction: dict) -> dict:
    intent = instruction.get("intent")
    if not intent:
        return {"status": "error", "message": "Missing 'intent' field in instruction"}

    handler = INTENT_MAP.get(intent)
    if handler is None:
        return {
            "status": "error",
            "message": f"Unknown intent: '{intent}'. Valid intents: {list(INTENT_MAP.keys())}",
        }

    params = instruction.get("params", {})
    print(f"[CLI] Dispatching intent: {intent}", file=sys.stderr)
    try:
        result = handler(params)
        print(f"[CLI] Completed intent: {intent}", file=sys.stderr)
        return result
    except KeyError as exc:
        return {"status": "error", "message": f"Missing required parameter: {exc}"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}


def main():
    parser = argparse.ArgumentParser(description="AI Audit System CLI Orchestrator")
    parser.add_argument("--instruction", help="Path to JSON instruction file")
    args = parser.parse_args()

    if args.instruction:
        with open(args.instruction, "r", encoding="utf-8") as fh:
            instruction = json.load(fh)
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print(
                json.dumps({"status": "error", "message": "No instruction provided"}),
                file=sys.stdout,
            )
            sys.exit(1)
        instruction = json.loads(raw)

    result = dispatch(instruction)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
