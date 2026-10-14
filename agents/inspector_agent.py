from orchestrator.state import WorkflowState
from tools.profiling import profile_dataset
from typing import Dict, Any

class InspectorAgent:
    """
    Agent 1: Data Inspector Agent
    Inspects structure, counts missing values, identifies duplicate records, 
    detects anomalies, potential ID columns, and builds the initial profile.
    """
    def __init__(self, name: str = "Data Inspector Agent"):
        self.name = name

    def execute(self, state: WorkflowState) -> WorkflowState:
        try:
            profile = profile_dataset(state.working_df)
            state.profile_data = profile
            state.detected_issues = profile.get("issues", [])
            
            # Formulate preliminary transformation plan based on findings
            planned = []
            if profile.get("duplicate_rows", 0) > 0 and state.config.get("remove_duplicates", True):
                planned.append("Remove Duplicate Rows")
            if state.config.get("standardize_strings", True):
                planned.append("Standardize Casing & Trim Whitespace")
            if profile.get("total_missing", 0) > 0:
                planned.append("Impute Missing Numerical & Categorical Values")
            if state.config.get("treat_outliers", "none") != "none":
                planned.append("Treat Outliers using IQR Capping")
            if state.config.get("encode_categorical", "none") != "none":
                planned.append("Encode Categorical Variables")
            if state.config.get("scale_numerical", "none") != "none":
                planned.append("Scale Numerical Features")
                
            state.planned_steps = planned
            state.agent_results["inspector"] = {
                "status": "SUCCESS",
                "summary": f"Inspected {profile['num_rows']} rows, {profile['num_columns']} columns. Found {len(state.detected_issues)} quality issues.",
                "quality_score": profile.get("quality_score"),
                "detected_issues": state.detected_issues
            }
            state.log_transformation(self.name, "inspect_dataset", {
                "rows": profile["num_rows"],
                "columns": profile["num_columns"],
                "issues_count": len(state.detected_issues),
                "initial_score": profile.get("quality_score")
            })
        except Exception as e:
            state.errors.append(f"InspectorAgent error: {str(e)}")
            state.agent_results["inspector"] = {"status": "FAILED", "error": str(e)}
            
        return state
