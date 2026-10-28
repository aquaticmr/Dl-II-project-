import streamlit as st

def apply_custom_styles():
    """Inject modern, elegant CSS tokens and card styling for dark theme."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        
        .sub-header {
            color: #94A3B8;
            font-size: 1.05rem;
            margin-bottom: 1.8rem;
        }

        .metric-card {
            background: #1E293B;
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            text-align: center;
            color: #F8FAFC;
        }

        .agent-badge-success {
            background-color: #064E3B;
            color: #6EE7B7;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }

        .agent-badge-running {
            background-color: #1E3A8A;
            color: #93C5FD;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }

        .agent-badge-warning {
            background-color: #78350F;
            color: #FDE68A;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)

def render_agent_status_card(name: str, role: str, status: str, details: str):
    """Renders a structured visual agent execution step card with dark mode styling."""
    badge_class = "agent-badge-success" if status in ["SUCCESS", "PASS"] else ("agent-badge-warning" if status == "WARNING" else "agent-badge-running")
    st.markdown(f"""
        <div style="background:#1E293B; border-left: 4px solid #60A5FA; border:1px solid #334155; border-left-width:4px; padding:14px 18px; border-radius:8px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600; font-size:1.05rem; color:#F8FAFC;">{name}</span>
                <span class="{badge_class}">{status}</span>
            </div>
            <div style="color:#94A3B8; font-size:0.85rem; margin-top:2px;">{role}</div>
            <div style="color:#CBD5E1; font-size:0.95rem; margin-top:8px;">{details}</div>
        </div>
    """, unsafe_allow_html=True)
