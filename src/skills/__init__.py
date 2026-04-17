"""
src.skills package – loads each skill module from its canonical location under
the top-level ``skills/<skill-name>/scripts/`` folder so that existing imports
(e.g. ``from src.skills import skill_casting_check``) continue to work.
"""

import importlib.util
import pathlib
import sys

_SKILLS_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent / "skills"

_SKILL_MAP = {
    "skill_casting_check": "casting-check",
    "skill_fraud_detection": "fraud-detection",
    "skill_auto_mapping": "auto-mapping",
    "skill_cross_reference_check": "cross-reference-check",
    "skill_ocr_extraction": "ocr-extraction",
    "skill_llm_contract_parser": "llm-contract-parser",
    "skill_rag_legal_search": "rag-legal-search",
    "skill_analytical_review": "analytical-review",
    "skill_wp_generator": "wp-generator",
}


def _load(module_name: str, folder: str):
    """Load a skill script and register it under the src.skills namespace."""
    full_name = f"src.skills.{module_name}"
    if full_name in sys.modules:
        return sys.modules[full_name]
    script = _SKILLS_ROOT / folder / "scripts" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(full_name, script)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module


# Eagerly load every skill so ``from src.skills import skill_X`` works.
for _name, _folder in _SKILL_MAP.items():
    globals()[_name] = _load(_name, _folder)
