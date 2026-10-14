import streamlit as st

def apply_custom_styles():
    """Inject modern, elegant CSS tokens and card styling."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        
        .sub-header {
            color: #64748B;
            font-size: 1.05rem;
            margin-bottom: 1.8rem;
        }

        .metric-card {
            background: #FFFFFF;
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            text-align: center;
        }

        .agent-badge-success {
            background-color: #DCFCE7;
            color: #166534;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }

        .agent-badge-running {
            background-color: #DBEAFE;
            color: #1E40AF;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }

        .agent-badge-warning {
            background-color: #FEF3C7;
            color: #92400E;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)

def render_agent_status_card(name: str, role: str, status: str, details: str):
    """Renders a structured visual agent execution step card."""
    badge_class = "agent-badge-success" if status in ["SUCCESS", "PASS"] else ("agent-badge-warning" if status == "WARNING" else "agent-badge-running")
    st.markdown(f"""
        <div style="background:#F8FAFC; border-left: 4px solid #3B82F6; padding:12px 16px; border-radius:8px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600; font-size:1.05rem; color:#0F172A;">{name}</span>
                <span class="{badge_class}">{status}</span>
            </div>
            <div style="color:#64748B; font-size:0.85rem; margin-top:2px;">{role}</div>
            <div style="color:#334155; font-size:0.95rem; margin-top:8px;">{details}</div>
        </div>
    """, unsafe_allow_html=True)
