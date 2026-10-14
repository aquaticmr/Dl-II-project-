from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import pandas as pd

@dataclass
class WorkflowState:
    """
    Central shared state passed between agents in the AutoPrep AI workflow.
    """
    original_df: pd.DataFrame
    working_df: pd.DataFrame
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Inspection results
    profile_data: Dict[str, Any] = field(default_factory=dict)
    detected_issues: List[str] = field(default_factory=list)
    
    # Preprocessing plans & logs
    planned_steps: List[str] = field(default_factory=list)
    agent_results: Dict[str, Any] = field(default_factory=dict)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Validation
    validation_result: Dict[str, Any] = field(default_factory=dict)
    validation_status: str = "PENDING"
    retry_count: int = 0
    max_retries: int = 2
    
    # Final artifacts
    final_df: Optional[pd.DataFrame] = None
    final_report: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def log_transformation(self, agent_name: str, action: str, details: Dict[str, Any]):
        """Append an entry to the audit trail."""
        self.audit_log.append({
            "step": len(self.audit_log) + 1,
            "agent": agent_name,
            "action": action,
            "details": details
        })
