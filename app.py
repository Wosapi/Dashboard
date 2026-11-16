import io
import json
import re
from datetime import timedelta
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Advanced Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Color system (one source of truth)
#   Brand      : navy / navy2
#   Series     : target (slate)  vs  actual (teal)
#   Status     : green >= 100 | amber 80-99 | red < 80
#   Products   : 4 clearly distinguishable hues
# ---------------------------------------------------------
C = {
    "navy": "#0B2545",
    "navy2": "#13315C",
    "teal": "#0E9F8E",
    "orange": "#F59E0B",
    "blue": "#38BDF8",
    "deep": "#1E3A8A",
    "bg": "#F1F5F9",
    "white": "#FFFFFF",
    "text": "#0F2540",
    "muted": "#52637A",
    "border": "#D9E2EC",
    "red": "#DC2626",
    "green": "#16A34A",
    "amber": "#D97706",
    "gray": "#E2E8F0",
    "target": "#334E68",
    "actual": "#0E9F8E",
}

PRODUCTS = ["Min", "Syn", "DEO", "Fluids"]

PCOLORS = {
    "Min": C["deep"],
    "Syn": C["orange"],
    "DEO": C["teal"],
    "Fluids": C["blue"],
}

MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

MONTH_AR = dict(zip(
    MONTHS,
    [
        "يناير", "فبراير", "مارس", "أبريل",
        "مايو", "يونيو", "يوليو", "أغسطس",
        "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    ]
))

TEXT = {
    "ar": {
        "title": "لوحة تحكم الأداء البيعي المتقدم",
        "subtitle": "تحليل شامل للمستهدف والمبيعات الفعلية",
        "data": "📂 مصدر البيانات",
        "upload": "ارفع ملف Excel",
        "filters": "🎛️ الفلاتر التفاعلية",
        "year": "📅 السنة",
        "products": "🛢️ المنتجات",
        "quarters": "🗓️ الأرباع",
        "target": "🎯 المستهدف",
        "actual": "💰 الفعلي",
        "achievement": "📈 معدل الإنجاز",
        "remaining": "⏳ المتبقي",
        "best_month": "🏆 أفضل شهر",
        "best_product": "⭐ أفضل منتج",
        "monthly": "الأداء الشهري لعام",
        "half": "تحليل النصف السنوي",
        "quarter": "تحليل الربع السنوي",
        "month": "تحليل الشهر",
        "variance": "⚖️ الفرق",
        "product_perf": "أداء المنتجات بالطن",
        "total_chart": "الإجمالي بالطن (فعلي مقابل مستهدف)",
        "daily": "جدول تحليل المبيعات اليومية",
        "daily_total": "إجمالي المبيعات اليومية",
        "active_customers": "العملاء النشطة",
        "qty_title": "كميات المنتجات بالكرتون",
        "qty_unit": "كرتون",
        "qty_total": "إجمالي الكمية",
        "tables": "الجداول التحليلية",
        "export": "تصدير التقارير",
        "download": "تحميل التقرير الشامل (Excel)",
        "no_data": "⚠️ لا توجد بيانات متاحة لهذه الفترة.",
        "select_half": "📆 اختر النصف",
        "select_quarter": "🗓️ اختر الربع",
        "select_month": "📅 اختر الشهر",
        "sales_count": "عدد العمليات",
        "total_i": "إجمالي الكمية",
        "customer_count": "عدد العملاء",
        "total_amount": "مبلغ المبيعات (SAR)",
        "all": "الكل",
        "na": "غير متاحة",
        "holiday": "إجازة",
        "holiday_note": "لا توجد مبيعات في شهر",
        "no_sales_yet": "لا توجد مبيعات مسجلة بعد في شهر",
        "footer": "العملة: ريال سعودي (SAR) · لوحة الأداء البيعي",
    },

    "en": {
        "title": "Advanced Sales Performance Dashboard",
        "subtitle": "Comprehensive analysis of targets and actual sales",
        "data": "📂 Data Source",
        "upload": "Upload Excel file",
        "filters": "🎛️ Interactive Filters",
        "year": "📅 Year",
        "products": "🛢️ Products",
        "quarters": "🗓️ Quarters",
        "target": "🎯 Target",
        "actual": "💰 Actual",
        "achievement": "📈 Achievement",
        "remaining": "⏳ Remaining",
        "best_month": "🏆 Best Month",
        "best_product": "⭐ Best Product",
        "monthly": "Monthly Performance for",
        "half": "Half-Year Analysis",
        "quarter": "Quarter Analysis",
        "month": "Month Analysis",
        "variance": "⚖️ Variance",
        "product_perf": "Products Performance (tons)",
        "total_chart": "Total in tons (Actual vs Target)",
        "daily": "Daily Sales Table Breakdown",
        "daily_total": "Daily Sales Total",
        "active_customers": "Active Customers",
        "qty_title": "Product Quantities (Cartons)",
        "qty_unit": "cartons",
        "qty_total": "Total Quantity",
        "tables": "Detailed Analytical Tables",
        "export": "Export Reports",
        "download": "Download Comprehensive Report (Excel)",
        "no_data": "⚠️ No data available for this period.",
        "select_half": "📆 Select half-year",
        "select_quarter": "🗓️ Select quarter",
        "select_month": "📅 Select month",
        "sales_count": "Transactions",
        "total_i": "Total Quantities",
        "customer_count": "Customers",
        "total_amount": "Sales Amount (SAR)",
        "all": "All",
        "na": "N/A",
        "holiday": "Holiday",
        "holiday_note": "No sales in",
        "no_sales_yet": "No sales recorded yet in",
        "footer": "Currency: Saudi Riyal (SAR) · Sales Performance Dashboard",
    },
}

# =========================================================
# 2. CSS DESIGN
# =========================================================

st.markdown(f"""
<style>
/* ---------- Base ---------- */
.stApp {{
    background:{C['bg']};
    color:{C['text']};
}}

.block-container {{
    max-width:1600px;
    padding:1rem 1.25rem 2rem;
}}

h1,h2,h3,h4,h5,h6 {{
    color:{C['text']};
}}

.stApp label,
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stWidgetLabel"] p {{
    color:{C['muted']} !important;
    font-weight:600;
}}

/* ---------- Metrics ---------- */
div[data-testid="stMetric"] {{
    background:{C['white']};
    border:1px solid {C['border']};
    border-inline-start:4px solid {C['teal']};
    border-radius:12px;
    padding:10px 12px;
    box-shadow:0 2px 8px rgba(11,37,69,.06);
    min-height:84px;
}}

div[data-testid="stMetricLabel"] {{
    color:{C['muted']};
    font-weight:700;
    font-size:.78rem;
}}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] * {{
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:clip !important;
    line-height:1.25;
}}

div[data-testid="stMetricValue"] {{
    color:{C['navy']};
    font-weight:800;
    font-size:clamp(1.05rem,1.7vw,1.55rem);
}}

/* ---------- Header ---------- */
.dashboard-header {{
    background:linear-gradient(112deg,#0B2545 0%,#13315C 62%,#0E8C8C 100%);
    border-radius:15px;
    padding:18px 24px;
    color:white;
    margin-bottom:15px;
    box-shadow:0 6px 18px rgba(11,37,69,.18);
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:12px;
}}

.dashboard-header h1 {{
    color:white!important;
    margin:0;
    font-size:clamp(1.2rem,2.4vw,2rem);
}}

.dashboard-header p {{
    color:#CFE0F1;
    margin:4px 0 0;
    font-size:.9rem;
}}

.year-pill {{
    color:white;
    font-weight:750;
    white-space:nowrap;
    padding:8px 14px;
    border:1px solid #ffffff40;
    border-radius:10px;
    background:#ffffff18;
}}

.section-heading {{
    background:linear-gradient(100deg,{C['navy']},{C['navy2']});
    color:white;
    padding:10px 14px;
    border-radius:11px;
    margin:4px 0 10px;
    font-size:1rem;
    font-weight:750;
}}

.panel-heading {{
    background:linear-gradient(100deg,{C['navy']},{C['navy2']});
    color:white;
    padding:10px 14px;
    border-radius:10px;
    margin:0 0 10px;
    font-size:0.95rem;
    font-weight:750;
    min-height:44px;
    display:flex;
    align-items:center;
}}

.holiday-badge {{
    background:#FEF3C7;
    border:1px solid {C['orange']};
    color:#92400E;
    padding:10px 14px;
    border-radius:10px;
    font-weight:750;
    font-size:0.92rem;
    margin:6px 0 10px;
    display:block;
    text-align:center;
}}

/* إخفاء تذييل Streamlit الافتراضي */
footer {{
    visibility:hidden;
}}

.app-footer {{
    text-align:center;
    color:{C['muted']};
    font-size:.78rem;
    padding:14px 0 4px;
    border-top:1px solid {C['border']};
    margin-top:18px;
}}

/* ---------- Cards: كل بانل داخل بطاقة بيضاء ---------- */
div[class*="st-key-card_"] {{
    background:{C['white']};
    border:1px solid {C['border']};
    border-radius:16px;
    padding:12px 14px 10px;
    box-shadow:0 4px 14px rgba(11,37,69,.07);
}}

/* ---------- شريط العنوان + القائمة المنسدلة (الصف فقط) ---------- */
div[class*="st-key-hdr_"] {{
    background:linear-gradient(100deg,{C['navy']},{C['navy2']});
    border-radius:10px;
    padding:6px 10px;
    margin-bottom:10px;
    min-height:44px;
}}

div[class*="st-key-hdr_"] div[data-testid="stHorizontalBlock"] {{
    align-items:center;
}}

div[class*="st-key-hdr_"] div[data-testid="stSelectbox"] {{
    width:100%;
    margin:0 !important;
}}

div[class*="st-key-hdr_"] div[data-baseweb="select"] > div {{
    min-height:32px !important;
    height:32px !important;
    border-radius:7px !important;
    border:1px solid rgba(255,255,255,.40) !important;
    background-color:rgba(255,255,255,.14) !important;
    padding-top:0 !important;
    padding-bottom:0 !important;
}}

div[class*="st-key-hdr_"] div[data-baseweb="select"] * {{
    color:white !important;
    font-weight:750 !important;
    font-size:.85rem !important;
}}

div[class*="st-key-hdr_"] div[data-baseweb="select"] svg {{
    fill:white !important;
}}

/* ---------- منع قص الدوائر والرسوم عند حواف الأعمدة ---------- */
div[data-testid="stPlotlyChart"],
div[data-testid="stPlotlyChart"] .js-plotly-plot,
div[data-testid="stPlotlyChart"] .main-svg {{
    overflow:visible !important;
}}

.pct-legend {{
    display:flex;
    flex-wrap:wrap;
    gap:14px;
    justify-content:center;
    font-size:.78rem;
    color:{C['muted']};
    margin:2px 0 6px;
}}

.pct-legend span::before {{
    content:"";
    display:inline-block;
    width:9px;
    height:9px;
    border-radius:50%;
    margin-inline-end:5px;
    background:var(--c);
}}

/* ---------- دوائر الإنجاز (شبكة SVG ثابتة لا تتبعثر) ---------- */
.dn-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    align-items: center;
    justify-items: center;
    padding: 4px 0;
    height: 232px;
}}

.dn {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    text-align: center;
}}

.dn svg {{
    display: block;
    width: 86px;
    height: 86px;
}}

.dn-sub {{
    font-size: .66rem;
    font-weight: 700;
    color: {C['muted']};
    direction: ltr;
    white-space: nowrap;
    margin-top: 2px;
}}

/* ---------- مربعات الكميات بالكرتون ---------- */
.qty-grid {{
    display:grid;
    grid-template-columns:repeat(auto-fit, minmax(76px, 1fr));
    gap:8px;
    margin:4px 0 6px;
}}

.qty-box {{
    background:{C['white']};
    border:1px solid {C['border']};
    border-top:4px solid var(--c);
    border-radius:12px;
    padding:9px 6px 8px;
    text-align:center;
    box-shadow:0 2px 8px rgba(11,37,69,.06);
}}

.qty-name {{
    font-size:.74rem;
    font-weight:700;
    color:{C['muted']};
}}

.qty-val {{
    font-size:1.12rem;
    font-weight:800;
    color:{C['navy']};
    direction:ltr;
    line-height:1.35;
}}

.qty-unit {{
    font-size:.64rem;
    font-weight:600;
    color:{C['muted']};
}}

.qty-total {{
    background:linear-gradient(100deg,{C['navy']},{C['navy2']});
    border-color:{C['navy']};
    border-top-color:{C['teal']};
}}

.qty-total .qty-name,
.qty-total .qty-val,
.qty-total .qty-unit {{
    color:#FFFFFF;
}}

/* ---------- Dataframe / tabs / radio ---------- */
div[data-testid="stDataFrame"] {{
    border:1px solid {C['border']};
    border-radius:10px;
    overflow:hidden;
}}

button[data-baseweb="tab"] {{
    color:{C['muted']};
    font-weight:700;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color:{C['teal']};
}}

div[data-baseweb="tab-highlight"] {{
    background-color:{C['teal']} !important;
}}

hr {{
    border:0;
    border-top:1px solid {C['border']};
    margin:0.85rem 0;
}}

@media(max-width:700px) {{
    .block-container {{
        padding:.6rem .55rem 1.5rem;
    }}
    .dashboard-header {{
        padding:13px;
    }}
    div[class*="st-key-card_"] {{
        padding:8px 8px 6px;
    }}
}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. LANGUAGE
# =========================================================

lang_choice = st.sidebar.selectbox(
    "🌍 Language / اللغة",
    ["العربية", "English"],
    index=0
)

lang = "ar" if lang_choice == "العربية" else "en"
t = TEXT[lang]

# =========================================================
# 4. READ EXCEL WORKBOOK
# =========================================================

@st.cache_data(show_spinner=False)
def load_sheets(file_bytes, filename):
    try:
        engine = "pyxlsb" if filename.lower().endswith(".xlsb") else None
        book = pd.ExcelFile(io.BytesIO(file_bytes), engine=engine)
        result = {}
        for name in book.sheet_names:
            df = pd.read_excel(book, sheet_name=name, header=0)
            df.columns = [
                str(c).strip() if not pd.isna(c) else f"Unnamed_{i}"
                for i, c in enumerate(df.columns)
            ]
            result[name] = df
        return result
    except Exception as exc:
        return {"__ERROR__": pd.DataFrame({"error": [str(exc)]})}


# =========================================================
# 5. TARGET SHEET PROCESSING
# =========================================================

def parse_target(raw):
    if raw is None or raw.empty:
        return None

    header_pos = None
    for pos, (_, row) in enumerate(raw.iterrows()):
        vals = [str(val).strip() for val in row.values if pd.notna(val)]
        if "Min" in vals and "Syn" in vals:
            header_pos = pos
            break

    if header_pos is None:
        return None

    year_row = raw.iloc[header_pos - 1] if header_pos > 0 else pd.Series(raw.columns)
    prod_row = raw.iloc[header_pos]

    mapping = {}
    current_year = None

    for j in range(2, len(raw.columns)):
        year_text = str(year_row.iloc[j])
        for y in range(2024, 2031):
            if str(y) in year_text:
                current_year = y
                break
        prod = str(prod_row.iloc[j]).strip()
        if prod in PRODUCTS and current_year is not None:
            mapping[j] = (current_year, prod)

    qmap = {m: f"Q{(i // 3) + 1}" for i, m in enumerate(MONTHS)}
    hmap = {m: ("H1" if i < 6 else "H2") for i, m in enumerate(MONTHS)}

    records = []
    current_month = None

    for _, row in raw.iloc[header_pos + 1:].iterrows():
        c0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        c1 = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""

        if any(x in c0.lower() for x in ["total", "annual", "ytd"]):
            break

        if c0 in MONTHS:
            current_month = c0

        if current_month and c1 in ["Target", "Actual"]:
            for j, (year, product) in mapping.items():
                records.append({
                    "Year": year,
                    "Month": current_month,
                    "Month_Num": MONTHS.index(current_month) + 1,
                    "Quarter": qmap[current_month],
                    "Half": hmap[current_month],
                    "Product": product,
                    "Type": c1,
                    "Value": pd.to_numeric(row.iloc[j], errors="coerce")
                })

    if not records:
        return None

    df = pd.DataFrame(records).pivot_table(
        index=["Year", "Month", "Month_Num", "Quarter", "Half", "Product"],
        columns="Type",
        values="Value",
        aggfunc="first"
    ).reset_index()

    df.columns.name = None

    for col in ["Target", "Actual"]:
        if col not in df:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.sort_values(["Year", "Month_Num", "Product"]).reset_index(drop=True)


# =========================================================
# 6. GENERAL CALCULATIONS
# =========================================================

def total(series):
    return series.sum(min_count=1) if series is not None else np.nan


def metrics(df):
    out = df.copy()
    out["Variance"] = out["Actual"] - out["Target"]
    out["Remaining"] = out["Target"] - out["Actual"]
    out["Achievement %"] = np.where(
        out["Target"].notna() & (out["Target"] > 0) & out["Actual"].notna(),
        out["Actual"] / out["Target"] * 100,
        np.nan
    )
    return out


def summary(df, groups):
    if df.empty:
        return pd.DataFrame(
            columns=groups + ["Target", "Actual", "Variance", "Remaining", "Achievement %"]
        )
    grouped = df.groupby(groups, as_index=False, sort=False).agg(
        Target=("Target", lambda s: s.sum(min_count=1)),
        Actual=("Actual", lambda s: s.sum(min_count=1))
    )
    return metrics(grouped)


def num(v):
    return "—" if pd.isna(v) else f"{v:,.2f}"


def pct(v):
    return "—" if pd.isna(v) else f"{v:.1f}%"


def status_color(rate):
    """لون حالة الإنجاز: أخضر >= 100 ، كهرماني 80-99 ، أحمر < 80"""
    if pd.isna(rate):
        return C["muted"]
    if rate >= 100:
        return C["green"]
    if rate >= 80:
        return C["amber"]
    return C["red"]


def find_holiday_months(df):
    """الأشهر التي لا توجد فيها مبيعات فعلية وتقع قبل آخر شهر فيه مبيعات (إجازة)."""
    if df is None or df.empty:
        return set()
    m = summary(df, ["Month_Num", "Month"])
    with_sales = m[m["Actual"].fillna(0) > 0]
    if with_sales.empty:
        return set()
    last = with_sales["Month_Num"].max()
    gap = m[(m["Month_Num"] < last) & (m["Actual"].fillna(0) <= 0)]
    return set(gap["Month"].tolist())


def style_table(df):
    """تنسيق الجداول التحليلية: أرقام + تلوين الإنجاز والفرق."""
    fmt = {
        "Target": "{:,.2f}", "Actual": "{:,.2f}", "Variance": "{:,.2f}",
        "Remaining": "{:,.2f}", "Achievement %": "{:.1f}%",
    }
    fmt = {k: v for k, v in fmt.items() if k in df.columns}
    styler = df.style.format(fmt, na_rep="—")
    apply_fn = styler.map if hasattr(styler, "map") else styler.applymap

    def achievement_color(v):
        if pd.isna(v):
            return ""
        return f"color:{status_color(v)}; font-weight:700"

    def variance_color(v):
        if pd.isna(v):
            return ""
        return f"color:{C['green'] if v >= 0 else C['red']}; font-weight:700"

    if "Achievement %" in df.columns:
        styler = apply_fn(achievement_color, subset=["Achievement %"])
    if "Variance" in df.columns:
        styler = apply_fn(variance_color, subset=["Variance"])
    return styler


# =========================================================
# 7. CHARTS
# =========================================================

def donut_html(actual, target, product):
    """دائرة إنجاز SVG ثابتة التموضع لا تتبعثر عند تحويل الصفحة إلى صورة."""
    valid = pd.notna(actual) and pd.notna(target) and target > 0
    rate = actual / target * 100 if valid else 0.0
    clamped = max(0.0, min(rate, 100.0))
    label = f"{rate:.1f}%" if valid else "N/A"
    label_color = status_color(rate) if valid else C["muted"]
    ring_color = PCOLORS[product]

    r = 35
    circ = 2 * np.pi * r
    dash = circ * (clamped / 100.0)

    svg = (
        f'<svg viewBox="0 0 88 88" width="86" height="86" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="44" cy="44" r="{r}" fill="none" stroke="{C["gray"]}" stroke-width="9"/>'
        f'<circle cx="44" cy="44" r="{r}" fill="none" stroke="{ring_color}" stroke-width="9" '
        f'stroke-dasharray="{dash:.2f} {circ:.2f}" stroke-linecap="round" '
        f'transform="rotate(-90 44 44)"/>'
        f'<text x="44" y="39" text-anchor="middle" font-family="Tahoma, Arial, sans-serif" '
        f'font-size="11" font-weight="700" fill="{C["muted"]}">{product}</text>'
        f'<text x="44" y="54" text-anchor="middle" font-family="Tahoma, Arial, sans-serif" '
        f'font-size="13" font-weight="800" fill="{label_color}">{label}</text>'
        f'</svg>'
    )

    return (
        f'<div class="dn" title="{product}: {label}">'
        f'{svg}'
        f'<div class="dn-sub">{num(actual)} / {num(target)}</div>'
        f'</div>'
    )


def qty_boxes_html(values):
    """5 مربعات: كراتين كل منتج (من شيت Data) + إجمالي الكراتين للشهر."""
    values = values or {}

    def qnum(v):
        return "—" if pd.isna(v) else f"{v:,.0f}"

    present = [values.get(p, np.nan) for p in PRODUCTS]
    present = [v for v in present if pd.notna(v)]
    total_qty = sum(present) if present else np.nan

    boxes = []
    for product in PRODUCTS:
        val = values.get(product, np.nan)
        boxes.append(
            f'<div class="qty-box" style="--c:{PCOLORS[product]}">'
            f'<div class="qty-name">{product}</div>'
            f'<div class="qty-val">{qnum(val)}</div>'
            f'<div class="qty-unit">{t["qty_unit"]}</div></div>'
        )
    boxes.append(
        f'<div class="qty-box qty-total" style="--c:{C["teal"]}">'
        f'<div class="qty-name">{t["qty_total"]}</div>'
        f'<div class="qty-val">{qnum(total_qty)}</div>'
        f'<div class="qty-unit">{t["qty_unit"]}</div></div>'
    )
    return f'<div class="qty-grid">{"".join(boxes)}</div>'


def total_bar_chart(period_label, actual, target, height=235):
    fig = go.Figure()

    fig.add_bar(
        x=[period_label], y=[target if pd.notna(target) else 0],
        name=t["target"], marker_color=C["target"],
        text=[num(target)], textposition="auto", textfont=dict(size=11, color="white")
    )

    fig.add_bar(
        x=[period_label], y=[actual if pd.notna(actual) else 0],
        name=t["actual"], marker_color=C["actual"],
        text=[num(actual)], textposition="auto", textfont=dict(size=11, color="white")
    )

    fig.update_layout(
        barmode="group", height=height, margin=dict(l=6, r=6, t=24, b=6),
        plot_bgcolor="white", paper_bgcolor="white", font=dict(color=C["text"], size=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9.5)),
        xaxis=dict(showgrid=False), yaxis=dict(rangemode="tozero", gridcolor=C["gray"]),
        bargap=0.28, bargroupgap=0.10
    )

    return fig


def monthly_chart(month_df, holidays=()):
    base = pd.DataFrame({"Month": MONTHS}).merge(
        month_df[["Month", "Target", "Actual"]], on="Month", how="left"
    )

    fig = go.Figure()

    fig.add_bar(
        x=base.Month, y=base.Target, name=t["target"], marker_color=C["target"],
        text=base.Target.map(lambda v: "" if pd.isna(v) else f"{v:.2f}"),
        textposition="inside", textfont=dict(color="white", size=10)
    )

    fig.add_bar(
        x=base.Month, y=base.Actual, name=t["actual"], marker_color=C["actual"],
        text=base.Actual.map(lambda v: "" if pd.isna(v) else f"{v:.2f}"),
        textposition="inside", textfont=dict(color="white", size=10)
    )

    # نسبة الإنجاز الشهرية (فعلي ÷ مستهدف) فوق كل شهر، بلون حالة الإنجاز
    for _, r in base.iterrows():
        tgt, act = r["Target"], r["Actual"]
        if pd.notna(tgt) and tgt > 0 and pd.notna(act) and act > 0:
            rate = act / tgt * 100
            col = status_color(rate)
            fig.add_annotation(
                x=r["Month"], y=max(tgt, act), text=f"<b>{rate:.0f}%</b>",
                showarrow=False, yshift=15,
                font=dict(size=10.5, color=col),
                bgcolor="white", bordercolor=col, borderwidth=1.2, borderpad=2
            )

    for m in holidays:
        row = base[base.Month == m]
        y_val = float(row.Target.iloc[0]) if not row.empty and pd.notna(row.Target.iloc[0]) else 0.0
        fig.add_annotation(
            x=m, y=y_val, text=f"🏖️ {t['holiday']}", showarrow=False, yshift=16,
            font=dict(size=11, color="#92400E"),
            bgcolor="#FEF3C7", bordercolor=C["orange"], borderwidth=1, borderpad=3
        )

    fig.update_layout(
        barmode="group", height=300, margin=dict(l=12, r=12, t=34, b=8),
        plot_bgcolor="white", paper_bgcolor="white", font=dict(color=C["text"], size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            rangemode="tozero", gridcolor=C["gray"],
            range=[0, float(np.nanmax(base[["Target", "Actual"]].to_numpy(dtype=float))) * 1.22]
            if base[["Target", "Actual"]].notna().to_numpy().any() else None
        ),
        bargap=.22, bargroupgap=.08
    )

    return fig


# =========================================================
# 8. RENDER PANEL WITH INTEGRATED SELECTOR IN HEADER
# =========================================================

def render_panel_with_selector(title, options, default_idx, year_df, filter_col, key, icon="📊"):
    current_val = st.session_state.get(key, options[default_idx])

    with st.container(key=f"card_{key}"):
        # شريط العنوان الأزرق (الصف فقط) + القائمة المنسدلة
        with st.container(key=f"hdr_{key}"):
            h_col, s_col = st.columns([2.5, 1], gap="small")
            with h_col:
                st.markdown(
                    f'<div style="color:white; font-weight:750; font-size:0.95rem; padding:2px 4px;">{icon} {title}</div>',
                    unsafe_allow_html=True
                )
            with s_col:
                selected_val = st.selectbox(
                    title,
                    options,
                    index=options.index(current_val) if current_val in options else default_idx,
                    key=key,
                    label_visibility="collapsed"
                )

        sub_data = year_df[year_df[filter_col] == selected_val]

        if sub_data.empty:
            st.info(t["no_data"])
            return selected_val

        if filter_col == "Month" and selected_val in HOLIDAY_MONTHS:
            st.markdown(
                f'<div class="holiday-badge">🏖️ ({t["holiday"]}) — {t["holiday_note"]} '
                f'{MONTH_AR[selected_val] if lang == "ar" else selected_val}</div>',
                unsafe_allow_html=True
            )

        target = total(sub_data.Target)
        actual = total(sub_data.Actual)
        variance = actual - target if pd.notna(actual) and pd.notna(target) else np.nan
        rate = actual / target * 100 if pd.notna(actual) and pd.notna(target) and target > 0 else np.nan

        a, b, c, d = st.columns(4)
        a.metric(t["variance"], num(variance))
        b.metric(t["achievement"], pct(rate))
        c.metric(t["actual"], num(actual))
        d.metric(t["target"], num(target))

        bar_col, donuts_col = st.columns([1, 1.4], gap="small")

        with bar_col:
            st.caption(f"📊 {t['total_chart']}")
            st.plotly_chart(
                total_bar_chart(selected_val, actual, target, height=238),
                use_container_width=True,
                config={"displayModeBar": False, "staticPlot": True},
                key=f"{key}_bar"
            )

        with donuts_col:
            st.caption(f"🎯 {t['product_perf']} · {selected_val}")
            cells = "".join(
                donut_html(
                    total(sub_data[sub_data.Product == product].Actual),
                    total(sub_data[sub_data.Product == product].Target),
                    product
                )
                for product in PRODUCTS
            )
            st.markdown(f'<div class="dn-grid">{cells}</div>', unsafe_allow_html=True)

        # مربعات الكميات بالكرتون (تتبع الشهر المختار) — في بانل تحليل الشهر فقط
        if filter_col == "Month":
            st.caption(f"📦 {t['qty_title']} · {selected_val}")
            qty = month_cartons(year, selected_val)
            if qty is None and carton_error:
                st.caption(f"⚠️ {carton_error}")
            st.markdown(qty_boxes_html(qty), unsafe_allow_html=True)

    return selected_val


# =========================================================
# 9. DAILY DATA - CORRECTED VERSION
# =========================================================

def clean_column_name(value):
    return str(value).replace("\n", " ").strip().lower()


def find_column(df, possible_names):
    normalized = {clean_column_name(col): col for col in df.columns}
    for name in possible_names:
        key = clean_column_name(name)
        if key in normalized:
            return normalized[key]
    return None


def parse_excel_date(series):
    # تواريخ إكسل الحقيقية تأتي جاهزة كـ datetime: نستخدمها كما هي دون إعادة تفسير
    if pd.api.types.is_datetime64_any_dtype(series):
        return pd.to_datetime(series, errors="coerce")

    result = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
    numeric = pd.to_numeric(series, errors="coerce")
    numeric_mask = numeric.notna() & (numeric > 20000) & (numeric < 80000)

    if numeric_mask.any():
        result.loc[numeric_mask] = pd.to_datetime(
            numeric.loc[numeric_mask], unit="D", origin="1899-12-30", errors="coerce"
        )

    text_mask = series.notna() & ~numeric_mask
    if text_mask.any():
        result.loc[text_mask] = pd.to_datetime(
            series.loc[text_mask].astype(str).str.strip(), errors="coerce", dayfirst=True
        )

    return result


def clean_numeric(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("SAR", "", regex=False)
        .str.replace("SR", "", regex=False)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "None": np.nan}),
        errors="coerce"
    )


def daily_data_from_sheet(sheets):
    sheet_name = next(
        (name for name in sheets if clean_column_name(name) in ["data", "بيانات"]),
        None
    )
    if sheet_name is None:
        return None, "لم يتم العثور على شيت Data."

    df = sheets[sheet_name].copy()
    if df.empty:
        return None, "شيت Data فارغ."

    date_col = find_column(df, ["Date", "التاريخ"])
    amount_col = find_column(df, ["Amount", "المبلغ"])
    quantity_col = find_column(df, ["Total Quantities", "Total Quantities ", "اجمالي الكميه", "إجمالي الكمية"])
    customer_no_col = find_column(df, ["Customer - No", "Customer-No", "رقم العميل"])
    customer_name_col = find_column(df, ["Customer - name", "Customer - Name", "اسم العميل"])
    invoice_col = find_column(df, ["Invoice No", "Invoice", "رقم الفاتورة"])

    missing = []
    if date_col is None: missing.append("Date")
    if amount_col is None: missing.append("Amount")
    if quantity_col is None: missing.append("Total Quantities")
    if customer_no_col is None: missing.append("Customer - No")

    if missing:
        return None, "الأعمدة التالية غير موجودة في شيت Data: " + ", ".join(missing)

    res = pd.DataFrame(index=df.index)
    res["Parsed_Date"] = parse_excel_date(df[date_col])
    res["Amount"] = clean_numeric(df[amount_col])
    res["Total_I"] = clean_numeric(df[quantity_col])
    res["Customer_No"] = df[customer_no_col].astype("string").str.strip()
    res["Customer_Name"] = df[customer_name_col].astype("string").str.strip() if customer_name_col else pd.NA
    res["Invoice_No"] = df[invoice_col].astype("string").str.strip() if invoice_col else pd.NA

    res = res.dropna(subset=["Parsed_Date"]).copy()

    has_amount = res["Amount"].notna() & (res["Amount"] != 0)
    has_quantity = res["Total_I"].notna() & (res["Total_I"] != 0)
    res = res[has_amount | has_quantity].copy()

    res["Customer_No"] = res["Customer_No"].replace({"": pd.NA, "nan": pd.NA, "<NA>": pd.NA})
    res["Date_Only"] = res["Parsed_Date"].dt.date
    res["Year"] = res["Parsed_Date"].dt.year
    res["Month_Num"] = res["Parsed_Date"].dt.month
    res["Month"] = res["Parsed_Date"].dt.strftime("%b")

    return res.reset_index(drop=True), None


# أعمدة الكراتين في شيت Data (بترقيم الأعمدة من 0: A=0 ... J=9):
# Min = J,K | Syn = L | DEO = M,N | Fluids = P,Q
CARTON_COLS = {"Min": [9, 10], "Syn": [11], "DEO": [12, 13], "Fluids": [15, 16]}


def _base_header(name):
    """اسم العمود بدون لاحقة التكرار التي يضيفها pandas (Min.1 -> min)."""
    return re.sub(r"\.\d+$", "", str(name).strip()).lower()


def product_cartons_from_sheet(sheets):
    """كراتين كل منتج لكل يوم من شيت Data (مجموع أعمدة المنتج)."""
    sheet_name = next(
        (name for name in sheets if clean_column_name(name) in ["data", "بيانات"]),
        None
    )
    if sheet_name is None:
        return None, "لم يتم العثور على شيت Data."

    df = sheets[sheet_name]
    date_col = find_column(df, ["Date", "التاريخ"])
    if date_col is None:
        return None, "عمود Date غير موجود في شيت Data."

    out = pd.DataFrame({"Parsed_Date": parse_excel_date(df[date_col])})

    for product, idxs in CARTON_COLS.items():
        # 1) حسب موقع العمود (J,K / L / M,N / P,Q) مع التحقق من اسم العنوان
        cols = [
            df.columns[i] for i in idxs
            if i < len(df.columns) and _base_header(df.columns[i]) == product.lower()
        ]
        # 2) إن لم يتطابق الموقع نبحث بالاسم
        if len(cols) != len(idxs):
            cols = [c for c in df.columns if _base_header(c) == product.lower()]

        if cols:
            vals = pd.concat([clean_numeric(df[c]) for c in cols], axis=1)
            out[product] = vals.sum(axis=1, min_count=1)
        else:
            out[product] = np.nan

    out = out.dropna(subset=["Parsed_Date"]).copy()
    out["Year"] = out["Parsed_Date"].dt.year
    out["Month_Num"] = out["Parsed_Date"].dt.month
    return out.reset_index(drop=True), None


def month_cartons(year_value, month_abbr):
    """كراتين المنتجات المختارة في الشهر المحدد (dict) أو None عند تعذر القراءة."""
    if carton_df is None:
        return None
    month_num = MONTHS.index(month_abbr) + 1
    sub = carton_df[
        (carton_df["Year"] == int(year_value)) & (carton_df["Month_Num"] == month_num)
    ]
    return {
        p: (total(sub[p]) if p in chosen_products else np.nan)
        for p in PRODUCTS
    }


# =========================================================
# 10. EXPORT FUNCTION
# =========================================================

def excel_bytes(sheet_map):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, frame in sheet_map.items():
            frame.to_excel(writer, sheet_name=name[:31], index=False)
    return output.getvalue()


# =========================================================
# 11. FILE UPLOADER
# =========================================================

st.sidebar.header(t["data"])
uploaded = st.sidebar.file_uploader(t["upload"], type=["xlsx", "xls", "xlsb"])

if uploaded is None:
    st.markdown(f"""
    <div class="dashboard-header">
        <div>
            <h1>📊 {t['title']}</h1>
            <p>{t['subtitle']} · Advanced Sales Performance Dashboard</p>
        </div>
        <div class="year-pill">📅 2026</div>
    </div>
    """, unsafe_allow_html=True)
    st.info("👈 ارفع ملف Excel للبدء / Upload your Excel workbook to begin.")
    st.stop()


# =========================================================
# 12. LOAD WORKBOOK
# =========================================================

sheets = load_sheets(uploaded.getvalue(), uploaded.name)
if "__ERROR__" in sheets:
    st.error(sheets["__ERROR__"].iloc[0, 0])
    st.stop()


# =========================================================
# 13. FIND TARGET SHEET
# =========================================================

target_name = next((name for name in sheets if clean_column_name(name) == "target"), None)
if target_name is None:
    st.error("⚠️ لم يتم العثور على شيت Target في الملف.")
    st.stop()

data = parse_target(sheets[target_name])
if data is None or data.empty:
    st.error("⚠️ تعذر قراءة شيت Target. تأكد من وجود أسماء المنتجات Min وSyn في صف العناوين.")
    st.stop()


# =========================================================
# 14. SIDEBAR FILTERS
# =========================================================

years = sorted(data.Year.dropna().unique().tolist())
st.sidebar.header(t["filters"])
year = st.sidebar.selectbox(t["year"], years, index=len(years) - 1)
chosen_products = st.sidebar.multiselect(t["products"], PRODUCTS, default=PRODUCTS)
chosen_quarters = st.sidebar.multiselect(t["quarters"], ["Q1", "Q2", "Q3", "Q4"], default=["Q1", "Q2", "Q3", "Q4"])

if not chosen_products:
    st.warning("⚠️ اختر منتجًا واحدًا على الأقل.")
    st.stop()


# =========================================================
# 15. DASHBOARD HEADER
# =========================================================

st.markdown(f"""
<div class="dashboard-header">
    <div>
        <h1>📊 {t['title']}</h1>
        <p>{t['subtitle']} · Advanced Sales Performance Dashboard</p>
    </div>
    <div class="year-pill">📅 {year}</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 15b. DOWNLOAD DASHBOARD AS IMAGE (PNG)
# =========================================================

IMAGE_EXPORT_HTML = """
<style>
  html, body { margin:0; padding:0; background:transparent; }
  button {
    width:100%; height:46px; border:0; border-radius:11px; cursor:pointer;
    background:linear-gradient(100deg,#0E9F8E,#0B7F73); color:#fff;
    font-family:Tahoma, Arial, sans-serif; font-size:15px; font-weight:700;
    box-shadow:0 3px 10px rgba(14,159,142,.35);
  }
  button:disabled { opacity:.7; cursor:wait; }
</style>
<button id="dl"></button>
<script>
(function () {
  var LABEL = __LABEL__, BUSY = __BUSY__, DONE = __DONE__, FAIL = __FAIL__, FILE = __FILE__;
  var SRCS = [
    "https://cdnjs.cloudflare.com/ajax/libs/html-to-image/1.11.11/html-to-image.min.js",
    "https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js",
    "https://unpkg.com/html-to-image@1.11.11/dist/html-to-image.js"
  ];
  var btn = document.getElementById("dl");
  btn.textContent = LABEL;
  var P = window.parent, pd = P.document;

  function loadLib(i) {
    return new Promise(function (resolve, reject) {
      if (P.htmlToImage) { resolve(); return; }
      if (i >= SRCS.length) { reject(new Error("library")); return; }
      var s = pd.createElement("script");
      s.src = SRCS[i];
      s.onload = function () { P.htmlToImage ? resolve() : loadLib(i + 1).then(resolve, reject); };
      s.onerror = function () { loadLib(i + 1).then(resolve, reject); };
      pd.head.appendChild(s);
    });
  }

  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  btn.addEventListener("click", async function () {
    btn.disabled = true;
    btn.textContent = BUSY;
    var holder = window.frameElement && window.frameElement.closest(
      '[data-testid="stElementContainer"], .element-container'
    );
    var oldDisplay = holder ? holder.style.display : "";
    try {
      await loadLib(0);
      var node = pd.querySelector('[data-testid="stMainBlockContainer"]') ||
                 pd.querySelector(".block-container");
      if (!node) { throw new Error("node"); }
      if (holder) { holder.style.display = "none"; }
      await sleep(300);
      var w = Math.max(node.scrollWidth, 1200);
      var h = node.scrollHeight;
      var opts = {
        backgroundColor: "#F1F5F9",
        pixelRatio: Math.min(2, 12000 / h),
        cacheBust: true,
        width: w,
        height: h,
        style: {
          width: w + "px",
          maxWidth: w + "px",
          transform: "none"
        },
        filter: function (n) { return !(n.tagName === "IFRAME"); }
      };
      var blob;
      try {
        blob = await P.htmlToImage.toBlob(node, opts);
      } catch (e1) {
        opts.skipFonts = true;
        blob = await P.htmlToImage.toBlob(node, opts);
      }
      if (!blob) { throw new Error("blob"); }
      var url = P.URL.createObjectURL(blob);
      var a = pd.createElement("a");
      a.href = url; a.download = FILE;
      pd.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { P.URL.revokeObjectURL(url); }, 5000);
      btn.textContent = DONE;
    } catch (err) {
      btn.textContent = FAIL;
    } finally {
      if (holder) { holder.style.display = oldDisplay; }
      setTimeout(function () { btn.textContent = LABEL; btn.disabled = false; }, 2800);
    }
  });
})();
</script>
"""

_export_labels = {
    "ar": ("📸 تحميل اللوحة كاملة (صورة PNG)", "⏳ جارٍ إنشاء الصورة...", "✅ تم تحميل الصورة", "⚠️ تعذّر إنشاء الصورة"),
    "en": ("📸 Download full dashboard (PNG)", "⏳ Creating image...", "✅ Image downloaded", "⚠️ Could not create image"),
}[lang]

components.html(
    IMAGE_EXPORT_HTML
    .replace("__LABEL__", json.dumps(_export_labels[0]))
    .replace("__BUSY__", json.dumps(_export_labels[1]))
    .replace("__DONE__", json.dumps(_export_labels[2]))
    .replace("__FAIL__", json.dumps(_export_labels[3]))
    .replace("__FILE__", json.dumps(f"Sales_Dashboard_{year}.png")),
    height=54,
)


# =========================================================
# 16. TARGET DATA FILTERING
# =========================================================

year_data = data[(data.Year == year) & data.Product.isin(chosen_products)].copy()
filtered = year_data[year_data.Quarter.isin(chosen_quarters)].copy()

# الأشهر التي لا توجد بها مبيعات (إجازة)
HOLIDAY_MONTHS = find_holiday_months(year_data)

# كراتين المنتجات من شيت Data (لمربعات تحليل الشهر)
carton_df, carton_error = product_cartons_from_sheet(sheets)


# =========================================================
# 17. EXECUTIVE KPIs
# =========================================================

target_total = total(filtered.Target)
actual_total = total(filtered.Actual)
achievement = actual_total / target_total * 100 if pd.notna(actual_total) and pd.notna(target_total) and target_total > 0 else np.nan
remaining = target_total - actual_total if pd.notna(actual_total) and pd.notna(target_total) else np.nan

month_summary = summary(filtered, ["Month_Num", "Month"]).sort_values("Month_Num")
best_month_rows = month_summary.dropna(subset=["Actual"])
best_month = best_month_rows.loc[best_month_rows.Actual.idxmax(), "Month"] if not best_month_rows.empty else t["na"]

product_summary = summary(filtered, ["Product"])
best_prod_rows = product_summary.dropna(subset=["Actual"])
best_product = best_prod_rows.loc[best_prod_rows.Actual.idxmax(), "Product"] if not best_prod_rows.empty else t["na"]

k = st.columns(6)
k[0].metric(t["target"], num(target_total))
k[1].metric(t["actual"], num(actual_total))
k[2].metric(t["achievement"], pct(achievement))
k[3].metric(t["remaining"], num(remaining))
k[4].metric(t["best_month"], MONTH_AR.get(best_month, best_month) if lang == "ar" else best_month)
k[5].metric(t["best_product"], best_product)


# =========================================================
# 18. MONTHLY PERFORMANCE
# =========================================================

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f'<div class="section-heading">📈 {t["monthly"]} {year}</div>', unsafe_allow_html=True)
st.plotly_chart(
    monthly_chart(month_summary, [m for m in month_summary.Month if m in HOLIDAY_MONTHS]),
    use_container_width=True,
    config={"displayModeBar": False, "staticPlot": True}
)
st.markdown(
    f'<div class="pct-legend">'
    f'<span style="--c:{C["green"]}">{"تحقق المستهدف ≥ 100%" if lang == "ar" else "Target met ≥ 100%"}</span>'
    f'<span style="--c:{C["amber"]}">{"قريب من المستهدف 80–99%" if lang == "ar" else "Near target 80–99%"}</span>'
    f'<span style="--c:{C["red"]}">{"أقل من المستهدف < 80%" if lang == "ar" else "Below target < 80%"}</span>'
    f'</div>',
    unsafe_allow_html=True
)
st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# 19. HALF-YEAR AND QUARTER ANALYSIS
# =========================================================

half_col, quarter_col = st.columns(2, gap="medium")

with half_col:
    render_panel_with_selector(
        title=t["half"],
        options=["H1", "H2"],
        default_idx=1,
        year_df=year_data,
        filter_col="Half",
        key="half_choice",
        icon="📆"
    )

with quarter_col:
    render_panel_with_selector(
        title=t["quarter"],
        options=["Q1", "Q2", "Q3", "Q4"],
        default_idx=2,
        year_df=year_data,
        filter_col="Quarter",
        key="quarter_choice",
        icon="🗓️"
    )

st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# 20. MONTH ANALYSIS + DAILY SALES
# =========================================================

month_col, daily_col = st.columns(2, gap="medium")

with month_col:
    month = render_panel_with_selector(
        title=t["month"],
        options=MONTHS,
        default_idx=10,
        year_df=year_data,
        filter_col="Month",
        key="month_choice",
        icon="📅"
    )
    # مكان إجمالي المبيعات اليومية (يُملأ لاحقاً من جدول المبيعات اليومية)
    totals_slot = st.container()

with daily_col:
    with st.container(key="card_daily"):
        st.markdown(f'<div class="panel-heading">📋 {t["daily"]}</div>', unsafe_allow_html=True)
        daily_df, daily_error = daily_data_from_sheet(sheets)

        if daily_error:
            st.error(daily_error)
        elif daily_df is None or daily_df.empty:
            st.warning("لا توجد بيانات مبيعات يومية صالحة في شيت Data.")
        else:
            year_daily = daily_df[daily_df["Year"] == int(year)].copy()
            selected_month_number = MONTHS.index(month) + 1
            dy_filtered = year_daily[year_daily["Month_Num"] == selected_month_number].copy()

            if year_daily.empty:
                st.info(f"لا توجد مبيعات مسجلة في عام {year}.")
            else:
                year_min = year_daily["Date_Only"].min()
                year_max = year_daily["Date_Only"].max()
                if dy_filtered.empty:
                    min_d, max_d = year_min, year_max
                else:
                    min_d = dy_filtered["Date_Only"].min()
                    max_d = dy_filtered["Date_Only"].max()

                is_holiday = (month in HOLIDAY_MONTHS) or (
                    selected_month_number < int(year_daily["Month_Num"].max())
                )

                filter_mode = st.radio(
                    "طريقة العرض:",
                    ["الشهر كاملاً", "تاريخ محدد", "نطاق تاريخي"],
                    horizontal=True,
                    key="daily_filter_mode"
                )

                daily_view = dy_filtered.copy()

                if filter_mode == "تاريخ محدد":
                    selected_date = st.date_input(
                        "اختر اليوم المطلوب:",
                        value=max_d,
                        min_value=year_min,
                        max_value=year_max,
                        key=f"daily_single_date_{year}_{month}"
                    )
                    if selected_date:
                        daily_view = year_daily[year_daily["Date_Only"] == selected_date]

                elif filter_mode == "نطاق تاريخي":
                    presets = ["مخصص", "آخر 7 أيام", "آخر 30 يوماً", "الشهر المحدد", "السنة كاملة"]
                    preset = st.selectbox(
                        "اختصار سريع:",
                        presets,
                        key=f"daily_preset_{year}_{month}"
                    )

                    if preset == "آخر 7 أيام":
                        start_d, end_d = max(year_min, year_max - timedelta(days=6)), year_max
                    elif preset == "آخر 30 يوماً":
                        start_d, end_d = max(year_min, year_max - timedelta(days=29)), year_max
                    elif preset == "الشهر المحدد":
                        start_d, end_d = min_d, max_d
                    elif preset == "السنة كاملة":
                        start_d, end_d = year_min, year_max
                    else:
                        date_range = st.date_input(
                            "اختر نطاق التواريخ:",
                            value=(min_d, max_d),
                            min_value=year_min,
                            max_value=year_max,
                            key=f"daily_date_range_{year}_{month}"
                        )
                        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                            start_d, end_d = date_range
                        else:
                            start_d, end_d = min_d, max_d
                            st.caption("ℹ️ اختر تاريخ النهاية لإكمال النطاق.")

                    daily_view = year_daily[
                        (year_daily["Date_Only"] >= start_d) &
                        (year_daily["Date_Only"] <= end_d)
                    ]
                    st.caption(f"📆 {start_d} ← {end_d}")

                if not daily_view.empty:
                    grouped_daily = (
                        daily_view.groupby("Date_Only", as_index=False)
                        .agg(
                            Sales_Count=("Amount", lambda s: s.notna().sum()),
                            Total_I_Sum=("Total_I", lambda s: s.sum(min_count=1)),
                            Customer_Count=("Customer_No", "nunique"),
                            Total_Amount=("Amount", lambda s: s.sum(min_count=1))
                        )
                        .sort_values("Date_Only", ascending=False)
                    )

                    display_daily = grouped_daily.rename(
                        columns={
                            "Date_Only": "التاريخ",
                            "Sales_Count": t["sales_count"],
                            "Total_I_Sum": t["total_i"],
                            "Customer_Count": t["customer_count"],
                            "Total_Amount": t["total_amount"]
                        }
                    )

                    format_dict = {
                        t["total_i"]: "{:,.2f}",
                        t["total_amount"]: "{:,.2f}"
                    }

                    st.dataframe(
                        display_daily.style.format(format_dict, na_rep="—"),
                        use_container_width=True,
                        hide_index=True,
                        height=260
                    )

                    with totals_slot:
                        with st.container(key="card_daily_totals"):
                            st.markdown(f"#### 📊 {t['daily_total']}")
                            m1, m2, m3 = st.columns(3)
                            m1.metric(t["active_customers"], f"{daily_view['Customer_No'].nunique():,}")
                            m2.metric(t["total_i"], num(daily_view["Total_I"].sum(min_count=1)))
                            m3.metric(t["total_amount"], num(daily_view["Amount"].sum(min_count=1)))
                else:
                    month_label = MONTH_AR[month] if lang == "ar" else month
                    if filter_mode == "الشهر كاملاً" and is_holiday:
                        st.markdown(
                            f'<div class="holiday-badge">🏖️ ({t["holiday"]}) — {t["holiday_note"]} {month_label}</div>',
                            unsafe_allow_html=True
                        )
                    elif filter_mode == "الشهر كاملاً":
                        st.info(f"{t['no_sales_yet']} {month_label}.")
                    else:
                        st.warning("لا توجد مبيعات في التاريخ المحدد.")


# =========================================================
# 21. ANALYTICAL TABLES
# =========================================================

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f'<div class="section-heading">📋 {t["tables"]}</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📅 Monthly Summary",
    "🛢️ Products Breakdown",
    "📆 Yearly Comparison"
])

with tab1:
    st.dataframe(
        style_table(month_summary.drop(columns=["Month_Num"], errors="ignore")),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    product_quarter = summary(filtered, ["Product", "Quarter"])
    st.dataframe(
        style_table(product_quarter),
        use_container_width=True,
        hide_index=True
    )

with tab3:
    yearly = summary(data[data.Product.isin(chosen_products)], ["Year"])
    st.dataframe(
        style_table(yearly),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 22. EXPORT REPORTS
# =========================================================

st.markdown(f'<div class="section-heading">📥 {t["export"]}</div>', unsafe_allow_html=True)

exports = {
    "Monthly_Summary": month_summary.drop(columns=["Month_Num"], errors="ignore"),
    "Half_Year": summary(year_data, ["Half"]),
    "Quarterly": summary(year_data, ["Quarter"]),
    "Products": product_summary,
    "Product_Quarter": product_quarter,
    "Yearly": yearly,
}

if daily_df is not None and not daily_df.empty:
    daily_export = daily_df.copy()
    daily_export["Parsed_Date"] = daily_export["Parsed_Date"].dt.strftime("%Y-%m-%d")
    exports["Daily_Sales"] = daily_export

st.download_button(
    "📥 " + t["download"],
    data=excel_bytes(exports),
    file_name=f"Sales_Analysis_{year}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.markdown(f'<div class="app-footer">{t["footer"]}</div>', unsafe_allow_html=True)
