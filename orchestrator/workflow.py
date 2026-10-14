import pandas as pd
from typing import Dict, Any, Callable, Optional
from orchestrator.state import WorkflowState
from agents.inspector_agent import InspectorAgent
from agents.cleaning_agent import CleaningAgent
from agents.missing_value_agent import MissingValueAgent
from agents.feature_engineering_agent import FeatureEngineeringAgent
from agents.validator_agent import ValidatorAgent

class WorkflowOrchestrator:
    """
    Central Orchestrator coordinating the 5-agent stateful workflow:
    1. Inspector Agent
    2. Cleaning Agent
    3. Missing Value Agent
    4. Feature Engineering Agent
    5. Quality Validator Agent
    Includes conditional recovery retry loops (up to max_retries).
    """
    def __init__(self, max_retries: int = 2):
        self.inspector = InspectorAgent()
        self.cleaner = CleaningAgent()
        self.imputer = MissingValueAgent()
        self.feature_engineer = FeatureEngineeringAgent()
        self.validator = ValidatorAgent()
        self.max_retries = max_retries

    def run(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any],
        step_callback: Optional[Callable[[str, str, Dict[str, Any]], None]] = None
    ) -> WorkflowState:
        """
        Runs the multi-agent pipeline with execution logging and conditional verification.
        """
        # Initialize state with a pristine copy
        state = WorkflowState(
            original_df=df.copy(),
            working_df=df.copy(),
            config=config,
            max_retries=self.max_retries
        )

        def notify(agent_name: str, status: str, details: Dict[str, Any]):
            if step_callback:
                step_callback(agent_name, status, details)

        # Stage 1: Inspection
        notify("Data Inspector Agent", "RUNNING", {"msg": "Profiling dataset structure and quality issues..."})
        state = self.inspector.execute(state)
        notify("Data Inspector Agent", state.agent_results.get("inspector", {}).get("status", "SUCCESS"), state.agent_results.get("inspector", {}))

        # Stage 2: Cleaning
        notify("Data Cleaning Agent", "RUNNING", {"msg": "Executing duplicate checks and header/string normalization..."})
        state = self.cleaner.execute(state)
        notify("Data Cleaning Agent", state.agent_results.get("cleaning", {}).get("status", "SUCCESS"), state.agent_results.get("cleaning", {}))

        # Stage 3: Missing Value Handling
        notify("Missing Value Agent", "RUNNING", {"msg": "Evaluating missing values and executing imputation..."})
        state = self.imputer.execute(state)
        notify("Missing Value Agent", state.agent_results.get("missing_value", {}).get("status", "SUCCESS"), state.agent_results.get("missing_value", {}))

        # Stage 4: Feature Engineering
        notify("Feature Engineering Agent", "RUNNING", {"msg": "Executing outlier treatment, encoding, and scaling..."})
        state = self.feature_engineer.execute(state)
        notify("Feature Engineering Agent", state.agent_results.get("feature_engineering", {}).get("status", "SUCCESS"), state.agent_results.get("feature_engineering", {}))

        # Stage 5: Validation with conditional retry loop
        while state.retry_count <= self.max_retries:
            notify("Quality Validator Agent", "RUNNING", {"msg": f"Running verification checks (Attempt {state.retry_count + 1})..."})
            state = self.validator.execute(state)
            
            # If validation passed or only minor warnings remain, complete successfully
            if state.validation_status in ["PASS", "WARNING"]:
                notify("Quality Validator Agent", state.validation_status, state.agent_results.get("validator", {}))
                break
                
            # If critical FAIL and retries remain, attempt corrective re-imputation
            if state.retry_count < self.max_retries:
                state.retry_count += 1
                notify("Quality Validator Agent", "RETRYING", {
                    "msg": f"Validation failed with critical issue. Initiating recovery attempt {state.retry_count}..."
                })
                # Corrective action: enforce strict zero/unknown imputation fallback
                state.config["numerical_imputation"] = "median"
                state.config["categorical_imputation"] = "mode"
                state = self.imputer.execute(state)
            else:
                notify("Quality Validator Agent", "FAIL", {
                    "msg": "Max retries reached. Workflow completed with unresolved validation warnings.",
                    "details": state.validation_result
                })
                break

        return state
