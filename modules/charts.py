import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import COLORS

def plot_monthly_target_vs_actual(monthly_df):
    """رسم بياني بالأعمدة يجمع المستهدف والفعلي لكل شهر"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_df["Month"],
        y=monthly_df["Target"],
        name="المستهدف (Target)",
        marker_color=COLORS["navy_blue"]
    ))
    fig.add_trace(go.Bar(
        x=monthly_df["Month"],
        y=monthly_df["Actual"],
        name="الفعلي (Actual)",
        marker_color=COLORS["teal"]
    ))
    fig.update_layout(
        barmode="group",
        plot_bgcolor=COLORS["white"],
        paper_bgcolor=COLORS["white"],
        font_color=COLORS["text"],
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="الكمية"
    )
    return fig

def plot_monthly_growth_line(monthly_df):
    """رسم خطي لتطور المبيعات الفعلية مقابل المستهدفة شهرياً"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_df["Month"],
        y=monthly_df["Target"],
        mode="lines+markers",
        name="مسار المستهدف",
        line=dict(color=COLORS["orange"], width=2, dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=monthly_df["Month"],
        y=monthly_df["Actual"],
        mode="lines+markers",
        name="المبيعات الفعلية",
        line=dict(color=COLORS["dark_blue"], width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        plot_bgcolor=COLORS["white"],
        paper_bgcolor=COLORS["white"],
        font_color=COLORS["text"],
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_quarterly_comparison(quarterly_df):
    """مقارنة الأرباع الأربعة Q1 - Q4"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=quarterly_df["Quarter"],
        y=quarterly_df["Target"],
        name="مستهدف الربع",
        marker_color="#1E3A5F"
    ))
    fig.add_trace(go.Bar(
        x=quarterly_df["Quarter"],
        y=quarterly_df["Actual"],
        name="فعلي الربع",
        marker_color="#16A36A"
    ))
    fig.update_layout(
        barmode="group",
        plot_bgcolor=COLORS["white"],
        paper_bgcolor=COLORS["white"],
        font_color=COLORS["text"],
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_donut_chart(percentage, color):
    """رسم دائري ديناميكي يعرض نسبة التحقيق الحقيقية"""
    if percentage is None or pd.isna(percentage):
        display_val = 0
        label_text = "N/A"
    else:
        display_val = min(max(percentage, 0), 100)
        label_text = f"{percentage:.1f}%"

    fig = go.Figure(data=[go.Pie(
        values=[display_val, 100 - display_val],
        hole=0.75,
        marker_colors=[color, "#E2E8F0"],
        textinfo="none",
        hoverinfo="none",
        sort=False
    )])
    fig.update_layout(
        showlegend=False,
        annotations=[dict(text=label_text, x=0.5, y=0.5, font_size=20, font_weight="bold", font_color=COLORS["text"], showarrow=False)],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=5, r=5, t=5, b=5),
        height=160
    )
    return fig
