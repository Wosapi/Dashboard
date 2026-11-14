import plotly.express as px
import plotly.graph_objects as go
from config import COLORS

def plot_target_vs_actual(df):
    """إنشاء رسم بياني للمقارنة بين المستهدف والفعلي"""
    fig = go.Figure()
    # تخصيص الألوان والرسوم البيانية الاحترافية
    fig.update_layout(
        plot_bgcolor=COLORS["white"],
        paper_bgcolor=COLORS["white"],
        font_color=COLORS["text"]
    )
    return fig
