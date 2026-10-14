import os
import pandas as pd
import numpy as np

def generate_sample_dataset(output_path: str = "sample_data/sample_dataset.csv") -> str:
    """
    Generates a synthetic dataset with deliberate data-quality issues:
    - Missing numerical & categorical values
    - Duplicate rows
    - Inconsistent casing and leading/trailing whitespace
    - Outliers in numerical features
    - Target column for classification/regression demonstration
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data = {
        "Customer_ID": [
            "CUST_001", "CUST_002", "CUST_003", "CUST_004", "CUST_005",
            "CUST_006", "CUST_007", "CUST_008", "CUST_009", "CUST_010",
            "CUST_003", "CUST_011", "CUST_012", "CUST_013", "CUST_014",
            "CUST_015", "CUST_016", "CUST_017", "CUST_018", "CUST_019",
            "CUST_020", "CUST_021", "CUST_022", "CUST_023", "CUST_024"
        ],
        "Age": [
            25, 34, np.nan, 45, 29,
            52, 19, 41, np.nan, 38,
            np.nan, 61, 23, 145, 31,  # 145 is a clear outlier
            28, np.nan, 50, 36, 42,
            27, 33, 48, np.nan, 30
        ],
        "Gender": [
            "Male", "Female", "female", " MALE ", "Female",
            "male", "FEMALE", "Male", np.nan, "female",
            "female", "Male", " Female ", "Male", "male",
            np.nan, "Male", "Female", "male", "Female",
            "Male", "female", "Male", "Female", "male"
        ],
        "Annual_Income": [
            45000, 68000, 52000, 89000, np.nan,
            110000, 32000, 74000, 61000, 58000,
            52000, 95000, 41000, 550000, 49000, # 550000 is an outlier
            np.nan, 67000, 82000, 53000, 71000,
            46000, 64000, 88000, 39000, 51000
        ],
        "Education_Level": [
            "Bachelor", "Master", "bachelor", "PhD", "High School",
            "Master", "Bachelor", "master", np.nan, "Bachelor",
            "bachelor", "PhD", "High School", "Master", "Bachelor",
            "Bachelor", "Master", "PhD", "High School", "Bachelor",
            "Master", "Bachelor", "High School", "Master", "Bachelor"
        ],
        "Credit_Score": [
            710, 680, 590, 750, 620,
            810, 560, 730, np.nan, 640,
            590, 790, 600, 720, 670,
            630, 705, 780, 595, 715,
            640, 690, 760, 580, 665
        ],
        "Purchased": [
            "Yes", "No", "Yes", "Yes", "No",
            "Yes", "No", "Yes", "No", "No",
            "Yes", "Yes", "No", "Yes", "No",
            "No", "Yes", "Yes", "No", "Yes",
            "No", "No", "Yes", "No", "Yes"
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    return output_path

if __name__ == "__main__":
    generate_sample_dataset()
    print("Sample dataset created successfully.")
