import pandas as pd
import numpy as np
from typing import Dict, Any, List

def validate_dataset(
    df: pd.DataFrame,
    initial_shape: tuple = (0, 0),
    target_column: str = None
) -> Dict[str, Any]:
    """
    Validates dataset quality post-processing:
    - Verifies null counts
    - Verifies duplicate rows
    - Checks infinite numbers or extreme NaNs
    - Computes before-and-after quality score
    - Emits PASS, WARNING, or FAIL status
    """
    if df is None or df.empty:
        return {
            "status": "FAIL",
            "score": 0.0,
            "issues": ["Dataset is empty or null."],
            "checks": {"non_empty": False}
        }
        
    num_rows, num_cols = df.shape
    total_missing = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    
    # Check infinite values in numeric columns
    num_cols_list = df.select_dtypes(include=[np.number]).columns
    inf_count = int(np.isinf(df[num_cols_list]).sum().sum()) if len(num_cols_list) > 0 else 0
    
    issues = []
    warnings = []
    
    if duplicate_rows > 0:
        warnings.append(f"{duplicate_rows} duplicate rows remain in dataset.")
        
    if total_missing > 0:
        missing_cols = df.isnull().sum()[df.isnull().sum() > 0].to_dict()
        if target_column and target_column in missing_cols:
            issues.append(f"Target column '{target_column}' contains {missing_cols[target_column]} missing values!")
        else:
            warnings.append(f"{total_missing} missing values still present in columns: {list(missing_cols.keys())}.")
            
    if inf_count > 0:
        issues.append(f"Found {inf_count} infinite values in numeric features.")
        
    # Check severe row shrinkage (e.g. lost > 80% of rows)
    if initial_shape[0] > 0 and num_rows < 0.2 * initial_shape[0]:
        warnings.append(f"Dataset row count dropped substantially from {initial_shape[0]} to {num_rows}.")

    # Status classification
    if issues:
        status = "FAIL"
    elif warnings:
        status = "WARNING"
    else:
        status = "PASS"
        
    # Recalculate transparent score (0-100)
    total_cells = max(num_rows * num_cols, 1)
    completeness = max(0.0, 100.0 - ((total_missing / total_cells) * 100 * 2))
    uniqueness = max(0.0, 100.0 - ((duplicate_rows / max(num_rows, 1)) * 100 * 2))
    validity = 100.0 if inf_count == 0 else max(0.0, 100.0 - (inf_count * 10))
    
    final_score = round((completeness * 0.5) + (uniqueness * 0.3) + (validity * 0.2), 1)
    
    return {
        "status": status,
        "score": final_score,
        "num_rows": num_rows,
        "num_columns": num_cols,
        "remaining_missing": total_missing,
        "remaining_duplicates": duplicate_rows,
        "infinite_values": inf_count,
        "issues": issues,
        "warnings": warnings,
        "component_scores": {
            "completeness": round(completeness, 1),
            "uniqueness": round(uniqueness, 1),
            "validity": round(validity, 1)
        }
    }
