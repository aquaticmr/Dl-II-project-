from orchestrator.state import WorkflowState
from tools.cleaning import standardize_column_names, remove_duplicate_rows, normalize_strings_and_categories
from typing import Dict, Any

class CleaningAgent:
    """
    Agent 2: Data Cleaning Agent
    Standardizes column names, removes exact duplicates, normalizes whitespace and casing.
    """
    def __init__(self, name: str = "Data Cleaning Agent"):
        self.name = name

    def execute(self, state: WorkflowState) -> WorkflowState:
        try:
            df = state.working_df.copy()
            cleaned_actions = []

            # 1. Standardize column names if enabled
            if state.config.get("standardize_columns", True):
                df, col_res = standardize_column_names(df)
                if col_res["count"] > 0:
                    cleaned_actions.append(f"Standardized {col_res['count']} column headers")
                    state.log_transformation(self.name, "standardize_column_names", col_res)

            # 2. Remove duplicate rows if enabled
            if state.config.get("remove_duplicates", True):
                df, dup_res = remove_duplicate_rows(df)
                if dup_res["rows_removed"] > 0:
                    cleaned_actions.append(f"Removed {dup_res['rows_removed']} duplicate rows")
                    state.log_transformation(self.name, "remove_duplicates", dup_res)

            # 3. Normalize string casing & whitespace
            if state.config.get("standardize_strings", True):
                casing = state.config.get("string_casing", "title")
                df, norm_res = normalize_strings_and_categories(df, casing=casing)
                if norm_res["total_columns_affected"] > 0:
                    cleaned_actions.append(f"Normalized string values across {norm_res['total_columns_affected']} columns")
                    state.log_transformation(self.name, "normalize_strings", norm_res)

            state.working_df = df
            state.agent_results["cleaning"] = {
                "status": "SUCCESS",
                "summary": "; ".join(cleaned_actions) if cleaned_actions else "No cleaning transformations required.",
                "actions": cleaned_actions
            }
        except Exception as e:
            state.errors.append(f"CleaningAgent error: {str(e)}")
            state.agent_results["cleaning"] = {"status": "FAILED", "error": str(e)}

        return state
