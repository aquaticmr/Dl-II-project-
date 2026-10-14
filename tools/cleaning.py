import re
import pandas as pd
from typing import Tuple, Dict, Any, List

def standardize_column_names(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Standardizes column names by stripping spaces, replacing special characters
    with underscores, and ensuring clean snake_case or clean text.
    """
    df = df.copy()
    old_cols = list(df.columns)
    new_cols = []
    for c in old_cols:
        clean = str(c).strip()
        clean = re.sub(r"[^\w\s]", "", clean)
        clean = re.sub(r"\s+", "_", clean)
        new_cols.append(clean)
    
    mapping = dict(zip(old_cols, new_cols))
    df.columns = new_cols
    
    changed = {k: v for k, v in mapping.items() if k != v}
    return df, {
        "operation": "standardize_column_names",
        "changed_columns": changed,
        "count": len(changed)
    }

def remove_duplicate_rows(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Removes exact duplicate rows and records count.
    """
    initial_rows = len(df)
    df_clean = df.drop_duplicates().copy()
    removed = initial_rows - len(df_clean)
    return df_clean, {
        "operation": "remove_duplicates",
        "rows_removed": removed,
        "initial_rows": initial_rows,
        "final_rows": len(df_clean)
    }

def normalize_strings_and_categories(
    df: pd.DataFrame, 
    casing: str = "title"  # "title", "lower", "upper", or "trim_only"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Trims leading/trailing whitespace and normalizes string casing for object/category columns.
    Also handles empty strings as NaN.
    """
    df = df.copy()
    affected_cols = {}
    
    cat_cols = list(df.select_dtypes(include=["object", "string", "category"]).columns)
    for col in cat_cols:
        orig = df[col].copy()
        
        # Convert to string stripped or leave NaN
        def clean_val(v):
            if pd.isna(v) or v is None:
                return v
            s = str(v).strip()
            if s == "" or s.lower() in ["nan", "null", "none", "n/a", "?"]:
                return pd.NA
            if casing == "title":
                return s.title()
            elif casing == "lower":
                return s.lower()
            elif casing == "upper":
                return s.upper()
            return s

        df[col] = df[col].apply(clean_val)
        
        # Count differences
        diff_count = (orig.astype(str) != df[col].astype(str)).sum()
        if diff_count > 0:
            affected_cols[col] = int(diff_count)
            
    return df, {
        "operation": "normalize_strings",
        "casing_strategy": casing,
        "columns_modified": affected_cols,
        "total_columns_affected": len(affected_cols)
    }
