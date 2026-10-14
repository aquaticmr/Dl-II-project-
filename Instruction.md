# MASTER PROJECT DEVELOPMENT PROMPT
# AutoPrep AI — Multi-Agent Intelligent Dataset Preparation System

## 1. YOUR ROLE

Act as a senior Python developer, AI/ML engineer, Agentic AI architect, and technical mentor.

Your task is to design and implement a complete, working, beginner-friendly academic project named:

**AutoPrep AI: A Multi-Agent Intelligent Framework for Automated Dataset Cleaning, Transformation, Validation, and Machine Learning Preparation**

Build a functional web application that allows users to upload raw datasets and automatically transform them into clean, validated, machine-learning-ready datasets using a coordinated multi-agent workflow.

The project is intended for a Computer Science Engineering student specializing in Artificial Intelligence and Machine Learning. Keep the implementation easy to understand, easy to demonstrate during an examination, technically correct, and sufficiently impressive for an academic project.

Do not merely create a UI mockup or a chatbot that describes how data could be cleaned. Implement real dataset-processing functionality using Python libraries.

---

## 2. PROJECT OVERVIEW

### Problem statement

Data preprocessing is an important but time-consuming stage of machine learning. Real-world datasets often contain missing values, duplicate records, inconsistent categorical values, incorrect data types, outliers, irrelevant columns, and other quality issues.

These problems must be identified and handled before training a machine-learning model.

Traditional preprocessing requires users to write separate scripts and manually decide which operations to perform. This can be difficult for beginners and repetitive for data analysts.

AutoPrep AI addresses this problem by using multiple specialized AI agents coordinated through an intelligent workflow.

### Proposed solution

The application should accept a CSV or Excel dataset, inspect its structure, identify data-quality issues, select suitable preprocessing operations, execute those operations through Python tools, validate the result, and generate a final dataset that can be used for machine-learning experiments.

The system must include five specialized agents:

1. Data Inspector Agent
2. Data Cleaning Agent
3. Missing Value Agent
4. Feature Engineering Agent
5. Quality Validator Agent

A central orchestrator coordinates the agents and controls the execution sequence.

The final application should provide:
- A dataset upload interface.
- Automatic dataset profiling.
- A multi-agent preprocessing workflow.
- A live execution log.
- Before-and-after data-quality comparisons.
- A cleaned dataset preview.
- A downloadable processed CSV file.
- A downloadable preprocessing report.
- An optional baseline machine-learning training module.
- A clear explanation of the transformations performed.

---

## 3. PROJECT OBJECTIVES

The main objectives are:

1. Automate common dataset-preprocessing operations.
2. Demonstrate Agentic AI through planning, tool usage, state management, conditional decisions, and validation.
3. Use specialized agents for different preprocessing responsibilities.
4. Apply actual data transformations rather than generating textual recommendations only.
5. Improve data quality while preserving valid observations.
6. Maintain an audit log of all transformations.
7. Provide an understandable interface for students and beginner data scientists.
8. Export datasets and preprocessing configurations for reproducible machine-learning experiments.
9. Prevent data leakage when preparing data for model training.
10. Demonstrate measurable results through before-and-after quality metrics.

---

## 4. TECHNOLOGY STACK

Use the following stack unless a genuine technical limitation requires a small adjustment.

### Programming language
- Python 3.12

### Frontend and application interface
- Streamlit

### Data processing
- Pandas
- NumPy
- OpenPyXL for Excel files

### Machine learning and preprocessing
- Scikit-learn

### Agent orchestration
- LangGraph for a stateful multi-agent workflow.

If LangGraph introduces unnecessary complexity or dependency problems, implement the same architecture using a modular Python orchestrator with explicit agent classes and conditional transitions. Keep the agents separate even if a framework is not used.

### Large language model
- Gemini API through a supported Python SDK, or another configurable LLM provider.
- Store API credentials in environment variables.
- Never hardcode API keys.
- The application must still perform deterministic preprocessing when the LLM API is unavailable.

### Visualization
- Plotly
- Streamlit charts

### Report generation
- Python standard libraries for JSON reports.
- ReportLab for optional PDF reports.

### Testing
- Pytest

### Version control
- Git and GitHub

Do not introduce Docker, Kubernetes, microservices, vector databases, or other unnecessary infrastructure in the initial version. Keep the application simple enough to run locally on Windows.

---

## 5. SYSTEM ARCHITECTURE

Implement the following logical architecture:

User
→ Streamlit Interface
→ Dataset Loader
→ Workflow Orchestrator
→ Data Inspector Agent
→ Data Cleaning Agent
→ Missing Value Agent
→ Feature Engineering Agent
→ Quality Validator Agent
→ Conditional correction or approval
→ Processed Dataset
→ Export and Optional Model Training

The orchestrator must maintain shared workflow state containing:
- Original dataset.
- Working dataset.
- Dataset metadata.
- Detected issues.
- User configuration.
- Planned transformations.
- Agent execution results.
- Transformation audit log.
- Validation results.
- Errors and warnings.
- Final dataset.
- Export information.

The original dataset must never be modified directly. Work on a copy and retain the original for comparison or reset.

The agents must communicate through structured Python data rather than relying entirely on natural-language messages.

Use clearly defined inputs and outputs for each agent.

---

## 6. AGENT 1 — DATA INSPECTOR AGENT

### Purpose

Understand the uploaded dataset and identify its structure, quality issues, and preprocessing requirements.

### Responsibilities

1. Read dataset dimensions.
2. Identify numerical, categorical, Boolean, datetime, and text columns.
3. Calculate missing-value counts and percentages.
4. Detect exact duplicate rows.
5. Identify constant and near-constant columns.
6. Detect suspicious numeric values and potential outliers.
7. Identify inconsistent categorical formatting.
8. Check for possible identifier columns.
9. Detect columns with excessive missingness.
10. Identify potential target columns if the user specifies a prediction task.
11. Generate a dataset-quality summary.

### Required outputs

Produce structured metadata such as:

- Number of rows.
- Number of columns.
- Column names and data types.
- Memory usage where available.
- Missing values per column.
- Duplicate-row count.
- Numeric-column summaries.
- Categorical-column summaries.
- Potential quality issues.
- Initial recommendations.

### Decision-making

The inspector should identify which problems require attention and pass its findings to the orchestrator.

For example:

If the `Age` column contains 18 missing values, the agent records the issue and recommends evaluating numerical imputation methods.

If the `Gender` column contains inconsistent capitalization, it flags a possible standardization task.

If a column contains unique values in nearly every row, it may be an identifier. Do not automatically delete it without sufficient evidence or user approval.

### Implementation

Use Pandas and NumPy for calculations.

The LLM may explain findings or suggest next steps, but actual counts, percentages, and statistical summaries must come from Python.

---

## 7. AGENT 2 — DATA CLEANING AGENT

### Purpose

Correct straightforward data-quality issues while preserving valid information.

### Responsibilities

1. Standardize column names.
2. Remove exact duplicate rows when enabled.
3. Trim unnecessary whitespace from string columns.
4. Normalize categorical capitalization when appropriate.
5. Normalize common missing-value markers such as empty strings and configured tokens.
6. Convert data types only when conversion is safe.
7. Identify invalid values and conversion failures.
8. Flag suspicious columns without automatically deleting them.
9. Record every modification.

### Example

Original categorical values:

- `Male`
- `male`
- ` MALE `
- `Female`
- `female`

After approved normalization:

- `Male`
- `Male`
- `Male`
- `Female`
- `Female`

### Rules

- Do not remove duplicate rows without recording how many were removed.
- Do not treat every repeated value as a duplicate record.
- Do not automatically drop identifier columns.
- Do not assume that every extreme numeric value is an error.
- Preserve the original dataset.
- Allow the user to disable individual transformations.
- Handle errors without crashing the application.

Every operation must generate an audit entry containing the operation name, affected column or rows, number of affected records where applicable, and outcome.

---

## 8. AGENT 3 — MISSING VALUE AGENT

### Purpose

Select and apply appropriate missing-value handling methods based on column characteristics and the user's configuration.

### Responsibilities

1. Detect remaining missing values.
2. Classify columns by data type.
3. Calculate missing-value percentages.
4. Select a suitable imputation strategy.
5. Apply imputation through Pandas or Scikit-learn.
6. Report which values were imputed.
7. Flag columns for which automatic imputation may be unreliable.

### Default strategies

For numerical columns:
- Median imputation by default.
- Mean imputation as an optional alternative.

For categorical columns:
- Most-frequent-value imputation.
- A configurable `Unknown` category where appropriate.

For datetime columns:
- Do not blindly fill missing dates.
- Use a configurable strategy only when the meaning and ordering of the data justify it.

For columns with excessive missingness:
- Recommend dropping the column or retaining it with an appropriate missingness indicator.
- Ask the user for confirmation when the choice could materially affect the dataset.

For target columns:
- Do not silently impute missing target labels.
- Flag the issue and ask the user to choose whether affected training records should be excluded.

### Example

If the `Age` column contains:

`20, 22, NaN, 24, 100`

The agent calculates the median and uses the selected strategy to fill the missing value.

It must not assume that `100` is invalid merely because it is an outlier.

### Important requirements

- Never silently remove valid records.
- Preserve a record of the original missing-value counts.
- Explain why a particular strategy was selected.
- Make the strategy configurable through the UI.
- Provide a clear warning when an automatic decision is uncertain.

For model training, learn imputation statistics from training data only. Never calculate them using the held-out test set.

---

## 9. AGENT 4 — FEATURE ENGINEERING AGENT

### Purpose

Prepare the cleaned data for use by common machine-learning algorithms.

### Responsibilities

1. Identify numerical and categorical features.
2. Encode categorical variables.
3. Scale numerical features when appropriate.
4. Detect constant features.
5. Identify potential identifier columns.
6. Recommend feature transformations.
7. Support optional outlier treatment.
8. Generate a feature summary.
9. Preserve a mapping between original and transformed columns where practical.

### Required preprocessing methods

For categorical columns:
- One-hot encoding for nominal features.
- Ordinal encoding only when a meaningful order is specified.
- Safe handling of previously unseen categories.

For numerical columns:
- StandardScaler or MinMaxScaler as selectable options.
- No scaling when it is unnecessary or explicitly disabled.

For outliers:
- Detect potential outliers using the interquartile range (IQR) method.
- Report the affected columns and counts.
- Allow the user to leave outliers unchanged or choose an explicitly configured treatment.

For constant features:
- Flag columns with a single unique non-missing value.
- Allow the user to remove them after confirmation.

### Leakage prevention

Do not perform transformations using information from the test set.

For model training, use a Scikit-learn Pipeline or ColumnTransformer so imputation, encoding, and scaling are fitted on training data and subsequently applied to test data.

For a standalone exported dataset, make clear that the export is intended for exploration or downstream preparation and that model evaluation requires leakage-safe train/test preprocessing.

Do not use the target column as an input feature.

Do not automatically drop all identifier-like columns because some may carry useful information.

---

## 10. AGENT 5 — QUALITY VALIDATOR AGENT

### Purpose

Check the output of previous agents and determine whether the dataset satisfies the configured quality requirements.

### Validation checks

1. Verify column names and expected structure.
2. Check for remaining missing values.
3. Check for duplicate rows.
4. Check data-type consistency.
5. Check for unexpected infinite values.
6. Identify constant columns.
7. Validate categorical encoding.
8. Detect unexpected row-count changes.
9. Confirm that transformations were recorded.
10. Check target-column availability if model training is requested.
11. Check for potential train/test leakage in the model-training workflow.
12. Produce a final data-quality score with a transparent calculation.

### Validation decision

The validator must return one of three states:

- PASS: All required checks succeed.
- WARNING: The dataset is usable, but some issues require attention.
- FAIL: A critical requirement is violated.

If validation fails, return a structured list of issues to the orchestrator.

The orchestrator may retry the responsible agent for a maximum of two correction attempts. Prevent infinite loops.

If an issue cannot be corrected safely, stop the workflow and ask the user to review it.

### Data-quality score

Create an explainable score from 0 to 100 based on configurable indicators such as:

- Missing-value completeness.
- Duplicate-row rate.
- Type consistency.
- Required validation checks.

Display the component scores and their weights. Make clear that the score is an internal quality indicator, not a universal statistical standard or a guarantee of model accuracy.

---

## 11. CENTRAL ORCHESTRATOR

The orchestrator is responsible for managing the entire workflow.

### Responsibilities

1. Receive the uploaded dataset and user preferences.
2. Initialize workflow state.
3. Execute the inspector.
4. Construct a preprocessing plan from the findings.
5. Execute enabled cleaning operations.
6. Execute missing-value handling.
7. Execute feature engineering.
8. Run the quality validator.
9. Evaluate validation results.
10. Retry eligible corrections when validation fails.
11. Stop after the configured retry limit.
12. Generate the final report.
13. Make the output available for download.

### Agent workflow example

Input dataset
→ Inspector detects missing values and duplicate rows
→ Orchestrator creates a plan
→ Cleaner removes configured duplicate rows
→ Imputer handles missing values
→ Feature engineer prepares the selected features
→ Validator checks the result
→ If validation fails, the orchestrator identifies the relevant agent and retries
→ If validation succeeds or only noncritical warnings remain, produce the report and final dataset

The application must record the real execution sequence.

Do not merely display fabricated messages such as “Agent is thinking” or “Agent completed successfully.” Update the interface based on actual function execution and results.

---

## 12. GENUINE AGENTIC AI REQUIREMENTS

This project must demonstrate agentic behavior rather than simply running five fixed preprocessing functions and calling them agents.

Include these capabilities:

### A. Goal interpretation

Allow the user to specify a goal such as:

“Clean this dataset for a classification model.”

The system should use that goal to select relevant preprocessing and validation steps.

### B. Planning

Create a structured plan based on the inspector's findings and the user's configuration.

### C. Tool calling

Provide the agent with controlled Python tools, including:

- `profile_dataset`
- `remove_duplicates`
- `standardize_categories`
- `impute_missing_values`
- `detect_outliers`
- `encode_categorical_features`
- `scale_numerical_features`
- `validate_dataset`
- `generate_quality_report`

The LLM may select among permitted tools, but each tool must have validated inputs and actual implementations.

### D. Conditional decisions

Examples:

- Skip imputation if there are no missing values.
- Skip encoding if no categorical features are selected.
- Request approval before dropping a high-missingness column.
- Run additional validation after a failed check.
- Recommend an alternative method when the selected transformation fails.

### E. Shared state

Pass structured results between agents and retain the workflow's execution history.

### F. Verification

Require the validator to independently recalculate key quality metrics after transformations.

### G. Transparency

Show the chosen operation, reason, result, and any warnings.

### H. Safe fallback

If the LLM is unavailable, use deterministic rules and continue processing.

Do not allow the LLM to execute arbitrary Python code, access the filesystem without restriction, or modify system settings.

The agents should use allowlisted tools with validated arguments.

---

## 13. USER INTERFACE

Create a professional, modern Streamlit dashboard.

Use a clean, light-themed design with restrained colors, readable typography, clear status indicators, and consistent spacing.

Do not sacrifice usability for decorative elements.

### Page 1: Home Dashboard

Display:

- Project name and short description.
- Start-processing button.
- Number of supported file formats.
- Agent workflow overview.
- Brief explanation of the system.

### Page 2: Dataset Upload

Allow users to upload:

- CSV files.
- XLSX files.

Validate file size and extension.

Display:
- Filename.
- File size.
- Row count.
- Column count.
- Dataset preview.

Provide an option to download a small sample dataset for testing.

### Page 3: Dataset Profiling

Display:

- Dataset shape.
- Column data types.
- Missing-value count and percentage.
- Duplicate-row count.
- Numerical statistics.
- Categorical distributions.
- Potential outlier counts.
- Constant-column warnings.

Use charts and tables where useful.

### Page 4: Preprocessing Configuration

Allow the user to configure:

- Whether to remove exact duplicate rows.
- Whether to standardize string values.
- Numerical imputation strategy.
- Categorical imputation strategy.
- Maximum acceptable missingness before requiring confirmation.
- Whether to encode categorical variables.
- Numerical scaling method.
- Whether to detect or treat outliers.
- Target column, if model training is required.
- Whether to train a baseline model.

Use safe defaults.

### Page 5: Agent Execution

Display the agents as separate stages:

1. Data Inspector
2. Data Cleaner
3. Missing Value Handler
4. Feature Engineer
5. Quality Validator

For each agent, display:

- Current status.
- Operations performed.
- Number of rows or columns affected where applicable.
- Findings.
- Warnings.
- Execution result.

Use actual workflow state to determine the displayed status.

### Page 6: Results Dashboard

Display before-and-after comparisons for:

- Number of rows.
- Number of columns.
- Missing values.
- Duplicate rows.
- Data-type issues.
- Data-quality score.

Show:
- Processed dataset preview.
- Transformation history.
- Validation status.
- Warnings and unresolved issues.

### Page 7: Export

Provide downloadable files for:

- Cleaned dataset in CSV format.
- JSON preprocessing report.
- JSON or YAML preprocessing configuration, if supported.
- Optional PDF summary report.

Clearly indicate the exact transformations applied and any remaining limitations.

### Page 8: Optional Model Training

Allow the user to select a target column and choose classification or regression.

Support simple baseline models:

Classification:
- Logistic Regression.
- Decision Tree Classifier.

Regression:
- Linear Regression.
- Decision Tree Regressor.

Use a train/test split and leakage-safe Scikit-learn Pipelines.

For classification, display suitable metrics such as accuracy, precision, recall, F1-score, and a confusion matrix.

For regression, display MAE, RMSE, and R² where applicable.

Handle class imbalance, small datasets, missing target labels, and unsupported target types with clear warnings.

Do not guarantee high model accuracy simply because the dataset was cleaned.

---

## 14. DATASET REQUIREMENTS

The application must be generic and not hardcoded for one specific dataset.

Initially support tabular CSV and Excel datasets.

The system should work with datasets containing:

- Numerical columns.
- Categorical columns.
- Boolean columns.
- Datetime columns.
- Missing values.
- Duplicate rows.
- Inconsistent string values.
- Potential outliers.

Include a small synthetic dataset for demonstration and testing.

The synthetic dataset should deliberately contain:
- Missing numerical values.
- Missing categorical values.
- Duplicate rows.
- Inconsistent capitalization and whitespace.
- At least one categorical feature.
- At least two numerical features.
- A target column suitable for a basic model-training demonstration.

Clearly label synthetic data as demonstration data.

Do not require an external dataset download for the basic application to run.

The user should be able to upload their own dataset and inspect the result.

---

## 15. DATA SAFETY AND CORRECTNESS

Follow these rules strictly:

1. Never overwrite the original uploaded dataset.
2. Never delete columns or rows without recording the reason.
3. Never silently modify target labels.
4. Never treat all outliers as invalid.
5. Never claim the dataset is perfect or universally model-ready.
6. Never calculate model evaluation metrics on training data and present them as test performance.
7. Never fit preprocessing transformations on the held-out test set.
8. Never include target information in feature transformations that could cause leakage.
9. Never expose API keys in the interface, logs, or reports.
10. Never execute code generated by the LLM directly.
11. Validate uploaded files and handle malformed inputs.
12. Set configurable limits for upload size and dataset dimensions.
13. Use temporary or in-memory processing where practical.
14. Clearly disclose when an operation is skipped, fails, or requires user approval.
15. Keep an audit trail for all applied transformations.

When the application is used on a new dataset, it must inspect the data before selecting transformations.

---

## 16. PROJECT FOLDER STRUCTURE

Organize the application into separate modules.

Use the following structure as the starting point:

autoprep-ai/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── agents/
│   ├── __init__.py
│   ├── inspector_agent.py
│   ├── cleaning_agent.py
│   ├── missing_value_agent.py
│   ├── feature_engineering_agent.py
│   └── validator_agent.py
│
├── orchestrator/
│   ├── __init__.py
│   ├── workflow.py
│   └── state.py
│
├── tools/
│   ├── __init__.py
│   ├── profiling.py
│   ├── cleaning.py
│   ├── imputation.py
│   ├── feature_engineering.py
│   ├── validation.py
│   └── reporting.py
│
├── ml/
│   ├── __init__.py
│   ├── preprocessing_pipeline.py
│   └── model_training.py
│
├── ui/
│   ├── __init__.py
│   ├── components.py
│   └── charts.py
│
├── sample_data/
│   └── sample_dataset.csv
│
├── reports/
│   └── .gitkeep
│
└── tests/
    ├── test_profiling.py
    ├── test_cleaning.py
    ├── test_imputation.py
    ├── test_validation.py
    └── test_workflow.py

You may adjust the structure slightly if necessary, but maintain clear separation between UI, agents, tools, workflow orchestration, and model training.

Do not place the entire application inside one Python file.

---

## 17. IMPLEMENTATION PLAN

Build the application in phases.

### Phase 1: Basic working application

Implement:
- Streamlit UI.
- CSV and Excel uploads.
- Dataset preview.
- Data profiling.
- Synthetic sample dataset.

At the end of this phase, the application must run locally.

### Phase 2: Core preprocessing tools

Implement:
- Duplicate removal.
- String normalization.
- Missing-value imputation.
- Data-type checks.
- Outlier detection.
- Categorical encoding and numerical scaling.

Write unit tests for these operations.

### Phase 3: Agent implementation

Create five separate agent modules.

Each agent must:
- Accept structured inputs.
- Perform its assigned responsibilities.
- Return structured outputs.
- Record actions and warnings.
- Handle failures gracefully.

### Phase 4: Orchestration

Implement:
- Shared state.
- Agent execution order.
- Conditional transitions.
- Validation-based correction.
- Maximum retry count.
- Audit logging.

### Phase 5: Agentic LLM integration

Add:
- Goal interpretation.
- LLM-assisted planning.
- Controlled tool selection.
- Explanation of decisions.
- Fallback behavior when no API key is configured.

Keep the core preprocessing functional without an LLM.

### Phase 6: Results and export

Implement:
- Before-and-after comparisons.
- Data-quality metrics.
- Processed dataset preview.
- CSV export.
- JSON report export.
- Optional PDF export.

### Phase 7: Model training

Implement:
- Target selection.
- Classification and regression detection or selection.
- Leakage-safe train/test split.
- Scikit-learn Pipelines.
- Baseline model training.
- Evaluation metrics.

### Phase 8: Testing and documentation

Implement tests for:
- Valid datasets.
- Missing values.
- Duplicate rows.
- Empty datasets.
- Malformed files.
- Mixed data types.
- Columns containing only missing values.
- Validation failures.
- Workflow retry limits.
- Model training.
- Export functionality.
- LLM-unavailable fallback.

Complete the README and academic documentation.

---

## 18. ERROR HANDLING

Handle common problems without crashing the application.

Examples include:

- Unsupported file format.
- Empty CSV file.
- Invalid Excel file.
- Dataset with zero rows.
- Dataset with only one column.
- Dataset with all values missing in a column.
- Dataset with duplicate column names.
- Invalid date formats.
- Numerical conversion failures.
- Insufficient rows for train/test splitting.
- Target column with only one class.
- Missing API credentials.
- LLM timeout or API errors.
- Failed preprocessing operations.
- Validation failures after retries.

Display understandable messages to users and record technical details in appropriate logs without revealing secrets.

Never report a successful transformation when the underlying operation failed.

---

## 19. TESTING REQUIREMENTS

Write meaningful unit and integration tests.

At minimum, verify the following:

1. Missing-value counts are calculated correctly.
2. Duplicate rows are detected correctly.
3. Enabled duplicate removal works as expected.
4. Numerical imputation works with valid numerical data.
5. Categorical imputation works with valid categorical data.
6. String standardization does not alter unrelated numeric values.
7. The validator identifies remaining missing values.
8. The original dataset remains unchanged.
9. The orchestrator executes the expected agents.
10. Failed validation triggers a bounded correction attempt.
11. The workflow terminates after the retry limit.
12. CSV exports can be read back successfully.
13. Training preprocessing is fitted only on the training partition.
14. Model training produces metrics when the dataset is suitable.
15. The application remains functional without an LLM API key.

Use synthetic test fixtures rather than relying on internet access.

Do not claim that tests passed unless they have actually been executed.

---

## 20. ACADEMIC DELIVERABLES

Prepare the following deliverables:

### A. Working source code

Provide all required Python modules and configuration files.

### B. README

Include:
- Project overview.
- Problem statement.
- Features.
- Architecture.
- Technology stack.
- Installation instructions.
- Configuration.
- Run commands.
- Example workflow.
- Troubleshooting.

### C. Project report

Write an academic report with these sections:

1. Title page.
2. Abstract.
3. Introduction.
4. Problem statement.
5. Objectives.
6. Existing-system limitations.
7. Proposed system.
8. System architecture.
9. Agent descriptions.
10. Methodology.
11. Implementation details.
12. Dataset description.
13. Results and screenshots to be captured from the actual application.
14. Testing and evaluation.
15. Limitations.
16. Future scope.
17. Conclusion.
18. References.

Do not invent screenshots, measured improvements, experimental results, or citations.

### D. Diagrams

Prepare:
- System architecture diagram.
- Agent workflow diagram.
- Data-flow diagram.
- Use-case diagram.
- Optional sequence diagram.

### E. Presentation

Create a presentation outline with approximately 10 slides:
1. Title.
2. Problem statement.
3. Objectives.
4. Existing versus proposed system.
5. Architecture.
6. Five-agent workflow.
7. Technology stack.
8. Demonstration results.
9. Limitations and future scope.
10. Conclusion.

### F. Viva preparation

Prepare at least 20 questions with simple answers covering:
- Agentic AI.
- Multi-agent systems.
- LLMs.
- Tool calling.
- Pandas.
- Missing-value imputation.
- Feature engineering.
- Outlier detection.
- Data validation.
- LangGraph or the selected orchestration approach.
- Scikit-learn Pipelines.
- Data leakage.
- Train/test splitting.
- Evaluation metrics.
- Why this project is different from ordinary data cleaning.

---

## 21. DEFINITION OF DONE

The project is complete only when:

- The application runs locally.
- A user can upload a CSV or Excel dataset.
- Dataset profiling works on actual uploaded data.
- Each of the five agents performs real, distinct operations.
- The orchestrator manages the workflow and records execution.
- Missing values and duplicates can be handled using configurable methods.
- Feature engineering is performed when enabled.
- Validation checks run after preprocessing.
- Failed validation is handled safely.
- The application shows before-and-after results.
- A cleaned dataset can be downloaded.
- A preprocessing report can be downloaded.
- The original dataset remains unchanged.
- The optional baseline model uses leakage-safe preprocessing.
- The application works without an LLM API key through deterministic fallback.
- Automated tests exist and have been run.
- Setup and demonstration instructions are documented.

Do not claim the dataset is ready for every machine-learning problem. Report the transformations applied and any unresolved issues.

---

## 22. HOW YOU MUST GENERATE THE CODE

Follow these development instructions carefully.

1. Start by presenting the proposed architecture and explaining how the five agents interact.
2. Provide the complete folder structure.
3. Explain the responsibilities of each module.
4. List the required dependencies and explain how to install them.
5. Generate the project in small, logically ordered phases.
6. For every file, provide its exact relative path followed by its complete source code.
7. Do not provide incomplete placeholders such as “implement this later,” “rest of the code here,” or pseudocode where working code is required.
8. Ensure imports, function names, and interfaces are consistent across modules.
9. Explain how to create and activate a Python virtual environment on Windows PowerShell.
10. Explain how to configure the optional LLM API key.
11. Provide exact commands to run the application and tests.
12. Test the core workflow using the included synthetic dataset.
13. When an error occurs, identify the cause and provide a concrete fix.
14. Avoid introducing unnecessary dependencies.
15. Prioritize a fully working MVP over advanced features.
16. Do not generate all files in a single enormous response if doing so risks truncation. Divide the work into phases while preserving a consistent architecture.
17. At the end of each phase, explain which files have been created, how to run or test them, and what should work at that stage.
18. Do not claim to have created files or executed tests unless that has actually occurred.
19. Explain technical concepts in beginner-friendly language so the student can confidently explain the implementation during an examination.
20. After the implementation, help prepare the project report, architecture diagrams, presentation, and viva answers.

Begin with Phase 1 and produce a working, minimal version before moving to advanced functionality.

The final objective is a real, modular, reliable, dataset-independent multi-agent preprocessing application suitable for an academic demonstration.