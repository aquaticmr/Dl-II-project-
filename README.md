# AutoPrep AI — Multi-Agent Intelligent Dataset Preparation System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4+-F7931E.svg)](https://scikit-learn.org/)

**AutoPrep AI** is an academic-grade, automated multi-agent framework designed to inspect, clean, impute, transform, and validate messy datasets for machine learning workflows.

---

## 🌟 Architecture Overview

AutoPrep AI organizes data preparation into five specialized, collaborative agents coordinated by a central workflow orchestrator:

1. 🔍 **Data Inspector Agent** (`agents/inspector_agent.py`):
   - Profiles dataset dimensions, data types, missing rates, and exact duplicate rows.
   - Detects constant columns, potential ID features, and numerical outliers using IQR.
2. 🧹 **Data Cleaning Agent** (`agents/cleaning_agent.py`):
   - Standardizes headers to clean snake_case.
   - Eliminates duplicate rows.
   - Trims whitespace and normalizes categorical casing.
3. 🧩 **Missing Value Agent** (`agents/missing_value_agent.py`):
   - Computes column missing percentages.
   - Executes median/mean numerical imputation and mode/unknown categorical imputation.
   - Preserves target variable integrity without silent corruption.
4. ⚙️ **Feature Engineering Agent** (`agents/feature_engineering_agent.py`):
   - Caps extreme numerical outliers.
   - Performs one-hot or label encoding on categorical variables.
   - Scales numeric attributes using StandardScaler or MinMaxScaler.
5. ✅ **Quality Validator Agent** (`agents/validator_agent.py`):
   - Verifies post-transformation integrity (nulls, duplicates, infinities).
   - Computes transparent 0–100 data quality score.
   - Issues **PASS**, **WARNING**, or **FAIL** decisions.
   - Initiates bounded correction attempts if needed.

---

## 🚀 Quickstart Guide

### 1. Setup Virtual Environment
```powershell
# Create virtual environment
py -3.12 -m venv .venv

# Activate in PowerShell
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run Automated Tests
```powershell
pytest -v
```

### 4. Launch the Web Application
```powershell
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
├── app.py                     # Main Streamlit web application
├── requirements.txt           # Project dependencies
├── README.md                  # System documentation
│
├── agents/                    # Specialized AI Agents
│   ├── inspector_agent.py
│   ├── cleaning_agent.py
│   ├── missing_value_agent.py
│   ├── feature_engineering_agent.py
│   └── validator_agent.py
│
├── orchestrator/              # Workflow Orchestration
│   ├── workflow.py            # 5-stage stateful execution engine
│   └── state.py               # Shared WorkflowState dataclass
│
├── tools/                     # Deterministic, safe tool implementations
│   ├── profiling.py
│   ├── cleaning.py
│   ├── imputation.py
│   ├── feature_engineering.py
│   ├── validation.py
│   └── reporting.py
│
├── ml/                        # Leakage-Safe Baseline ML Models
│   └── model_training.py
│
├── ui/                        # Presentation, charts & CSS styling
│   ├── components.py
│   └── charts.py
│
├── sample_data/               # Demonstration datasets
│   └── generate_sample.py
│
└── tests/                     # Pytest automated test suite
    └── test_autoprep.py
```

---

## 🔒 Data Leakage Prevention Guarantee
- Feature scaling, one-hot encoding, and imputation statistics in the baseline ML module are **strictly fitted on training splits only** via Scikit-Learn `Pipeline` and `ColumnTransformer`.
- Target column labels are never silently imputed.
