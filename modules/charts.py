import plotly.express as px
import plotly.graph_objects as go
from config import COLORS

def create_bar_chart(df):
    """رسم بياني بالأعمدة للمقارنة السنوية/الفئات"""
    fig = px.bar(
        df, 
        barmode='group',
        color_discrete_sequence=[COLORS["navy_blue"], COLORS["dark_blue"], COLORS["teal"], COLORS["orange"]]
    )
    fig.update_layout(
        plot_bgcolor=COLORS["white"],
        paper_bgcolor=COLORS["white"],
        font_color=COLORS["text"],
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_line_chart(df):
    """رسم بياني خطي لمسار النمو الشهري"""
    fig = go.Figure()
    # افتراض بيانات خطية تجريبية أو من البيانات المتاحة
    fig.add_trace(go.Scatter(
        x=['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
        y=[2, 2, 3, 5, 7, 8, 10, 11],
        mode='lines+markers',
        line=dict(color=COLORS["dark_blue"], width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        plot_bgcolor=COLORS["white"],
        paper_bgcolor=COLORS["white"],
        font_color=COLORS["text"],
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig

def create_donut_chart(percentage, title, color):
    """رسم بياني دائري (Donut Chart) لمؤشرات الأداء"""
    fig = go.Figure(data=[go.Pie(
        values=[percentage, 100 - percentage],
        hole=0.75,
        marker_colors=[color, "#E2E8F0"],
        textinfo='none',
        hoverinfo='none'
    )])
    fig.update_layout(
        showlegend=False,
        annotations=[dict(text=f"{percentage}%", x=0.5, y=0.5, font_size=20, font_color=COLORS["text"], showarrow=False)],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=180
    )
    return fig
