import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any

def create_score_gauge(score: float, title: str = "Quality Score") -> go.Figure:
    """Creates a sleek gauge chart for data quality score (0 to 100)."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20, 'color': "#1E293B"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': "#3B82F6"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [0, 50], 'color': '#FEE2E2'},
                {'range': [50, 75], 'color': '#FEF3C7'},
                {'range': [75, 100], 'color': '#DCFCE7'}
            ],
            'threshold': {
                'line': {'color': "#10B981", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(height=240, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def create_missing_chart(missing_dict: Dict[str, int]) -> go.Figure:
    """Bar chart for missing value counts per column."""
    items = [(col, count) for col, count in missing_dict.items() if count > 0]
    if not items:
        fig = go.Figure()
        fig.add_annotation(text="No Missing Values Detected 🎉", showarrow=False, font=dict(size=16, color="#10B981"))
        fig.update_layout(height=240, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    cols, counts = zip(*sorted(items, key=lambda x: x[1], reverse=True))
    fig = px.bar(
        x=cols, y=counts,
        labels={'x': 'Column', 'y': 'Missing Count'},
        color=counts,
        color_continuous_scale="Reds",
        title="Missing Values by Column"
    )
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
    return fig

def create_comparison_chart(before: Dict[str, Any], after: Dict[str, Any]) -> go.Figure:
    """Grouped bar chart for before and after metrics."""
    metrics = ['Missing Values', 'Duplicate Rows']
    b_vals = [before.get('total_missing', 0), before.get('duplicate_rows', 0)]
    a_vals = [after.get('remaining_missing', 0), after.get('remaining_duplicates', 0)]

    fig = go.Figure(data=[
        go.Bar(name='Before AutoPrep', x=metrics, y=b_vals, marker_color='#EF4444'),
        go.Bar(name='After AutoPrep', x=metrics, y=a_vals, marker_color='#10B981')
    ])
    fig.update_layout(
        barmode='group',
        title="Before vs. After AutoPrep AI Transformation",
        height=260,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
