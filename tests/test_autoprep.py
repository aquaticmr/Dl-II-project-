import pytest
import pandas as pd
import numpy as np
from tools.profiling import profile_dataset
from tools.cleaning import standardize_column_names, remove_duplicate_rows, normalize_strings_and_categories
from tools.imputation import impute_missing_values
from tools.feature_engineering import treat_outliers_iqr, encode_categorical_features, scale_numerical_features
from tools.validation import validate_dataset
from orchestrator.workflow import WorkflowOrchestrator
from ml.model_training import train_baseline_model

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Customer_ID": ["1", "2", "3", "3"],
        "Age": [25.0, np.nan, 29.0, 29.0],
        "Gender": ["Male", " female ", "Male", "Male"],
        "Income": [50000.0, 60000.0, 1000000.0, 1000000.0], # 1000000 outlier
        "Purchased": ["Yes", "No", "Yes", "Yes"]
    })

def test_profiling(sample_df):
    profile = profile_dataset(sample_df)
    assert profile["num_rows"] == 4
    assert profile["num_columns"] == 5
    assert profile["duplicate_rows"] == 1
    assert profile["total_missing"] == 1
    assert "Age" in profile["missing_values"]

def test_cleaning(sample_df):
    df_clean, dup_res = remove_duplicate_rows(sample_df)
    assert len(df_clean) == 3
    assert dup_res["rows_removed"] == 1

    df_norm, norm_res = normalize_strings_and_categories(df_clean, casing="title")
    assert "Female" in df_norm["Gender"].values

def test_imputation(sample_df):
    df_clean, _ = remove_duplicate_rows(sample_df)
    df_imp, imp_res = impute_missing_values(df_clean, numerical_strategy="median")
    assert df_imp["Age"].isnull().sum() == 0

def test_feature_engineering(sample_df):
    df_clean, _ = remove_duplicate_rows(sample_df)
    df_capped, out_res = treat_outliers_iqr(df_clean, method="cap")
    assert out_res["operation"] == "treat_outliers_iqr"

    df_enc, enc_res = encode_categorical_features(df_clean, encoding_type="onehot", target_column="Purchased")
    assert any("Gender" in col for col in df_enc.columns)

def test_validation(sample_df):
    val = validate_dataset(sample_df)
    assert val["status"] in ["PASS", "WARNING", "FAIL"]
    assert "score" in val

def test_orchestrator(sample_df):
    orchestrator = WorkflowOrchestrator(max_retries=2)
    config = {
        "remove_duplicates": True,
        "standardize_columns": True,
        "standardize_strings": True,
        "string_casing": "title",
        "numerical_imputation": "median",
        "categorical_imputation": "mode",
        "treat_outliers": "cap",
        "encode_categorical": "onehot",
        "scale_numerical": "standard",
        "target_column": "Purchased"
    }
    state = orchestrator.run(sample_df, config)
    assert state.final_df is not None
    assert len(state.final_df) == 3
    assert state.validation_status in ["PASS", "WARNING"]

def test_ml_baseline(sample_df):
    # Repeat rows to make >= 10 rows for ML pipeline test
    big_df = pd.concat([sample_df] * 4, ignore_index=True)
    res = train_baseline_model(
        df=big_df,
        target_column="Purchased",
        model_type="classification",
        algorithm="decision_tree"
    )
    assert res["status"] == "SUCCESS"
    assert "accuracy" in res["metrics"]
