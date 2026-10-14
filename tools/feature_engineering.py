import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def treat_outliers_iqr(
    df: pd.DataFrame,
    method: str = "cap", # "cap", "none"
    factor: float = 1.5,
    exclude_columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Detects and optionally caps outliers using the IQR method.
    """
    df = df.copy()
    exclude = exclude_columns or []
    outlier_summary = {}
    
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]
    for col in num_cols:
        series = df[col].dropna()
        if len(series) < 4:
            continue
        q25 = float(series.quantile(0.25))
        q75 = float(series.quantile(0.75))
        iqr = q75 - q25
        lower = q25 - (factor * iqr)
        upper = q75 + (factor * iqr)
        
        outliers_mask = (df[col] < lower) | (df[col] > upper)
        count = int(outliers_mask.sum())
        
        if count > 0:
            outlier_summary[col] = {
                "count": count,
                "lower_bound": round(lower, 2),
                "upper_bound": round(upper, 2),
                "action_taken": method
            }
            if method == "cap":
                df[col] = df[col].clip(lower=lower, upper=upper)
                
    return df, {
        "operation": "treat_outliers_iqr",
        "method": method,
        "outlier_summary": outlier_summary
    }

def encode_categorical_features(
    df: pd.DataFrame,
    encoding_type: str = "onehot", # "onehot", "label", "none"
    max_cardinality: int = 15,
    target_column: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Encodes categorical features. Avoids encoding target column or high-cardinality ID columns.
    """
    df = df.copy()
    if encoding_type == "none":
        return df, {"operation": "encode_categorical", "type": "none", "encoded_columns": []}

    cat_cols = [c for c in df.select_dtypes(include=["object", "category"]).columns if c != target_column]
    encoded_info = []
    
    for col in cat_cols:
        unique_cnt = df[col].nunique()
        if unique_cnt > max_cardinality:
            encoded_info.append({
                "column": col,
                "action": "skipped_high_cardinality",
                "unique_values": unique_cnt
            })
            continue

        if encoding_type == "onehot":
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True, dtype=int)
            df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
            encoded_info.append({
                "column": col,
                "action": "onehot_encoded",
                "new_columns": list(dummies.columns)
            })
        elif encoding_type == "label":
            labels, uniques = pd.factorize(df[col])
            df[col] = labels
            encoded_info.append({
                "column": col,
                "action": "label_encoded",
                "classes": list(uniques)
            })
            
    return df, {
        "operation": "encode_categorical",
        "type": encoding_type,
        "details": encoded_info
    }

def scale_numerical_features(
    df: pd.DataFrame,
    scaler_type: str = "standard", # "standard", "minmax", "none"
    exclude_columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Scales numerical features using StandardScaler or MinMaxScaler.
    """
    df = df.copy()
    if scaler_type == "none":
        return df, {"operation": "scale_numerical", "type": "none", "scaled_columns": []}

    exclude = exclude_columns or []
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]
    
    if not num_cols:
        return df, {"operation": "scale_numerical", "type": scaler_type, "scaled_columns": []}

    scaler = StandardScaler() if scaler_type == "standard" else MinMaxScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])
    
    return df, {
        "operation": "scale_numerical",
        "type": scaler_type,
        "scaled_columns": num_cols
    }
