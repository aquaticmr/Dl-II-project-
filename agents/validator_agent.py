from orchestrator.state import WorkflowState
from tools.validation import validate_dataset
from tools.reporting import generate_quality_report
from typing import Dict, Any

class ValidatorAgent:
    """
    Agent 5: Quality Validator Agent
    Independently inspects transformed dataset, evaluates nulls/duplicates/anomalies,
    computes final quality score, emits PASS/WARNING/FAIL decision, and generates report.
    """
    def __init__(self, name: str = "Quality Validator Agent"):
        self.name = name

    def execute(self, state: WorkflowState) -> WorkflowState:
        try:
            val_result = validate_dataset(
                df=state.working_df,
                initial_shape=state.original_df.shape,
                target_column=state.config.get("target_column")
            )
            state.validation_result = val_result
            state.validation_status = val_result.get("status", "FAIL")

            # Check if retry or correction is required
            if state.validation_status == "FAIL":
                state.warnings.extend(val_result.get("issues", []))
            
            # Generate quality comparison report
            report = generate_quality_report(
                profile_before=state.profile_data,
                validation_after=val_result,
                audit_log=state.audit_log,
                config=state.config
            )
            state.final_report = report
            state.final_df = state.working_df.copy()

            state.agent_results["validator"] = {
                "status": "SUCCESS",
                "validation_status": state.validation_status,
                "score": val_result.get("score"),
                "summary": f"Validation completed with status {state.validation_status}. Quality score: {val_result.get('score')}/100.",
                "issues": val_result.get("issues", []),
                "warnings": val_result.get("warnings", [])
            }
            state.log_transformation(self.name, "validate_dataset", {
                "status": state.validation_status,
                "score": val_result.get("score"),
                "remaining_missing": val_result.get("remaining_missing"),
                "remaining_duplicates": val_result.get("remaining_duplicates")
            })
        except Exception as e:
            state.errors.append(f"ValidatorAgent error: {str(e)}")
            state.agent_results["validator"] = {"status": "FAILED", "error": str(e)}

        return state
