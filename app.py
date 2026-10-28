import os
import json
import pandas as pd
import streamlit as st

from orchestrator.workflow import WorkflowOrchestrator
from tools.profiling import profile_dataset
from tools.reporting import export_report_to_json
from sample_data.generate_sample import generate_sample_dataset
from ui.components import apply_custom_styles, render_agent_status_card
from ui.charts import create_score_gauge, create_missing_chart, create_comparison_chart

st.set_page_config(
    page_title="AutoPrep AI — Multi-Agent Dataset Preparation System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()

# Ensure sample dataset exists
sample_path = "sample_data/sample_dataset.csv"
if not os.path.exists(sample_path):
    generate_sample_dataset(sample_path)

# Initialize Session State
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = None
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = "None"

# Navigation
st.sidebar.title("🤖 AutoPrep AI")
st.sidebar.markdown("*Multi-Agent Intelligent Dataset Preparation*")

nav_choice = st.sidebar.radio(
    "Navigation",
    [
        "1. Home & Architecture",
        "2. Dataset Upload & Profile",
        "3. Preprocessing Config",
        "4. Multi-Agent Execution",
        "5. Results & Audit Log",
        "6. Export & Download"
    ]
)

# ---------------- PAGE 1: HOME & ARCHITECTURE ----------------
if nav_choice == "1. Home & Architecture":
    st.markdown('<div class="main-header">AutoPrep AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">A Multi-Agent Intelligent Framework for Automated Dataset Cleaning, Transformation, Validation, and Machine Learning Preparation</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("""
        ### Welcome to AutoPrep AI!
        AutoPrep AI automates tedious data preprocessing through a coordinated **Multi-Agent Architecture**:
        
        1. 🔍 **Data Inspector Agent**: Profiles structure, detects missing values, duplicates, outliers, and potential ID columns.
        2. 🧹 **Data Cleaning Agent**: Normalizes column headers, removes duplicate rows, and standardizes categorical text casing.
        3. 🧩 **Missing Value Agent**: Applies intelligent median, mean, or mode imputation with strict leakage & target safety.
        4. ⚙️ **Feature Engineering Agent**: Detects & caps IQR outliers, encodes nominal/ordinal categories, and scales features.
        5. ✅ **Quality Validator Agent**: Validates output consistency, recalculates data quality scores, and executes bounded correction loops.

        ### Key Agentic Capabilities:
        - **Shared State Management**: Agents communicate through structured Python state (`WorkflowState`).
        - **Controlled Tool Calling**: Modular, tested Python tool implementations with validated inputs.
        - **Conditional Correction Loops**: Automatic retry mechanisms if post-validation fails.
        - **Leakage Prevention**: Strictly isolates held-out test splits in model training.
        """)
        
        st.info("💡 To start, head to **2. Dataset Upload & Profile** to upload a CSV/Excel file or load the built-in synthetic demonstration dataset.")
    
    with col2:
        st.markdown("### Agent Workflow Diagram")
        st.markdown("""
        ```mermaid
        graph TD
            U[User Dataset] --> I[Agent 1: Inspector]
            I --> O[Workflow Orchestrator]
            O --> C[Agent 2: Cleaner]
            C --> M[Agent 3: Imputer]
            M --> F[Agent 4: Feature Eng.]
            F --> V[Agent 5: Validator]
            V -- Status == FAIL (Retry <= 2) --> M
            V -- Status in [PASS, WARNING] --> R[Export & ML Ready]
        ```
        """)

# ---------------- PAGE 2: UPLOAD & PROFILE ----------------
elif nav_choice == "2. Dataset Upload & Profile":
    st.markdown('<div class="main-header">Dataset Upload & Automatic Profiling</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload a tabular CSV/Excel dataset or test with our pre-configured synthetic dataset.</div>', unsafe_allow_html=True)

    col_up1, col_up2 = st.columns([2, 1])
    with col_up1:
        uploaded_file = st.file_uploader("Upload CSV or XLSX file", type=["csv", "xlsx"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    st.session_state.raw_df = pd.read_csv(uploaded_file)
                else:
                    st.session_state.raw_df = pd.read_excel(uploaded_file)
                st.session_state.dataset_name = uploaded_file.name
                st.session_state.workflow_state = None
                st.success(f"Successfully loaded '{uploaded_file.name}'!")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    with col_up2:
        st.markdown("#### Sample Demo Dataset")
        st.caption("Contains deliberate flaws (missing values, duplicates, outliers, casing errors).")
        if st.button("Load Built-in Sample Dataset", use_container_width=True):
            st.session_state.raw_df = pd.read_csv(sample_path)
            st.session_state.dataset_name = "sample_dataset.csv (Demonstration)"
            st.session_state.workflow_state = None
            st.success("Loaded synthetic demonstration dataset!")

    if st.session_state.raw_df is not None:
        df = st.session_state.raw_df
        st.divider()
        st.subheader(f"Dataset Overview: {st.session_state.dataset_name}")
        
        # Profile using Data Inspector logic
        profile = profile_dataset(df)
        
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Rows", profile["num_rows"])
        m2.metric("Total Columns", profile["num_columns"])
        m3.metric("Total Missing Cells", profile["total_missing"])
        m4.metric("Duplicate Rows", profile["duplicate_rows"])
        m5.metric("Data Quality Score", f"{profile['quality_score']}/100")

        tab_preview, tab_stats, tab_charts = st.tabs(["Dataset Preview", "Data Structure & Types", "Data Quality Visuals"])
        with tab_preview:
            st.dataframe(df.head(15), use_container_width=True)
        with tab_stats:
            dtypes_df = pd.DataFrame({
                "Column": profile["columns"],
                "Data Type": [profile["dtypes"][c] for c in profile["columns"]],
                "Missing Count": [profile["missing_values"][c] for c in profile["columns"]],
                "Missing %": [f"{profile['missing_pct'][c]}%" for c in profile["columns"]]
            })
            st.dataframe(dtypes_df, use_container_width=True)
        with tab_charts:
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(create_score_gauge(profile["quality_score"], "Initial Quality Score"), use_container_width=True)
            with c2:
                st.plotly_chart(create_missing_chart(profile["missing_values"]), use_container_width=True)

        if profile["issues"]:
            st.warning("⚠️ **Detected Data Quality Issues:**\n- " + "\n- ".join(profile["issues"]))
    else:
        st.info("Please upload a file or click 'Load Built-in Sample Dataset' to begin.")

# ---------------- PAGE 3: PREPROCESSING CONFIG ----------------
elif nav_choice == "3. Preprocessing Config":
    st.markdown('<div class="main-header">Agent Preprocessing Configuration</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configure the transformation parameters for each specialized agent.</div>', unsafe_allow_html=True)

    if st.session_state.raw_df is None:
        st.warning("Please upload or load a dataset first in Step 2.")
    else:
        df = st.session_state.raw_df
        cols = list(df.columns)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("### 🧹 Data Cleaner Settings")
            remove_dup = st.checkbox("Remove exact duplicate rows", value=True)
            std_headers = st.checkbox("Standardize column headers (snake_case)", value=True)
            std_strings = st.checkbox("Normalize categorical string casing & whitespace", value=True)
            string_casing = st.selectbox("Categorical casing style", ["title", "lower", "upper"], index=0)

            st.markdown("### 🧩 Missing Value Handler Settings")
            num_imp = st.selectbox("Numerical imputation strategy", ["median", "mean", "constant_zero"], index=0)
            cat_imp = st.selectbox("Categorical imputation strategy", ["mode", "constant_unknown"], index=0)
            max_miss = st.slider("Maximum allowed missing rate before flagging", 0.1, 0.9, 0.6, 0.05)

        with col_c2:
            st.markdown("### ⚙️ Feature Engineer Settings")
            treat_out = st.selectbox("Outlier treatment method", ["cap", "none"], index=0)
            enc_cat = st.selectbox("Categorical encoding", ["onehot", "label", "none"], index=0)
            scale_num = st.selectbox("Numerical scaling", ["standard", "minmax", "none"], index=0)

            st.markdown("### 🎯 Machine Learning Target (Optional)")
            target_col = st.selectbox("Designate Target Column (Optional)", ["None"] + cols, index=cols.index("Purchased") + 1 if "Purchased" in cols else 0)
            target_col_val = None if target_col == "None" else target_col

        st.session_state.config = {
            "remove_duplicates": remove_dup,
            "standardize_columns": std_headers,
            "standardize_strings": std_strings,
            "string_casing": string_casing,
            "numerical_imputation": num_imp,
            "categorical_imputation": cat_imp,
            "max_missing_threshold": max_miss,
            "treat_outliers": treat_out,
            "encode_categorical": enc_cat,
            "scale_numerical": scale_num,
            "target_column": target_col_val
        }
        st.success("✅ Preprocessing configuration updated! Ready for multi-agent execution.")

# ---------------- PAGE 4: MULTI-AGENT EXECUTION ----------------
elif nav_choice == "4. Multi-Agent Execution":
    st.markdown('<div class="main-header">Multi-Agent Workflow Execution</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Trigger the orchestrated 5-agent pipeline and observe live agent execution logs.</div>', unsafe_allow_html=True)

    if st.session_state.raw_df is None:
        st.warning("Please upload or load a dataset first in Step 2.")
    else:
        config = getattr(st.session_state, "config", {
            "remove_duplicates": True,
            "standardize_columns": True,
            "standardize_strings": True,
            "string_casing": "title",
            "numerical_imputation": "median",
            "categorical_imputation": "mode",
            "max_missing_threshold": 0.60,
            "treat_outliers": "cap",
            "encode_categorical": "onehot",
            "scale_numerical": "standard",
            "target_column": "Purchased" if "Purchased" in st.session_state.raw_df.columns else None
        })

        if st.button("🚀 Run Multi-Agent AutoPrep Pipeline", type="primary", use_container_width=True):
            with st.spinner("Multi-Agent pipeline executing..."):
                orchestrator = WorkflowOrchestrator(max_retries=2)
                state = orchestrator.run(st.session_state.raw_df, config)
                st.session_state.workflow_state = state
                st.success("🎉 Multi-Agent workflow completed!")

        if st.session_state.workflow_state is not None:
            state = st.session_state.workflow_state
            st.divider()
            st.subheader("Agent Execution Feed")

            res = state.agent_results
            render_agent_status_card("Agent 1: Data Inspector", "Profiling & Anomaly Discovery", res.get("inspector", {}).get("status", "SUCCESS"), res.get("inspector", {}).get("summary", "Complete"))
            render_agent_status_card("Agent 2: Data Cleaner", "Duplicates & String Normalization", res.get("cleaning", {}).get("status", "SUCCESS"), res.get("cleaning", {}).get("summary", "Complete"))
            render_agent_status_card("Agent 3: Missing Value Handler", "Imputation & Target Safety", res.get("missing_value", {}).get("status", "SUCCESS"), res.get("missing_value", {}).get("summary", "Complete"))
            render_agent_status_card("Agent 4: Feature Engineer", "Outlier Capping, Encoding & Scaling", res.get("feature_engineering", {}).get("status", "SUCCESS"), res.get("feature_engineering", {}).get("summary", "Complete"))
            render_agent_status_card("Agent 5: Quality Validator", "Verification & Scoring", res.get("validator", {}).get("validation_status", "PASS"), res.get("validator", {}).get("summary", "Complete"))

            if state.validation_status == "PASS":
                st.success("✅ **Quality Validator Decision: PASS** — Dataset satisfies all quality and integrity checks!")
            elif state.validation_status == "WARNING":
                st.warning(f"⚠️ **Quality Validator Decision: WARNING** — Dataset processed with minor non-blocking notices.")
            else:
                st.error("❌ **Quality Validator Decision: FAIL** — Unresolved issues remain.")

# ---------------- PAGE 5: RESULTS & AUDIT LOG ----------------
elif nav_choice == "5. Results & Audit Log":
    st.markdown('<div class="main-header">Results & Quality Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Transparent audit log and measurable before-and-after quality benchmarks.</div>', unsafe_allow_html=True)

    if st.session_state.workflow_state is None:
        st.warning("Please execute the multi-agent pipeline in Step 4 to view results.")
    else:
        state = st.session_state.workflow_state
        before = state.profile_data
        after = state.validation_result

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Rows (Before -> After)", f"{before['num_rows']} → {after['num_rows']}")
        col_m2.metric("Missing Values", f"{before['total_missing']} → {after['remaining_missing']}", delta=-(before['total_missing'] - after['remaining_missing']))
        col_m3.metric("Duplicate Rows", f"{before['duplicate_rows']} → {after['remaining_duplicates']}", delta=-(before['duplicate_rows'] - after['remaining_duplicates']))
        col_m4.metric("Quality Score", f"{before['quality_score']} → {after['score']}", delta=round(after['score'] - before['quality_score'], 1))

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(create_comparison_chart(before, after), use_container_width=True)
        with c2:
            st.plotly_chart(create_score_gauge(after['score'], "Final Validated Quality Score"), use_container_width=True)

        st.subheader("Cleaned Dataset Preview")
        st.dataframe(state.final_df.head(20), use_container_width=True)

        st.subheader("Detailed Transformation Audit Trail")
        audit_records = []
        for a in state.audit_log:
            audit_records.append({
                "Step": a["step"],
                "Agent": a["agent"],
                "Action": a["action"],
                "Details": str(a["details"])
            })
        st.dataframe(pd.DataFrame(audit_records), use_container_width=True)

# ---------------- PAGE 6: EXPORT & DOWNLOAD ----------------
elif nav_choice == "6. Export & Download":
    st.markdown('<div class="main-header">Export & Audit Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Download the machine-learning-ready dataset and complete JSON audit report.</div>', unsafe_allow_html=True)

    if st.session_state.workflow_state is None or st.session_state.workflow_state.final_df is None:
        st.warning("Please execute the multi-agent pipeline in Step 4 before downloading exports.")
    else:
        state = st.session_state.workflow_state
        csv_data = state.final_df.to_csv(index=False).encode('utf-8')
        json_report = export_report_to_json(state.final_report).encode('utf-8')

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("### 📥 Cleaned Dataset")
            st.caption("Machine-learning prepared, imputed, and validated CSV file.")
            st.download_button(
                label="Download Cleaned CSV",
                data=csv_data,
                file_name="autoprep_cleaned_dataset.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_d2:
            st.markdown("### 📄 Preprocessing Audit Report")
            st.caption("Full JSON record with before/after benchmarks and step audit log.")
            st.download_button(
                label="Download Audit Report (JSON)",
                data=json_report,
                file_name="autoprep_audit_report.json",
                mime="application/json",
                use_container_width=True
            )

        st.subheader("Raw Report Preview")
        st.json(state.final_report)
