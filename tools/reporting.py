import json
import pandas as pd
from typing import Dict, Any

def generate_quality_report(
    profile_before: Dict[str, Any],
    validation_after: Dict[str, Any],
    audit_log: list,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assembles a full audit report comparing before and after quality metrics.
    """
    return {
        "title": "AutoPrep AI - Data Preparation & Quality Audit Report",
        "configuration": config,
        "before_metrics": {
            "num_rows": profile_before.get("num_rows"),
            "num_columns": profile_before.get("num_columns"),
            "total_missing": profile_before.get("total_missing"),
            "duplicate_rows": profile_before.get("duplicate_rows"),
            "quality_score": profile_before.get("quality_score"),
            "issues_detected": profile_before.get("issues", [])
        },
        "after_metrics": {
            "num_rows": validation_after.get("num_rows"),
            "num_columns": validation_after.get("num_columns"),
            "remaining_missing": validation_after.get("remaining_missing"),
            "remaining_duplicates": validation_after.get("remaining_duplicates"),
            "quality_score": validation_after.get("score"),
            "status": validation_after.get("status"),
            "warnings": validation_after.get("warnings", []),
            "unresolved_issues": validation_after.get("issues", [])
        },
        "score_improvement": round(
            float(validation_after.get("score", 0.0)) - float(profile_before.get("quality_score", 0.0)), 1
        ),
        "audit_trail": audit_log
    }

def export_report_to_json(report_data: Dict[str, Any]) -> str:
    """Serializes report to formatted JSON string."""
    return json.dumps(report_data, indent=2, default=str)
