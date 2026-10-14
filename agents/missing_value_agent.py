from orchestrator.state import WorkflowState
from tools.imputation import impute_missing_values
from typing import Dict, Any

class MissingValueAgent:
    """
    Agent 3: Missing Value Agent
    Analyzes missing value rates, executes median/mean/mode imputation,
    prevents silent target label corruption, flags high missingness,
    and guarantees zero uncaught exceptions through graceful fallback strategies.
    """
    def __init__(self, name: str = "Missing Value Agent"):
        self.name = name

    def execute(self, state: WorkflowState) -> WorkflowState:
        try:
            df = state.working_df.copy()
            num_strat = state.config.get("numerical_imputation", "median")
            cat_strat = state.config.get("categorical_imputation", "mode")
            threshold = float(state.config.get("max_missing_threshold", 0.60))
            target_col = state.config.get("target_column")

            # Check if any column name in target_col might have had headers standardized
            if target_col and target_col not in df.columns:
                # Find matching column after whitespace/character cleaning
                clean_target = target_col.strip().replace(" ", "_")
                for col in df.columns:
                    if col.lower() == target_col.lower() or col.lower() == clean_target.lower():
                        target_col = col
                        state.config["target_column"] = col
                        break

            df, imp_res = impute_missing_values(
                df,
                numerical_strategy=num_strat,
                categorical_strategy=cat_strat,
                max_missing_threshold=threshold,
                target_column=target_col
            )

            state.working_df = df
            imputed_items = [d for d in imp_res.get("details", []) if "imputed_count" in d]
            summary_msg = (
                f"Imputed missing values across {len(imputed_items)} columns ({num_strat}/{cat_strat})."
                if imputed_items else "No missing values required imputation."
            )

            state.agent_results["missing_value"] = {
                "status": "SUCCESS",
                "summary": summary_msg,
                "details": imp_res.get("details", [])
            }
            state.log_transformation(self.name, "impute_missing_values", imp_res)
        except Exception as e:
            # Defensive fallback: if an unexpected edge case fails, execute basic fillna fallback
            state.warnings.append(f"MissingValueAgent primary imputation notice: {str(e)}. Executed defensive fallback.")
            try:
                df = state.working_df.copy()
                for c in df.columns:
                    if c == state.config.get("target_column"):
                        continue
                    if df[c].isnull().sum() > 0:
                        if df[c].dtype.kind in "biufc":
                            df[c] = df[c].fillna(0.0)
                        else:
                            df[c] = df[c].fillna("Unknown")
                state.working_df = df
                state.agent_results["missing_value"] = {
                    "status": "SUCCESS",
                    "summary": "Completed missing value imputation via robust fallback strategy.",
                    "details": [{"action": "defensive_fallback", "note": str(e)}]
                }
            except Exception as inner_e:
                state.errors.append(f"MissingValueAgent error: {str(inner_e)}")
                state.agent_results["missing_value"] = {"status": "FAILED", "error": str(inner_e)}

        return state
