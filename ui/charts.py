import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any

def create_score_gauge(score: float, title: str = "Quality Score") -> go.Figure:
    """Creates a sleek gauge chart for data quality score (0 to 100) tuned for dark theme."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20, 'color': "#F8FAFC"}},
        number={'font': {'color': "#F8FAFC"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#64748B", 'tickfont': {'color': '#94A3B8'}},
            'bar': {'color': "#60A5FA"},
            'bgcolor': "#1E293B",
            'borderwidth': 1,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.25)'},
                {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.25)'},
                {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.25)'}
            ],
            'threshold': {
                'line': {'color': "#34D399", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=240,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_missing_chart(missing_dict: Dict[str, int]) -> go.Figure:
    """Bar chart for missing value counts per column tuned for dark theme."""
    items = [(col, count) for col, count in missing_dict.items() if count > 0]
    if not items:
        fig = go.Figure()
        fig.add_annotation(text="No Missing Values Detected 🎉", showarrow=False, font=dict(size=16, color="#34D399"))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=240,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        return fig

    cols, counts = zip(*sorted(items, key=lambda x: x[1], reverse=True))
    fig = px.bar(
        x=cols, y=counts,
        labels={'x': 'Column', 'y': 'Missing Count'},
        color=counts,
        color_continuous_scale="Reds",
        title="Missing Values by Column"
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    return fig

def create_comparison_chart(before: Dict[str, Any], after: Dict[str, Any]) -> go.Figure:
    """Grouped bar chart for before and after metrics tuned for dark theme."""
    metrics = ['Missing Values', 'Duplicate Rows']
    b_vals = [before.get('total_missing', 0), before.get('duplicate_rows', 0)]
    a_vals = [after.get('remaining_missing', 0), after.get('remaining_duplicates', 0)]

    fig = go.Figure(data=[
        go.Bar(name='Before AutoPrep', x=metrics, y=b_vals, marker_color='#F87171'),
        go.Bar(name='After AutoPrep', x=metrics, y=a_vals, marker_color='#34D399')
    ])
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        barmode='group',
        title="Before vs. After AutoPrep AI Transformation",
        height=260,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
