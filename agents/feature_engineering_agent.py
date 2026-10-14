from orchestrator.state import WorkflowState
from tools.feature_engineering import treat_outliers_iqr, encode_categorical_features, scale_numerical_features
from typing import Dict, Any

class FeatureEngineeringAgent:
    """
    Agent 4: Feature Engineering Agent
    Executes outlier treatment, categorical variable encoding, and numerical scaling.
    """
    def __init__(self, name: str = "Feature Engineering Agent"):
        self.name = name

    def execute(self, state: WorkflowState) -> WorkflowState:
        try:
            df = state.working_df.copy()
            target_col = state.config.get("target_column")
            actions = []

            # 1. Outlier treatment
            outlier_strat = state.config.get("treat_outliers", "none")
            if outlier_strat == "cap":
                df, out_res = treat_outliers_iqr(df, method="cap", exclude_columns=[target_col] if target_col else [])
                capped_cols = list(out_res.get("outlier_summary", {}).keys())
                if capped_cols:
                    actions.append(f"Capped outliers using IQR for columns: {capped_cols}")
                    state.log_transformation(self.name, "treat_outliers_iqr", out_res)

            # 2. Categorical encoding
            enc_type = state.config.get("encode_categorical", "none")
            if enc_type != "none":
                df, enc_res = encode_categorical_features(
                    df,
                    encoding_type=enc_type,
                    target_column=target_col
                )
                encoded_cols = [d["column"] for d in enc_res.get("details", []) if "encoded" in d.get("action", "")]
                if encoded_cols:
                    actions.append(f"Encoded {len(encoded_cols)} categorical columns ({enc_type})")
                    state.log_transformation(self.name, "encode_categorical", enc_res)

            # 3. Numerical scaling
            scale_type = state.config.get("scale_numerical", "none")
            if scale_type != "none":
                df, scale_res = scale_numerical_features(
                    df,
                    scaler_type=scale_type,
                    exclude_columns=[target_col] if target_col else []
                )
                scaled_cols = scale_res.get("scaled_columns", [])
                if scaled_cols:
                    actions.append(f"Scaled {len(scaled_cols)} numerical features using {scale_type}")
                    state.log_transformation(self.name, "scale_numerical", scale_res)

            state.working_df = df
            state.agent_results["feature_engineering"] = {
                "status": "SUCCESS",
                "summary": "; ".join(actions) if actions else "Feature engineering skipped or no transformations configured.",
                "actions": actions
            }
        except Exception as e:
            state.errors.append(f"FeatureEngineeringAgent error: {str(e)}")
            state.agent_results["feature_engineering"] = {"status": "FAILED", "error": str(e)}

        return state
