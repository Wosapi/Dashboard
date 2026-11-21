import html
import io
import json
import re
from datetime import datetime, timedelta, timezone
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

# =========================================================
# COMPANY BRANDING (ترويسة كشف الحساب)
# =========================================================
COMPANY_AR = "شركة توتال السعودية للمنتجات البترولية المحدودة"
COMPANY_EN = "Saudi Total Petroleum Products Co. Ltd"
LOGO_B64 = "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"

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
        "area_title": "المبيعات حسب المنطقة",
        "year_analysis": "تحليل السنة",
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
        "area_title": "Sales by Area",
        "year_analysis": "Year Analysis",
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

/* ---------- المبيعات حسب المنطقة ---------- */
.area-list {{ display:flex; flex-direction:column; gap:8px; margin:4px 0 6px; }}
.area-row {{
    background:{C['white']};
    border:1px solid {C['border']};
    border-inline-start:4px solid var(--c);
    border-radius:12px;
    padding:9px 12px 8px;
    box-shadow:0 2px 8px rgba(11,37,69,.06);
}}
.area-top {{ display:flex; justify-content:space-between; align-items:baseline; gap:8px; }}
.area-name {{ font-weight:800; color:{C['navy']}; font-size:.92rem; }}
.area-qty {{ font-weight:800; color:{C['navy']}; font-size:1rem; direction:ltr; white-space:nowrap; }}
.area-qty small {{ font-weight:600; color:{C['muted']}; font-size:.66rem; }}
.area-bar {{ height:7px; background:#E2E8F0; border-radius:99px; margin:6px 0 5px; overflow:hidden; }}
.area-bar > span {{ display:block; height:100%; background:var(--c); border-radius:99px; }}
.area-prods {{ display:grid; grid-template-columns:repeat(4, 1fr); gap:6px; margin:2px 0 6px; }}
.area-prods .ap {{ background:#F8FAFC; border:1px solid {C['border']}; border-top:3px solid var(--c);
    border-radius:8px; text-align:center; padding:3px 2px 2px; }}
.area-prods .ap span {{ display:block; font-size:.62rem; font-weight:700; color:{C['muted']}; }}
.area-prods .ap b {{ font-size:.86rem; color:{C['navy']}; direction:ltr; }}
details.area-row > summary {{ list-style:none; cursor:pointer; outline:none; }}
details.area-row > summary::-webkit-details-marker {{ display:none; }}
.area-hint {{ font-size:.66rem; font-weight:700; color:{C['teal']}; margin-top:5px; }}
.area-hint::after {{ content:" ▾"; }}
details.area-row[open] .area-hint::after {{ content:" ▴"; }}
.area-det {{ margin-top:8px; max-height:300px; overflow:auto; border-top:1px dashed {C['border']}; padding-top:6px; }}
.area-tbl {{ width:100%; border-collapse:collapse; font-size:.74rem; }}
.area-tbl th {{ background:{C['navy']}; color:#fff; padding:5px 6px; font-weight:700; position:sticky; top:0; }}
.area-tbl td {{ padding:5px 6px; border-bottom:1px solid #EDF2F7; text-align:center; }}
.area-tbl td:first-child, .area-tbl th:first-child {{ text-align:right; }}
.area-tbl tr.tt td {{ background:#EAF0F7; font-weight:800; color:{C['navy']}; }}
.area-meta {{ display:flex; flex-wrap:wrap; gap:4px 12px; font-size:.72rem; font-weight:600; color:{C['muted']}; }}
.area-meta b {{ color:{C['navy']}; direction:ltr; unicode-bidi:plaintext; }}

/* ---------- كشف حساب العميل ---------- */
.stmt-banner {{
    background:linear-gradient(100deg,{C['navy']},{C['navy2']});
    border-radius:12px;
    border-inline-start:5px solid {C['teal']};
    padding:10px 14px;
    margin:6px 0 10px;
    color:#FFFFFF;
}}

.stmt-name {{
    font-weight:800;
    font-size:1rem;
    line-height:1.4;
}}

.stmt-meta {{
    font-size:.76rem;
    color:#CFE0F1;
    margin-top:2px;
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

_SLOTS = {}  # حاويات تُملأ لاحقاً (إجمالي المبيعات اليومية داخل تحليل الشهر)


def render_panel_with_selector(title, options, default_idx, year_df, filter_col, key, icon="📊"):
    mode = "شهري"
    months_in = None
    sel_key = key
    is_month_panel = filter_col == "Month"

    with st.container(key=f"card_{key}"):
        if filter_col == "Month":
            mode = st.radio(
                "نوع الفترة",
                ["شهري", "ربع سنوي", "نصف سنوي", "سنوي"],
                horizontal=True,
                key="period_mode",
                label_visibility="collapsed",
            )
            if mode == "ربع سنوي":
                options, filter_col, default_idx, sel_key = ["Q1", "Q2", "Q3", "Q4"], "Quarter", 2, f"{key}_q"
                title, icon = t["quarter"], "🗓️"
            elif mode == "نصف سنوي":
                options, filter_col, default_idx, sel_key = ["H1", "H2"], "Half", 1, f"{key}_h"
                title, icon = t["half"], "📆"
            elif mode == "سنوي":
                options, filter_col, default_idx, sel_key = [str(year)], None, 0, f"{key}_y"
                title, icon = t["year_analysis"], "📈"
        current_val = st.session_state.get(sel_key, options[default_idx])

        # شريط العنوان الأزرق (الصف فقط) + القائمة المنسدلة
        with st.container(key=f"hdr_{key}"):
            h_col, s_col = st.columns([2.5, 1], gap="small")
            with h_col:
                st.markdown(
                    f'<div style="color:white; font-weight:750; font-size:0.95rem; padding:2px 4px;">{icon} {title}</div>',
                    unsafe_allow_html=True
                )
            with s_col:
                if mode == "سنوي":
                    selected_val = options[0]
                    st.markdown(
                        f'<div style="color:white;font-weight:700;text-align:center;padding:6px 0">{selected_val}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    selected_val = st.selectbox(
                        title,
                        options,
                        index=options.index(current_val) if current_val in options else default_idx,
                        key=sel_key,
                        label_visibility="collapsed"
                    )

        if mode == "سنوي":
            sub_data = year_df
            months_in = list(range(1, 13))
        elif filter_col == "Quarter" and mode == "ربع سنوي":
            q = int(selected_val[1])
            months_in = list(range(3 * q - 2, 3 * q + 1))
            sub_data = year_df[year_df[filter_col] == selected_val]
        elif filter_col == "Half" and mode == "نصف سنوي":
            months_in = list(range(1, 7)) if selected_val == "H1" else list(range(7, 13))
            sub_data = year_df[year_df[filter_col] == selected_val]
        else:
            sub_data = year_df[year_df[filter_col] == selected_val]
            if filter_col == "Month":
                months_in = [MONTHS.index(selected_val) + 1]
        if is_month_panel:
            _SLOTS["months"] = months_in

        # الشهر الممثِّل للفترة (يُستخدم في جدول المبيعات اليومية): آخر شهر فيه فعلي
        ret_val = selected_val
        if is_month_panel and mode != "شهري":
            with_data = sub_data.dropna(subset=["Actual"]) if "Actual" in sub_data.columns else sub_data
            last_n = int(with_data["Month_Num"].max()) if not with_data.empty else months_in[-1]
            ret_val = MONTHS[last_n - 1]

        if sub_data.empty:
            st.info(t["no_data"])
            return ret_val

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
        if is_month_panel:
            st.caption(f"📦 {t['qty_title']} · {selected_val}")
            qty = period_cartons(year, months_in)
            if qty is None and carton_error:
                st.caption(f"⚠️ {carton_error}")
            st.markdown(qty_boxes_html(qty), unsafe_allow_html=True)

            # إجمالي المبيعات اليومية (يُملأ لاحقاً من جدول المبيعات اليومية) — أعلى المبيعات حسب المنطقة
            _SLOTS["totals"] = st.container()

            # المبيعات حسب المنطقة (العمود H) لنفس الشهر — مع خيارات إظهار/إخفاء
            st.caption(f"📍 {t['area_title']} · {selected_val}")
            areas_df = month_areas(year, months_in)
            if areas_df is not None and not areas_df.empty:
                all_areas = areas_df["Area"].tolist()
                picked_areas = st.multiselect(
                    "المناطق المعروضة (احذف منطقة لإخفائها)",
                    all_areas,
                    default=all_areas,
                    key=f"area_pick_{selected_val}",
                )
                o1, o2 = st.columns(2)
                with o1:
                    show_prods = st.toggle("تفصيل المنتجات", value=True, key=f"area_prods_{selected_val}")
                with o2:
                    sort_by = st.selectbox(
                        "الترتيب حسب",
                        ["الكراتين", "المبيعات", "العملاء"],
                        key=f"area_sort_{selected_val}",
                        label_visibility="collapsed",
                    )
                shown = areas_df[areas_df["Area"].isin(picked_areas)].copy()
                sort_col = {"الكراتين": "Cartons", "المبيعات": "Amount", "العملاء": "Customers"}[sort_by]
                shown = shown.sort_values(sort_col, ascending=False, na_position="last").reset_index(drop=True)
                month_total_c = areas_df["Cartons"].sum()
                if shown.empty:
                    st.info("اختر منطقة واحدة على الأقل لعرضها.")
                else:
                    st.caption(
                        f"المعروض: {shown['Cartons'].sum():,.0f} كرتون من {month_total_c:,.0f} "
                        f"· {num(shown['Amount'].sum())} SAR · {len(shown)} من {len(all_areas)} منطقة"
                    )
                    st.markdown(
                        area_cards_html(shown, month_total_c, show_prods, area_details(year, months_in)),
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(area_cards_html(areas_df), unsafe_allow_html=True)

            # تدقيق: مجموع كراتين المنتجات مقابل عمود الكمية الإجمالية
            mism = carton_mismatch(year, months_in)
            if mism is not None and not mism.empty:
                with st.expander(f"🔎 تدقيق الكراتين — {len(mism):,} صف فيه فرق بين المنتجات والكمية الإجمالية"):
                    st.caption(
                        "الكراتين في المناطق ومربعات المنتجات تُجمع من أعمدة المنتجات (Min / Syn / DEO / Fluids)، "
                        "بينما كشف الحساب يعتمد عمود الكمية الإجمالية. هذه الصفوف يختلف فيها الرقمان، "
                        "وغالباً فيها خطأ إدخال في خلية أحد المنتجات."
                    )
                    st.dataframe(mism, use_container_width=True, hide_index=True, height=min(360, 35 * (len(mism) + 1) + 3))

    return ret_val


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


SHUKRAN_COL_IDX = 35   # العمود AJ (كود شكران)
SHUKRAN_CUST_IDX = 31  # العمود AF (رقم العميل في الجدول الجانبي)


def normalize_pay_type(v):
    """العمود E: Cash -> نقد ، Credit -> آجل."""
    t = str(v).strip().lower() if pd.notna(v) else ""
    if t.startswith("cash") or "نقد" in t:
        return "نقد"
    if t.startswith("credit") or "آجل" in t or "اجل" in t or "أجل" in t:
        return "آجل"
    return "غير محدد"


def paid_flag(v):
    """العمود B: أي قيمة غير فارغة/غير صفرية في صف الفاتورة تعني أنها سُدّدت."""
    if pd.isna(v):
        return False
    t = str(v).strip().lower()
    if t in ("", "nan", "<na>", "none", "0", "0.0", "-", "false", "no", "لا"):
        return False
    return True


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
    # قيمة الفاتورة = العمود D (حسب ترتيب الشيت الحالي)، وإلا العمود المسمّى Amount
    res["Amount"] = clean_numeric(df.iloc[:, 3] if df.shape[1] > 3 else df[amount_col])
    res["Total_I"] = clean_numeric(df[quantity_col])
    res["Customer_No"] = df[customer_no_col].astype("string").str.strip()
    res["Customer_Name"] = df[customer_name_col].astype("string").str.strip() if customer_name_col else pd.NA
    # كود شكران: جدول العملاء الجانبي في الشيت (AF = رقم العميل، AJ = كود شكران)
    # مستقل عن صفوف الفواتير، فنبني قاموساً رقم العميل -> الكود ثم نربطه بالعميل
    res["Shukran_Code"] = pd.NA
    if df.shape[1] > SHUKRAN_COL_IDX:
        sk_code_col = next(
            (c for c in df.columns if "shukran" in str(c).lower()), df.columns[SHUKRAN_COL_IDX]
        )
        sk_no_col = df.columns[SHUKRAN_CUST_IDX]

        def _clean_id(series):
            out = series.astype("string").str.strip().str.replace(r"\.0+$", "", regex=True)
            return out.replace({"": pd.NA, "nan": pd.NA, "<NA>": pd.NA, "None": pd.NA})

        sk_tbl = pd.DataFrame({"no": _clean_id(df[sk_no_col]), "code": _clean_id(df[sk_code_col])}).dropna()
        sk_tbl = sk_tbl[sk_tbl["code"] != "0"].drop_duplicates("no", keep="first")
        code_map = dict(zip(sk_tbl["no"], sk_tbl["code"]))
        res["Shukran_Code"] = _clean_id(df[customer_no_col]).map(code_map).astype("string")
    res["Invoice_No"] = df[invoice_col].astype("string").str.strip() if invoice_col else pd.NA

    # E = نوع الفاتورة (Cash/Credit)
    # العمود نفسه يُكتشف بالعنوان (Cash/Credit) حتى لو تغيّر موضعه في الشيت
    type_col = next(
        (c for c in df.columns
         if "cash" in str(c).lower() and "credit" in str(c).lower()),
        None,
    ) or find_column(df, ["Payment Type", "Pay Type", "نوع الفاتورة", "نوع الدفع"])
    if type_col is None and invoice_col is not None:
        pos = list(df.columns).index(invoice_col) + 1
        type_col = df.columns[pos] if pos < df.shape[1] else None
    res["Pay_Type"] = df[type_col].map(normalize_pay_type) if type_col is not None else "غير محدد"
    # عمود السداد (A) = المبلغ المسدّد في نفس صف الفاتورة (قد يكون جزءاً من المبلغ)
    pay_series = df.iloc[:, 0]
    res["Paid_Flag"] = pay_series.map(paid_flag)
    res["Paid_Amt"] = clean_numeric(pay_series).fillna(0.0)

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


# أعمدة الكراتين في شيت Data (بترقيم الأعمدة من 0: A=0 ... L=11):
# كتلة المنتجات = L..S فقط (8 أعمدة تلي عمود التاريخ K مباشرة):
# Min = L,M | Syn = N | DEO = O,P | (Q فاصل) | Fluids = R,S
CARTON_COLS = {"Min": [11, 12], "Syn": [13], "DEO": [14, 15], "Fluids": [17, 18]}
CARTON_BLOCK_WIDTH = 8  # عدد أعمدة كتلة المنتجات بعد التاريخ (L..S)


# أسماء بديلة للمناطق (فارغ: كل قيمة في العمود H منطقة مستقلة، و T منطقة قائمة بذاتها)
AREA_ALIASES = {}


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

    # المنطقة (العمود H = Area)، وقيمة الفاتورة (D) ورقم العميل، لتحليل المبيعات حسب المنطقة
    area_col = find_column(df, ["Area", "المنطقة"])
    if area_col is None and df.shape[1] > 7:
        area_col = df.columns[7]
    area = df[area_col].astype("string").str.strip() if area_col is not None else pd.Series(pd.NA, index=df.index, dtype="string")
    area = area.replace({"": pd.NA, "nan": pd.NA, "<NA>": pd.NA, "None": pd.NA, "0": pd.NA})
    out["Area"] = area.map(lambda a: AREA_ALIASES.get(str(a).lower(), a) if pd.notna(a) else a)
    out["Amount"] = clean_numeric(df.iloc[:, 3]) if df.shape[1] > 3 else np.nan
    cust_col = find_column(df, ["Customer - No", "Customer-No", "رقم العميل"])
    out["Customer_No"] = (
        df[cust_col].astype("string").str.strip().str.replace(r"\.0+$", "", regex=True)
        if cust_col is not None else pd.NA
    )
    q_col = find_column(df, ["Total Quantities", "Total Quantities ", "اجمالي الكميه", "إجمالي الكمية"])
    out["Total_Q"] = clean_numeric(df[q_col]) if q_col is not None else np.nan
    cname_col = find_column(df, ["Customer - name", "Customer - Name", "اسم العميل"])
    out["Customer_Name"] = df[cname_col].astype("string").str.strip() if cname_col is not None else pd.NA
    inv_col = find_column(df, ["Invoice No", "Invoice", "رقم الفاتورة"])
    out["Invoice_No"] = df[inv_col].astype("string").str.strip() if inv_col is not None else pd.NA

    # كتلة أعمدة المنتجات تقع يمين أعمدة (الكمية / التاريخ). نحصر البحث في نافذة تلي آخرها
    # حتى لا تُلتقط أعمدة أخرى تحمل نفس الاسم (مثل جداول جانبية أو أعمدة السداد)
    cols_list = list(df.columns)
    anchors = [cols_list.index(c) for c in (date_col, q_col) if c is not None and c in cols_list]
    window = cols_list[max(anchors) + 1: max(anchors) + 1 + CARTON_BLOCK_WIDTH] if anchors else []

    for product, idxs in CARTON_COLS.items():
        # 1) داخل نافذة ما بعد التاريخ/الكمية (الأدق)
        cols = [c for c in window if _base_header(c) == product.lower()]
        # 2) حسب الموقع القديم مع التحقق من اسم العنوان
        if not cols:
            cols = [
                df.columns[i] for i in idxs
                if i < len(df.columns) and _base_header(df.columns[i]) == product.lower()
            ]
        # 3) آخر حل: بالاسم في كامل الشيت
        if not cols:
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


def period_cartons(year_value, month_nums):
    """كراتين المنتجات المختارة خلال مجموعة أشهر (شهر/ربع/نصف/سنة)."""
    if carton_df is None:
        return None
    sub = carton_df[
        (carton_df["Year"] == int(year_value)) & (carton_df["Month_Num"].isin(month_nums))
    ]
    return {p: (total(sub[p]) if p in chosen_products else np.nan) for p in PRODUCTS}


def _area_rows(year_value, month_nums):
    sub = carton_df[
        (carton_df["Year"] == int(year_value)) & (carton_df["Month_Num"].isin(month_nums))
    ].copy()
    sub = sub[sub["Area"].notna()]
    prods = [p for p in PRODUCTS if p in chosen_products and p in sub.columns]
    sub["Cartons"] = sub[prods].sum(axis=1, min_count=1) if prods else np.nan
    return sub[(sub["Cartons"].fillna(0) != 0) | (sub["Amount"].fillna(0) != 0)]


def carton_mismatch(year_value, month_nums):
    """صفوف يختلف فيها مجموع كراتين المنتجات عن عمود الكمية الإجمالية (Total Quantities)."""
    if carton_df is None or "Total_Q" not in carton_df.columns:
        return pd.DataFrame()
    sub = carton_df[
        (carton_df["Year"] == int(year_value)) & (carton_df["Month_Num"].isin(month_nums))
    ].copy()
    sub["Sum_Products"] = sub[[p for p in PRODUCTS if p in sub.columns]].sum(axis=1, min_count=1)
    diff = sub["Sum_Products"].fillna(0) - sub["Total_Q"].fillna(0)
    sub = sub[diff.abs() > 0.5].copy()
    sub["Diff"] = diff[sub.index]
    sub["Date"] = sub["Parsed_Date"].dt.strftime("%Y-%m-%d")
    cols = ["Date", "Customer_Name", "Customer_No", "Invoice_No", "Area"] + [
        p for p in PRODUCTS if p in sub.columns
    ] + ["Sum_Products", "Total_Q", "Diff"]
    out = sub[cols].rename(columns={
        "Date": "التاريخ", "Customer_Name": "العميل", "Customer_No": "رقم العميل",
        "Invoice_No": "رقم الفاتورة", "Area": "المنطقة", "Sum_Products": "مجموع المنتجات",
        "Total_Q": "الكمية الإجمالية", "Diff": "الفرق",
    })
    return out.sort_values("الفرق", key=lambda x: x.abs(), ascending=False).reset_index(drop=True)


def area_details(year_value, month_nums):
    """تفاصيل كل منطقة: العملاء (فواتير، كراتين، مبيعات) خلال الفترة."""
    if carton_df is None or "Area" not in carton_df.columns:
        return {}
    sub = _area_rows(year_value, month_nums)
    out = {}
    for area, g in sub.groupby("Area"):
        g = g.copy()
        g["Cust"] = g["Customer_Name"].fillna(g["Customer_No"]).fillna("—").astype(str)
        tbl = (
            g.groupby("Cust", as_index=False)
            .agg(
                Invoices=("Invoice_No", "nunique"),
                Cartons=("Cartons", lambda x: x.sum(min_count=1)),
                Amount=("Amount", lambda x: x.sum(min_count=1)),
            )
            .sort_values("Amount", ascending=False, na_position="last")
            .reset_index(drop=True)
        )
        out[area] = tbl
    return out


def month_areas(year_value, month_nums):
    """مبيعات الفترة مجمّعة حسب المنطقة: كراتين، مبلغ، عدد عملاء (أو None)."""
    if carton_df is None or "Area" not in carton_df.columns:
        return None
    sub = carton_df[
        (carton_df["Year"] == int(year_value)) & (carton_df["Month_Num"].isin(month_nums))
    ].copy()
    sub = sub[sub["Area"].notna()]
    if sub.empty:
        return pd.DataFrame(columns=["Area", "Cartons", "Amount", "Customers"] + list(PRODUCTS))
    prods = [p for p in PRODUCTS if p in chosen_products and p in sub.columns]
    sub["Cartons"] = sub[prods].sum(axis=1, min_count=1) if prods else np.nan
    sub = sub[(sub["Cartons"].fillna(0) != 0) | (sub["Amount"].fillna(0) != 0)]
    if sub.empty:
        return pd.DataFrame(columns=["Area", "Cartons", "Amount", "Customers"] + list(PRODUCTS))
    agg = {
        "Cartons": ("Cartons", lambda x: x.sum(min_count=1)),
        "Amount": ("Amount", lambda x: x.sum(min_count=1)),
        "Customers": ("Customer_No", "nunique"),
    }
    for p in PRODUCTS:
        if p in sub.columns:
            agg[p] = (p, lambda x: x.sum(min_count=1))
    res = (
        sub.groupby("Area", as_index=False)
        .agg(**agg)
        .sort_values(["Cartons", "Amount"], ascending=False, na_position="last")
        .reset_index(drop=True)
    )
    for p in PRODUCTS:
        if p not in res.columns or p not in chosen_products:
            res[p] = np.nan
    return res


AREA_COLORS = ["#0E9F8E", "#1E3A8A", "#F59E0B", "#38BDF8", "#8B5CF6", "#EC4899", "#64748B", "#16A34A"]


def area_cards_html(areas, month_total=None, show_products=True, details=None):
    """بطاقات المناطق: كراتين + شريط نسبة + تفصيل المنتجات + مبلغ + عدد العملاء."""
    if areas is None or areas.empty:
        return '<div class="area-meta">لا توجد مبيعات مسجّلة بمناطق في هذا الشهر.</div>'
    base = month_total if month_total else areas["Cartons"].sum()
    max_c = areas["Cartons"].max()
    rows = []
    for i, r in enumerate(areas.itertuples()):
        color = AREA_COLORS[i % len(AREA_COLORS)]
        c = 0 if pd.isna(r.Cartons) else r.Cartons
        share = (c / base * 100) if base else 0
        width = (c / max_c * 100) if max_c else 0
        amt = "—" if pd.isna(r.Amount) else f"{r.Amount:,.2f}"
        prods = ""
        if show_products:
            cells = "".join(
                f'<div class="ap" style="--c:{PCOLORS[p]}"><span>{p}</span>'
                f'<b>{"—" if pd.isna(getattr(r, p)) else f"{getattr(r, p):,.0f}"}</b></div>'
                for p in PRODUCTS
            )
            prods = f'<div class="area-prods">{cells}</div>'
        det_html = ""
        tbl = (details or {}).get(r.Area)
        if tbl is not None and not tbl.empty:
            trs = "".join(
                f'<tr><td>{html.escape(str(x.Cust))}</td><td>{int(x.Invoices):,}</td>'
                f'<td>{0 if pd.isna(x.Cartons) else x.Cartons:,.0f}</td>'
                f'<td>{0 if pd.isna(x.Amount) else x.Amount:,.2f}</td></tr>'
                for x in tbl.itertuples()
            )
            trs += (
                f'<tr class="tt"><td>الإجمالي</td><td>{int(tbl["Invoices"].sum()):,}</td>'
                f'<td>{tbl["Cartons"].sum():,.0f}</td><td>{tbl["Amount"].sum():,.2f}</td></tr>'
            )
            det_html = (
                '<div class="area-det"><table class="area-tbl"><thead><tr>'
                '<th>العميل</th><th>الفواتير</th><th>الكراتين</th><th>المبيعات (SAR)</th>'
                f'</tr></thead><tbody>{trs}</tbody></table></div>'
            )
        head = (
            f'<div class="area-top"><span class="area-name">📍 {html.escape(str(r.Area))}</span>'
            f'<span class="area-qty">{c:,.0f} <small>كرتون</small></span></div>'
            f'<div class="area-bar"><span style="width:{width:.1f}%"></span></div>'
            f'{prods}'
            f'<div class="area-meta"><span>النسبة: <b>{share:.1f}%</b></span>'
            f'<span>المبيعات: <b>{amt}</b> SAR</span>'
            f'<span>العملاء: <b>{int(r.Customers):,}</b></span></div>'
        )
        if det_html:
            rows.append(
                f'<details class="area-row" style="--c:{color}"><summary>{head}'
                f'<div class="area-hint">اضغط لعرض تفاصيل المبيعات</div></summary>{det_html}</details>'
            )
        else:
            rows.append(f'<div class="area-row" style="--c:{color}">{head}</div>')
    return f'<div class="area-list">{"".join(rows)}</div>'


# =========================================================
# 9b. CUSTOMER STATEMENT (كشف حساب وفواتير العملاء)
# =========================================================

CREDIT_MAX_DAYS = 30  # أقصى مدة سداد للفاتورة الآجلة (يوم)


def build_customer_tables(view):
    """فواتير العملاء وملخصهم (سحبيات / نقد / آجل / مسدّد / مديونية) من المبيعات المعروضة."""
    d = view.copy()
    for col in ["Customer_No", "Customer_Name", "Invoice_No"]:
        d[col] = d[col].astype("string").str.strip()
        d[col] = d[col].replace({"": pd.NA, "nan": pd.NA, "<NA>": pd.NA})

    for col in ["Customer_No", "Invoice_No"]:
        d[col] = d[col].str.replace(r"\.0+$", "", regex=True)

    if "Shukran_Code" not in d.columns:
        d["Shukran_Code"] = pd.NA
    d["Shukran_Code"] = d["Shukran_Code"].astype("string")
    if "Pay_Type" not in d.columns:
        d["Pay_Type"] = "غير محدد"
    if "Paid_Flag" not in d.columns:
        d["Paid_Flag"] = False
    d["_cash"] = d["Pay_Type"].eq("نقد")
    d["_credit"] = d["Pay_Type"].eq("آجل")
    d["Paid_Flag"] = d["Paid_Flag"].astype(bool)
    if "Paid_Amt" not in d.columns:
        d["Paid_Amt"] = 0.0
    d["Paid_Amt"] = d["Paid_Amt"].fillna(0.0)

    d["Customer_Key"] = d["Customer_No"].fillna(d["Customer_Name"]).fillna("غير محدد")

    # صف بلا رقم فاتورة يُعامل كفاتورة مستقلة حتى لا تُدمج الصفوف معاً
    fallback = pd.Series([f"—#{i}" for i in d.index], index=d.index, dtype="string")
    d["Invoice_Key"] = d["Invoice_No"].where(d["Invoice_No"].notna(), fallback)

    invoices = (
        d.groupby(["Customer_Key", "Invoice_Key"], as_index=False, sort=False)
        .agg(
            Customer_No=("Customer_No", "first"),
            Customer_Name=("Customer_Name", "first"),
            Date=("Parsed_Date", "min"),
            Quantity=("Total_I", lambda s: s.sum(min_count=1)),
            Amount=("Amount", lambda s: s.sum(min_count=1)),
            Cash_Any=("_cash", "any"),
            Credit_Any=("_credit", "any"),
            Paid_Any=("Paid_Flag", "any"),
            Paid_Raw=("Paid_Amt", "sum"),
            Shukran_Code=("Shukran_Code", "first"),
        )
    )
    invoices["Invoice_Show"] = invoices["Invoice_Key"].where(
        ~invoices["Invoice_Key"].str.startswith("—#"), "—"
    )
    invoices["Customer_Name"] = invoices["Customer_Name"].fillna(invoices["Customer_Key"])

    # نوع الفاتورة: آجل إن وُجد سطر آجل، وإلا نقد. الفاتورة الآجلة تُعتبر مسدّدة إذا وُجدت علامة سداد (العمود B)
    invoices["Pay_Type"] = np.where(
        invoices["Credit_Any"], "آجل", np.where(invoices["Cash_Any"], "نقد", "غير محدد")
    )
    amt = invoices["Amount"].fillna(0.0)
    is_credit = invoices["Pay_Type"].eq("آجل")
    is_cash = invoices["Pay_Type"].eq("نقد")
    # السداد = مبلغ العمود B في صف الفاتورة (لا يتجاوز مبلغها). المتبقي = المديونية
    paid_amt = np.minimum(invoices["Paid_Raw"].fillna(0.0).clip(lower=0.0), amt)
    invoices["Cash_Amount"] = amt.where(is_cash, 0.0)
    invoices["Credit_Amount"] = amt.where(is_credit, 0.0)
    invoices["Paid_Amount"] = paid_amt.where(is_credit, 0.0)
    invoices["Debt"] = (amt - paid_amt).where(is_credit, 0.0)
    invoices["Paid"] = is_credit & (invoices["Debt"] <= 0.005) & (invoices["Paid_Amount"] > 0)
    invoices["Partial"] = is_credit & (invoices["Debt"] > 0.005) & (invoices["Paid_Amount"] > 0)

    customers = (
        invoices.groupby("Customer_Key", as_index=False, sort=False)
        .agg(
            Customer_No=("Customer_No", "first"),
            Customer_Name=("Customer_Name", "first"),
            Invoices=("Invoice_Key", "nunique"),
            Quantity=("Quantity", lambda s: s.sum(min_count=1)),
            Amount=("Amount", lambda s: s.sum(min_count=1)),
            Cash=("Cash_Amount", "sum"),
            Credit=("Credit_Amount", "sum"),
            Paid=("Paid_Amount", "sum"),
            Debt=("Debt", "sum"),
            Shukran_Code=("Shukran_Code", "first"),
        )
        .sort_values("Amount", ascending=False, na_position="last")
        .reset_index(drop=True)
    )
    grand = customers["Amount"].sum()
    customers["Share"] = customers["Amount"] / grand * 100 if grand else np.nan
    return invoices, customers


def invoice_type_label(pay_type, paid, partial=False):
    """نص نوع الفاتورة في الكشف: نقد / آجل · مسدّد / آجل · مستحق."""
    if pay_type == "نقد":
        return "نقد"
    if pay_type == "آجل":
        if paid:
            return "آجل · مسدّد"
        return "آجل · جزئي" if partial else "آجل · مستحق"
    return "—"


def build_statement_table(inv):
    """كشف حساب عميل: الفواتير بالتاريخ + النوع (نقد/آجل) + إجمالي تراكمي + صف الإجمالي."""
    inv = inv.sort_values(["Date", "Invoice_Show"]).reset_index(drop=True)
    inv["Cumulative"] = inv["Amount"].fillna(0).cumsum()

    stmt = pd.DataFrame({
        "التاريخ": inv["Date"].dt.strftime("%Y-%m-%d"),
        "رقم الفاتورة": inv["Invoice_Show"].astype(str),
        "النوع": [invoice_type_label(p, bool(x), bool(y)) for p, x, y in zip(inv["Pay_Type"], inv["Paid"], inv["Partial"])],
        "الكمية (كرتون)": inv["Quantity"],
        "المبلغ (SAR)": inv["Amount"],
        "الإجمالي التراكمي (SAR)": inv["Cumulative"],
    })
    closing = pd.DataFrame([{
        "التاريخ": "الإجمالي",
        "رقم الفاتورة": f"{len(inv):,} فاتورة",
        "النوع": "",
        "الكمية (كرتون)": inv["Quantity"].sum(min_count=1),
        "المبلغ (SAR)": inv["Amount"].sum(min_count=1),
        "الإجمالي التراكمي (SAR)": inv["Cumulative"].iloc[-1],
    }])
    return pd.concat([stmt, closing], ignore_index=True)



def qfmt(v):
    """كمية بالكرتون: عدد صحيح بلا أصفار عشرية، وبرقمين فقط إن كانت كسرية."""
    if pd.isna(v):
        return "—"
    v = float(v)
    return f"{v:,.0f}" if abs(v - round(v)) < 1e-9 else f"{v:,.2f}"


STATEMENT_CSS = """
* { box-sizing: border-box; }
html, body { margin:0; padding:0; background:transparent; overflow-x:hidden;
  font-family:"Segoe UI", Tahoma, "Noto Sans Arabic", Arial, sans-serif; color:#0F2540; }
#sheet { background:#FFFFFF; border:1px solid #D9E2EC; border-radius:14px; padding:16px 16px 12px; width:100%;
  container-type:inline-size; }
.lh { display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:10px;
  padding-bottom:12px; border-bottom:3px solid #0B2545; }
.lh .ar { text-align:right; font-weight:800; font-size:14px; line-height:1.55; color:#0B2545; }
.lh .en { text-align:left; direction:ltr; font-weight:700; font-size:12px; line-height:1.55; color:#334E68; }
.lh img { height:56px; width:auto; display:block; }
.title { display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap; margin:12px 0 10px; }
.title b { font-size:15px; color:#0B2545; }
.title span { font-size:11.5px; color:#52637A; }
.cust { background:linear-gradient(100deg,#0B2545,#13315C); color:#FFFFFF; border-radius:10px;
  border-inline-start:5px solid #0E9F8E; padding:9px 12px; margin-bottom:10px; }
.cust .nm { font-weight:800; font-size:14px; line-height:1.5; }
.cust .mt { font-size:11.5px; color:#CFE0F1; margin-top:2px; }
.kpis { display:grid; grid-template-columns:repeat(4, 1fr); gap:8px; margin-bottom:10px; }
.kpi { border:1px solid #D9E2EC; border-top:3px solid #0E9F8E; border-radius:10px; padding:7px 9px; text-align:center; }
.kpi .l { font-size:11px; color:#52637A; font-weight:700; }
.kpi .v { font-size:16px; font-weight:800; color:#0B2545; direction:ltr; }
table { width:100%; border-collapse:collapse; font-size:12.5px; }
th { background:#0B2545; color:#FFFFFF; padding:7px 6px; font-weight:700; text-align:center; font-size:11.5px; }
td { padding:6px; border-bottom:1px solid #E2E8F0; text-align:center; white-space:nowrap; }
td.n { direction:ltr; font-variant-numeric:tabular-nums; }
tbody tr:nth-child(even) td { background:#F6F9FC; }
.bd { display:inline-block; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:700; }
.b-cash { background:#E3F6F3; color:#0B7F73; }
.b-paid { background:#E6F4EA; color:#1E7B3A; }
.b-part { background:#FEF3C7; color:#B45309; }
.b-due { background:#FDE8E8; color:#B42318; }
.kpi.kd-due { border-top-color:#D92D20; } .kpi.kd-due .v { color:#B42318; }
.kpi.kd-ok { border-top-color:#16A34A; } .kpi.kd-ok .v { color:#15803D; }
.acct { margin-top:10px; border:1px solid #D9E2EC; border-radius:10px; overflow:hidden; }
.acct .ah { background:#0B2545; color:#fff; font-weight:800; font-size:13px; padding:7px 12px; }
.acct .as { background:#F1F5F9; color:#52637A; font-size:11px; font-weight:700; padding:4px 12px; }
.acct .rw { display:flex; justify-content:space-between; gap:8px; padding:6px 12px; font-size:12.5px; border-bottom:1px solid #E2E8F0; }
.acct .rw b { direction:ltr; font-variant-numeric:tabular-nums; }
.acct .rw.due { background:#FDE8E8; color:#B42318; font-weight:800; }
.acct .rw.ok { background:#E6F4EA; color:#15803D; font-weight:800; }
tr.tot td { background:#E8EEF5 !important; font-weight:800; color:#0B2545; border-top:2px solid #0B2545; }
.foot { margin-top:8px; font-size:10.5px; color:#7A8AA0; display:flex; justify-content:space-between; gap:8px; flex-wrap:wrap; }
/* شاشة ضيقة (جوال): ترويسة مكدّسة وخط أصغر. الصورة المحمّلة بعرض 760 تبقى بالتخطيط العريض */
@container (max-width: 520px) {
  .lh { grid-template-columns:1fr; gap:6px; }
  .lh img { margin:0 auto; order:-1; height:48px; }
  .lh .ar, .lh .en { text-align:center; }
  .lh .ar { font-size:13px; }
  th { font-size:10px; padding:6px 3px; }
  td { font-size:11.5px; padding:6px 3px; }
  .kpis { grid-template-columns:repeat(2, 1fr); }
  .kpi .v { font-size:14px; }
  .acct .rw { font-size:11.5px; }
  th:last-child, td:last-child { display:none; }
  .kpi .l { font-size:10px; }
}
#dl { width:100%; height:44px; margin-top:10px; border:0; border-radius:11px; cursor:pointer;
  background:linear-gradient(100deg,#0E9F8E,#0B7F73); color:#FFFFFF; font-family:inherit;
  font-size:15px; font-weight:700; box-shadow:0 3px 10px rgba(14,159,142,.35); }
#dl:disabled { opacity:.7; cursor:wait; }
"""

STATEMENT_JS = """
(function () {
  var LABEL = __LABEL__, BUSY = __BUSY__, DONE = __DONE__, FAIL = __FAIL__, FILE = __FILE__;
  var SRCS = [
    "https://cdnjs.cloudflare.com/ajax/libs/html-to-image/1.11.11/html-to-image.min.js",
    "https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js",
    "https://unpkg.com/html-to-image@1.11.11/dist/html-to-image.js"
  ];
  var btn = document.getElementById("dl");
  var sheet = document.getElementById("sheet");
  var wrap = document.getElementById("wrap");
  btn.textContent = LABEL;

  function fit() {
    try {
      if (window.frameElement) {
        window.frameElement.style.height = (wrap.getBoundingClientRect().height + 6) + "px";
      }
    } catch (e) {}
  }
  fit();
  if (window.ResizeObserver) { new ResizeObserver(fit).observe(wrap); }
  window.addEventListener("load", fit);
  window.addEventListener("resize", fit);

  function loadLib(i) {
    return new Promise(function (resolve, reject) {
      if (window.htmlToImage) { resolve(); return; }
      if (i >= SRCS.length) { reject(new Error("library")); return; }
      var s = document.createElement("script");
      s.src = SRCS[i];
      s.onload = function () { window.htmlToImage ? resolve() : loadLib(i + 1).then(resolve, reject); };
      s.onerror = function () { loadLib(i + 1).then(resolve, reject); };
      document.head.appendChild(s);
    });
  }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  btn.addEventListener("click", async function () {
    btn.disabled = true;
    btn.textContent = BUSY;
    var oldW = sheet.style.width, oldMax = sheet.style.maxWidth;
    try {
      await loadLib(0);
      // عرض ثابت للصورة بغض النظر عن حجم الشاشة
      sheet.style.width = "760px";
      sheet.style.maxWidth = "760px";
      await sleep(250);
      var h = sheet.offsetHeight;
      var opts = { backgroundColor: "#FFFFFF", pixelRatio: 2, cacheBust: true, width: 760, height: h };
      var blob;
      try {
        blob = await window.htmlToImage.toBlob(sheet, opts);
      } catch (e1) {
        opts.skipFonts = true;
        blob = await window.htmlToImage.toBlob(sheet, opts);
      }
      if (!blob) { throw new Error("blob"); }
      var P = window.parent, pd = P.document;
      var url = P.URL.createObjectURL(blob);
      var a = pd.createElement("a");
      a.href = url; a.download = FILE;
      pd.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { P.URL.revokeObjectURL(url); }, 5000);
      btn.textContent = DONE;
    } catch (err) {
      btn.textContent = FAIL;
    } finally {
      sheet.style.width = oldW;
      sheet.style.maxWidth = oldMax;
      fit();
      setTimeout(function () { btn.textContent = LABEL; btn.disabled = false; }, 2800);
    }
  });
})();
"""


def statement_sheet_html(cust_name, cust_no, d_from, d_to, n_inv, qty, acct, stmt, file_name):
    """كشف حساب العميل كورقة HTML (ترويسة الشركة + الجدول + ملخص الحساب) مع زر تحميلها كصورة PNG."""
    esc = html.escape

    def badge(label):
        cls = {"نقد": "b-cash", "آجل · مسدّد": "b-paid", "آجل · مستحق": "b-due", "آجل · جزئي": "b-part"}.get(label)
        return f"<span class='bd {cls}'>{esc(label)}</span>" if cls else esc(label)

    rows = []
    for _, r in stmt.iloc[:-1].iterrows():
        rows.append(
            "<tr>"
            f"<td>{esc(str(r['التاريخ']))}</td>"
            f"<td>{esc(str(r['رقم الفاتورة']))}</td>"
            f"<td>{badge(str(r['النوع']))}</td>"
            f"<td class='n'>{qfmt(r['الكمية (كرتون)'])}</td>"
            f"<td class='n'>{num(r['المبلغ (SAR)'])}</td>"
            f"<td class='n'>{num(r['الإجمالي التراكمي (SAR)'])}</td>"
            "</tr>"
        )
    c = stmt.iloc[-1]
    rows.append(
        "<tr class='tot'>"
        f"<td>{esc(str(c['التاريخ']))}</td>"
        f"<td>{esc(str(c['رقم الفاتورة']))}</td>"
        "<td></td>"
        f"<td class='n'>{qfmt(c['الكمية (كرتون)'])}</td>"
        f"<td class='n'>{num(c['المبلغ (SAR)'])}</td>"
        f"<td class='n'>{num(c['الإجمالي التراكمي (SAR)'])}</td>"
        "</tr>"
    )

    def line(label, value, cls=""):
        return f"<div class='rw {cls}'><span>{label}</span><b>{num(value)}</b></div>"

    debt_all = float(acct["debt_all"])
    debt_cls = "due" if debt_all > 0.005 else "ok"
    account_box = (
        "<div class='acct'>"
        "<div class='ah'>ملخص الحساب</div>"
        "<div class='as'>خلال الفترة المحددة</div>"
        + line("إجمالي السحبيات (نقد + آجل)", acct["amount"])
        + line("مشتريات نقد", acct["cash"])
        + line("مشتريات آجل", acct["credit"])
        + line("المسدّد من الآجل", acct["paid"])
        + line("المديونية في الفترة (آجل غير مسدّد)", acct["debt_period"])
        + line("إجمالي المديونية على العميل", acct["debt_all"], debt_cls)
        + "</div>"
    )

    issued = datetime.now(timezone(timedelta(hours=3))).strftime("%Y-%m-%d %H:%M")
    js = (
        STATEMENT_JS
        .replace("__LABEL__", json.dumps("📸 تحميل كشف الحساب (صورة PNG)"))
        .replace("__BUSY__", json.dumps("⏳ جارٍ إنشاء الصورة..."))
        .replace("__DONE__", json.dumps("✅ تم تحميل الصورة"))
        .replace("__FAIL__", json.dumps("⚠️ تعذّر إنشاء الصورة"))
        .replace("__FILE__", json.dumps(file_name))
    )

    return (
        "<!doctype html><html dir='rtl' lang='ar'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<style>{STATEMENT_CSS}</style></head><body>"
        "<div id='wrap'>"
        "<div id='sheet'>"
        "<div class='lh'>"
        f"<div class='ar'>{esc(COMPANY_AR)}</div>"
        f"<img alt='logo' src='data:image/png;base64,{LOGO_B64}'>"
        f"<div class='en'>{esc(COMPANY_EN)}</div>"
        "</div>"
        "<div class='title'><b>كشف حساب عميل</b>"
        f"<span>من {esc(str(d_from))} إلى {esc(str(d_to))}</span></div>"
        "<div class='cust'>"
        f"<div class='nm'>👤 {esc(str(cust_name))}</div>"
        f"<div class='mt'>رقم العميل: {esc(str(cust_no))}</div>"
        "</div>"
        "<div class='kpis'>"
        f"<div class='kpi'><div class='l'>عدد الفواتير</div><div class='v'>{n_inv:,}</div></div>"
        f"<div class='kpi'><div class='l'>الكمية (كرتون)</div><div class='v'>{qfmt(qty)}</div></div>"
        f"<div class='kpi'><div class='l'>سحبيات الفترة (SAR)</div><div class='v'>{num(acct['amount'])}</div></div>"
        f"<div class='kpi kd-{debt_cls}'><div class='l'>إجمالي المديونية (SAR)</div><div class='v'>{num(debt_all)}</div></div>"
        "</div>"
        "<table><thead><tr>"
        "<th>التاريخ</th><th>رقم الفاتورة</th><th>النوع</th><th>الكمية (كرتون)</th>"
        "<th>المبلغ (SAR)</th><th>الإجمالي التراكمي (SAR)</th>"
        "</tr></thead><tbody>"
        + "".join(rows) +
        "</tbody></table>"
        + account_box +
        f"<div class='foot'><span>تاريخ الإصدار: {issued}</span>"
        "<span>الكميات بالكرتون · المبالغ بالريال السعودي (SAR)</span></div>"
        "</div>"
        "<button id='dl'></button>"
        "</div>"
        f"<script>{js}</script></body></html>"
    )


CODE128_PATTERNS = "212222 222122 222221 121223 121322 131222 122213 122312 132212 221213 221312 231212 112232 122132 122231 113222 123122 123221 223211 221132 221231 213212 223112 312131 311222 321122 321221 312212 322112 322211 212123 212321 232121 111323 131123 131321 112313 132113 132311 211313 231113 231311 112133 112331 132131 113123 113321 133121 313121 211331 231131 213113 213311 213131 311123 311321 331121 312113 312311 332111 314111 221411 431111 111224 111422 121124 121421 141122 141221 112214 112412 122114 122411 142112 142211 241211 221114 413111 241112 134111 111242 121142 121241 114212 124112 124211 411212 421112 421211 212141 214121 412121 111143 111341 131141 114113 114311 411113 411311 113141 114131 311141 411131 211412 211214 211232 2331112".split()


def code128_widths(text):
    """ترميز Code 128 (يختار C للأرقام الزوجية وإلا B) ويعيد أعراض الأشرطة/الفراغات كسلسلة أرقام."""
    text = str(text)
    if not text or any(ord(ch) < 32 or ord(ch) > 126 for ch in text):
        raise ValueError("code")
    if text.isdigit() and len(text) % 2 == 0 and len(text) >= 2:
        values = [105] + [int(text[i:i + 2]) for i in range(0, len(text), 2)]
    else:
        values = [104] + [ord(ch) - 32 for ch in text]
    check = (values[0] + sum(v * i for i, v in enumerate(values[1:], start=1))) % 103
    values += [check, 106]
    return "".join(CODE128_PATTERNS[v] for v in values)


def barcode_svg(widths, bar_h=150):
    """باركود كـ SVG (مع هامش هادئ 10 وحدات) بلا أي مكتبة خارجية."""
    quiet = 10
    x, rects = quiet, []
    for i, ch in enumerate(widths):
        w = int(ch)
        if i % 2 == 0:
            rects.append(f"<rect x='{x}' y='0' width='{w}' height='{bar_h}'/>")
        x += w
    total = x + quiet
    return (
        f"<svg viewBox='0 0 {total} {bar_h}' preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg' "
        f"class='bars' shape-rendering='crispEdges'><rect width='{total}' height='{bar_h}' fill='#fff'/>"
        f"<g fill='#000'>{''.join(rects)}</g></svg>"
    )


SHUKRAN_CSS = """
* { box-sizing:border-box; }
html, body { margin:0; padding:0; background:transparent; font-family:"Segoe UI", Tahoma, "Noto Sans Arabic", Arial, sans-serif; color:#0F2540; }
#card { background:#fff; border:1px solid #D9E2EC; border-radius:14px; padding:16px; text-align:center; }
.brand { display:flex; align-items:center; justify-content:center; gap:10px; padding-bottom:10px; border-bottom:3px solid #0B2545; }
.brand img { height:44px; width:auto; }
.brand b { font-size:15px; color:#0B2545; }
.cap { margin:12px 0 4px; font-weight:800; font-size:17px; color:#0B2545; }
.sub { color:#52637A; font-size:12px; margin-bottom:10px; }
.cust { background:linear-gradient(100deg,#0B2545,#13315C); color:#fff; border-radius:10px;
  border-inline-start:5px solid #0E9F8E; padding:9px 12px; text-align:right; margin-bottom:14px; }
.cust .nm { font-weight:800; font-size:14px; line-height:1.5; }
.cust .mt { font-size:11.5px; color:#CFE0F1; margin-top:2px; }
.bcbox { background:#fff; border:1px dashed #B8C4D3; border-radius:10px; padding:14px 10px 8px; }
.bars { width:100%; max-width:520px; height:120px; display:block; margin:0 auto; }
.code { direction:ltr; font-family:"Courier New", monospace; font-size:20px; font-weight:700; letter-spacing:3px; margin-top:6px; color:#000; word-break:break-all; }
#dl { width:100%; height:44px; margin-top:12px; border:0; border-radius:11px; cursor:pointer;
  background:linear-gradient(100deg,#0E9F8E,#0B7F73); color:#fff; font-family:inherit; font-size:15px; font-weight:700; }
#dl:disabled { opacity:.7; }
"""

SHUKRAN_JS = """
(function () {
  var W = __WIDTHS__, CODE = __CODE__, NAME = __NAME__, NO = __NO__, FILE = __FILE__, LOGO = __LOGO__;
  var LABEL = "📸 تحميل الباركود (صورة PNG)";
  var btn = document.getElementById("dl"), card = document.getElementById("card");
  btn.textContent = LABEL;
  function fit() { try { if (window.frameElement) window.frameElement.style.height = (card.getBoundingClientRect().height + 70) + "px"; } catch (e) {} }
  fit(); window.addEventListener("load", fit); window.addEventListener("resize", fit);

  function draw(img) {
    var M = 4, Q = 10, mods = 0, i;
    for (i = 0; i < W.length; i++) mods += +W[i];
    var bw = (mods + 2 * Q) * M, cw = Math.max(bw + 80, 760), ch = img ? 480 : 396;
    var c = document.createElement("canvas"); c.width = cw; c.height = ch;
    var g = c.getContext("2d");
    g.fillStyle = "#fff"; g.fillRect(0, 0, cw, ch);
    var y = 24;
    if (img) { var lh = 70, lw = img.width * lh / img.height; g.drawImage(img, (cw - lw) / 2, y, lw, lh); y += lh + 14; }
    g.textAlign = "center"; g.fillStyle = "#0B2545";
    g.font = "bold 26px Tahoma, Arial, sans-serif"; g.fillText("Shukran App", cw / 2, y + 22); y += 40;
    g.font = "bold 24px Tahoma, Arial, sans-serif"; g.direction = "rtl"; g.fillText(NAME, cw / 2, y + 22); y += 34;
    g.direction = "ltr"; g.fillStyle = "#52637A"; g.font = "18px Tahoma, Arial, sans-serif";
    g.fillText("Customer No: " + NO, cw / 2, y + 18); y += 40;
    var x = (cw - bw) / 2 + Q * M, bh = 190;
    g.fillStyle = "#000";
    for (i = 0; i < W.length; i++) { var w = +W[i] * M; if (i % 2 === 0) g.fillRect(x, y, w, bh); x += w; }
    y += bh + 34;
    g.fillStyle = "#000"; g.font = "bold 30px 'Courier New', monospace";
    g.fillText(CODE.split("").join(" "), cw / 2, y);
    return c;
  }
  function save(c) {
    c.toBlob(function (blob) {
      var P = window.parent, pd = P.document, url = P.URL.createObjectURL(blob);
      var a = pd.createElement("a"); a.href = url; a.download = FILE;
      pd.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { P.URL.revokeObjectURL(url); }, 5000);
      btn.textContent = "✅ تم تحميل الصورة";
      setTimeout(function () { btn.textContent = LABEL; btn.disabled = false; }, 2500);
    }, "image/png");
  }
  btn.addEventListener("click", function () {
    btn.disabled = true;
    var img = new Image();
    img.onload = function () { save(draw(img)); };
    img.onerror = function () { save(draw(null)); };
    img.src = LOGO;
  });
})();
"""


def shukran_card_html(cust_name, cust_no, code, file_name):
    """بطاقة باركود العميل (Code 128) مع تحميل PNG عالي الدقة مرسوم مباشرة على canvas."""
    esc = html.escape
    widths = code128_widths(code)
    js = (
        SHUKRAN_JS
        .replace("__WIDTHS__", json.dumps(widths))
        .replace("__CODE__", json.dumps(str(code)))
        .replace("__NAME__", json.dumps(str(cust_name)))
        .replace("__NO__", json.dumps(str(cust_no)))
        .replace("__FILE__", json.dumps(file_name))
        .replace("__LOGO__", json.dumps("data:image/png;base64," + LOGO_B64))
    )
    return (
        "<!doctype html><html dir='rtl' lang='ar'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<style>{SHUKRAN_CSS}</style></head><body>"
        "<div id='wrap'><div id='card'>"
        f"<div class='brand'><img alt='logo' src='data:image/png;base64,{LOGO_B64}'><b>{esc(COMPANY_AR)}</b></div>"
        "<div class='cap'>Shukran App</div><div class='sub'>باركود العميل · امسحه عند الكاشير</div>"
        f"<div class='cust'><div class='nm'>👤 {esc(str(cust_name))}</div><div class='mt'>رقم العميل: {esc(str(cust_no))}</div></div>"
        f"<div class='bcbox'>{barcode_svg(widths)}<div class='code'>{esc(str(code))}</div></div>"
        "<button id='dl'></button></div></div>"
        f"<script>{js}</script></body></html>"
    )


def render_customer_statement(all_df, default_view, year_value):
    """بطاقة كشف حساب وفواتير وإجمالي كميات ومديونية العملاء، بفترة مرنة قابلة للتغيير."""
    xlsx_mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    a_min, a_max = all_df["Date_Only"].min(), all_df["Date_Only"].max()
    dv_min, dv_max = default_view["Date_Only"].min(), default_view["Date_Only"].max()

    with st.container(key="card_statement"):
        st.markdown('<div class="panel-heading">🧾 كشف حساب وفواتير العملاء</div>', unsafe_allow_html=True)

        # ---------- فترة الكشف (مرنة) ----------
        presets = ["فترة الجدول اليومي", "آخر 7 أيام", "آخر 30 يوماً", "السنة كاملة", "نطاق مخصص"]
        preset = st.selectbox("📆 فترة الكشف", presets, key="stmt_period")

        if preset == "آخر 7 أيام":
            start_d, end_d = max(a_min, a_max - timedelta(days=6)), a_max
        elif preset == "آخر 30 يوماً":
            start_d, end_d = max(a_min, a_max - timedelta(days=29)), a_max
        elif preset == "السنة كاملة":
            yr = all_df[all_df["Year"] == int(year_value)]
            start_d, end_d = (yr["Date_Only"].min(), yr["Date_Only"].max()) if not yr.empty else (a_min, a_max)
        elif preset == "نطاق مخصص":
            picked = st.date_input(
                "اختر نطاق التواريخ:",
                value=(dv_min, dv_max),
                min_value=a_min,
                max_value=a_max,
                key="stmt_range",
            )
            if isinstance(picked, (tuple, list)) and len(picked) == 2:
                start_d, end_d = picked
            else:
                start_d, end_d = dv_min, dv_max
                st.caption("ℹ️ اختر تاريخ النهاية لإكمال النطاق.")
        else:
            start_d, end_d = dv_min, dv_max

        if preset == "فترة الجدول اليومي":
            view = default_view
        else:
            view = all_df[(all_df["Date_Only"] >= start_d) & (all_df["Date_Only"] <= end_d)]

        if view.empty:
            st.info("لا توجد مبيعات في الفترة المحددة.")
            return

        invoices, customers = build_customer_tables(view)

        # المديونية والسحبيات الإجمالية لكل عميل عبر كل الفترات (الرصيد الفعلي لا يتأثر بفلتر التاريخ)
        invoices_all, customers_all = build_customer_tables(all_df)
        all_map = customers_all.set_index("Customer_Key")
        customers["Debt_All"] = customers["Customer_Key"].map(all_map["Debt"]).fillna(0.0)
        customers["Amount_All"] = customers["Customer_Key"].map(all_map["Amount"]).fillna(0.0)

        d_min, d_max = view["Date_Only"].min(), view["Date_Only"].max()
        st.caption(
            f"📆 {d_min} ← {d_max}  ·  👥 {len(customers):,} عميل  ·  🧾 {len(invoices):,} فاتورة"
            f"  ·  💳 مديونية العملاء: {num(customers['Debt_All'].sum())}"
        )

        tab_sum, tab_cust, tab_credit, tab_shukran = st.tabs(
            ["👥 ملخص العملاء", "🧾 كشف حساب عميل", "💳 أرصدة العملاء الآجل", "🎫 Shukran App barcode"]
        )

        # ---------- ملخص العملاء ----------
        with tab_sum:
            summary_df = pd.DataFrame({
                "رقم العميل": customers["Customer_No"].fillna("—").astype(str),
                "اسم العميل": customers["Customer_Name"].astype(str),
                "الفواتير": customers["Invoices"],
                "الكمية (كرتون)": customers["Quantity"],
                "السحبيات (SAR)": customers["Amount"],
                "المديونية (SAR)": customers["Debt_All"],
                "% من الإجمالي": customers["Share"],
            })
            styler = summary_df.style.format(
                {
                    "الفواتير": "{:,.0f}",
                    "الكمية (كرتون)": qfmt,
                    "السحبيات (SAR)": "{:,.2f}",
                    "المديونية (SAR)": "{:,.2f}",
                    "% من الإجمالي": "{:.1f}%",
                },
                na_rep="—",
            )
            apply_fn = styler.map if hasattr(styler, "map") else styler.applymap
            styler = apply_fn(
                lambda v: f"color:{C['red']}; font-weight:700" if pd.notna(v) and v > 0.005 else "",
                subset=["المديونية (SAR)"],
            )
            st.dataframe(
                styler,
                use_container_width=True,
                hide_index=True,
                height=min(420, 35 * (len(summary_df) + 1) + 3),
            )

            summary_export = pd.DataFrame({
                "رقم العميل": customers["Customer_No"].fillna("—").astype(str),
                "اسم العميل": customers["Customer_Name"].astype(str),
                "الفواتير": customers["Invoices"],
                "الكمية (كرتون)": customers["Quantity"],
                "السحبيات (SAR)": customers["Amount"],
                "نقد (SAR)": customers["Cash"],
                "آجل (SAR)": customers["Credit"],
                "المسدّد من الآجل (SAR)": customers["Paid"],
                "مديونية الفترة (SAR)": customers["Debt"],
                "المديونية الكلية (SAR)": customers["Debt_All"],
            })
            invoices_export = pd.DataFrame({
                "رقم العميل": invoices["Customer_No"].fillna("—").astype(str),
                "اسم العميل": invoices["Customer_Name"].astype(str),
                "التاريخ": invoices["Date"].dt.strftime("%Y-%m-%d"),
                "رقم الفاتورة": invoices["Invoice_Show"].astype(str),
                "النوع": [invoice_type_label(p, bool(x), bool(y)) for p, x, y in zip(invoices["Pay_Type"], invoices["Paid"], invoices["Partial"])],
                "الكمية (كرتون)": invoices["Quantity"],
                "المبلغ (SAR)": invoices["Amount"],
            }).sort_values(["اسم العميل", "التاريخ"])

            st.download_button(
                "📥 تحميل ملخص العملاء والفواتير (Excel)",
                data=excel_bytes({"Customers": summary_export, "Invoices": invoices_export}),
                file_name=f"Customers_Summary_{d_min}_{d_max}.xlsx",
                mime=xlsx_mime,
                use_container_width=True,
                key="dl_customers_summary",
            )

        # ---------- كشف حساب عميل ----------
        with tab_cust:
            labels = {}
            for row in customers.itertuples():
                no = row.Customer_No
                name = str(row.Customer_Name)
                labels[row.Customer_Key] = (
                    f"{name} — {no}" if pd.notna(no) and str(no) != name else name
                )

            chosen = st.selectbox(
                "🔎 اختر العميل (اكتب للبحث):",
                list(labels.keys()),
                format_func=lambda k: labels[k],
            )

            cust = customers[customers["Customer_Key"] == chosen].iloc[0]
            inv = invoices[invoices["Customer_Key"] == chosen].copy()
            stmt = build_statement_table(inv)

            acct = {
                "amount": cust["Amount"],
                "cash": cust["Cash"],
                "credit": cust["Credit"],
                "paid": cust["Paid"],
                "debt_period": cust["Debt"],
                "amount_all": cust["Amount_All"],
                "debt_all": cust["Debt_All"],
            }

            cust_no = "—" if pd.isna(cust["Customer_No"]) else str(cust["Customer_No"])
            safe_name = re.sub(r"[^\w\-]+", "_", str(cust["Customer_Name"])).strip("_")[:40] or "customer"

            components.html(
                statement_sheet_html(
                    cust["Customer_Name"], cust_no, d_min, d_max,
                    int(cust["Invoices"]), cust["Quantity"], acct,
                    stmt, f"Statement_{safe_name}_{d_min}_{d_max}.png",
                ),
                height=820 + 32 * len(stmt),
                scrolling=False,
            )

        # ---------- أرصدة العملاء الآجل + تنبيهات تجاوز المهلة ----------
        with tab_credit:
            today = datetime.now(timezone(timedelta(hours=3))).date()
            debt_inv = invoices_all[invoices_all["Debt"] > 0.005].copy()
            if debt_inv.empty:
                st.success("✅ لا توجد أرصدة آجلة مستحقة على أي عميل.")
            else:
                debt_inv["Age"] = (pd.Timestamp(today) - debt_inv["Date"].dt.normalize()).dt.days
                debt_inv["Due"] = debt_inv["Date"].dt.normalize() + pd.Timedelta(days=CREDIT_MAX_DAYS)
                debt_inv["Over"] = debt_inv["Age"] > CREDIT_MAX_DAYS
                debt_inv["Over_Debt"] = debt_inv["Debt"].where(debt_inv["Over"], 0.0)

                bal = (
                    debt_inv.groupby("Customer_Key", as_index=False, sort=False)
                    .agg(
                        Customer_No=("Customer_No", "first"),
                        Customer_Name=("Customer_Name", "first"),
                        Open_Invoices=("Invoice_Key", "nunique"),
                        Debt=("Debt", "sum"),
                        Over_Debt=("Over_Debt", "sum"),
                        Over_Count=("Over", "sum"),
                        Oldest=("Date", "min"),
                        Max_Age=("Age", "max"),
                    )
                    .sort_values(["Over_Debt", "Max_Age"], ascending=False)
                    .reset_index(drop=True)
                )

                def status_of(age):
                    if age > CREDIT_MAX_DAYS:
                        return "🔴 متجاوز المهلة"
                    if age >= CREDIT_MAX_DAYS - 7:
                        return "🟠 قارب الانتهاء"
                    return "🟢 ضمن المهلة"

                bal["Status"] = bal["Max_Age"].map(status_of)

                n_over = int((bal["Over_Count"] > 0).sum())
                n_soon = int((bal["Status"] == "🟠 قارب الانتهاء").sum())
                if n_over:
                    st.error(
                        f"🚨 تنبيه: {n_over:,} عميل تجاوزت فواتيره الآجلة {CREDIT_MAX_DAYS} يوماً "
                        f"({int(bal['Over_Count'].sum()):,} فاتورة) بمبلغ متأخر {num(bal['Over_Debt'].sum())} SAR."
                    )
                if n_soon:
                    st.warning(f"⏳ {n_soon:,} عميل قارب على انتهاء مهلة {CREDIT_MAX_DAYS} يوماً (خلال 7 أيام).")
                if not n_over and not n_soon:
                    st.success(f"✅ جميع الفواتير الآجلة ضمن مهلة {CREDIT_MAX_DAYS} يوماً.")

                c1, c2, c3 = st.columns(3)
                c1.metric("إجمالي أرصدة الآجل (SAR)", num(bal["Debt"].sum()))
                c2.metric("المتأخر عن المهلة (SAR)", num(bal["Over_Debt"].sum()))
                c3.metric("عملاء عليهم رصيد", f"{len(bal):,}")

                bal_df = pd.DataFrame({
                    "الحالة": bal["Status"],
                    "رقم العميل": bal["Customer_No"].fillna("—").astype(str),
                    "اسم العميل": bal["Customer_Name"].astype(str),
                    "فواتير مفتوحة": bal["Open_Invoices"],
                    "الرصيد (SAR)": bal["Debt"],
                    "المتأخر (SAR)": bal["Over_Debt"],
                    "أقدم فاتورة": bal["Oldest"].dt.strftime("%Y-%m-%d"),
                    "أقصى عمر (يوم)": bal["Max_Age"],
                })
                st.dataframe(
                    bal_df.style.format(
                        {"فواتير مفتوحة": "{:,.0f}", "الرصيد (SAR)": "{:,.2f}",
                         "المتأخر (SAR)": "{:,.2f}", "أقصى عمر (يوم)": "{:,.0f}"}
                    ),
                    use_container_width=True,
                    hide_index=True,
                    height=min(420, 35 * (len(bal_df) + 1) + 3),
                )

                det = debt_inv.sort_values(["Over", "Age"], ascending=False)
                det_df = pd.DataFrame({
                    "الحالة": np.where(det["Over"], "🔴 متجاوزة", "🟢 ضمن المهلة"),
                    "رقم العميل": det["Customer_No"].fillna("—").astype(str).values,
                    "اسم العميل": det["Customer_Name"].astype(str).values,
                    "رقم الفاتورة": det["Invoice_Show"].astype(str).values,
                    "تاريخ الفاتورة": det["Date"].dt.strftime("%Y-%m-%d").values,
                    "آخر موعد للسداد": det["Due"].dt.strftime("%Y-%m-%d").values,
                    "العمر (يوم)": det["Age"].values,
                    "المبلغ (SAR)": det["Amount"].values,
                    "المسدّد (SAR)": det["Paid_Amount"].values,
                    "المتبقي (SAR)": det["Debt"].values,
                })
                with st.expander("📄 تفاصيل الفواتير الآجلة المفتوحة"):
                    st.dataframe(
                        det_df.style.format(
                            {"العمر (يوم)": "{:,.0f}", "المبلغ (SAR)": "{:,.2f}",
                             "المسدّد (SAR)": "{:,.2f}", "المتبقي (SAR)": "{:,.2f}"}
                        ),
                        use_container_width=True,
                        hide_index=True,
                        height=min(420, 35 * (len(det_df) + 1) + 3),
                    )

                st.download_button(
                    "📥 تحميل أرصدة الآجل (Excel)",
                    data=excel_bytes({"Credit_Balances": bal_df, "Open_Invoices": det_df}),
                    file_name=f"Credit_Balances_{today}.xlsx",
                    mime=xlsx_mime,
                    use_container_width=True,
                    key="dl_credit_balances",
                )
                st.caption(f"ℹ️ الأرصدة محسوبة من كل الفترات بغض النظر عن فلتر التاريخ. المهلة {CREDIT_MAX_DAYS} يوماً من تاريخ الفاتورة.")

        # ---------- باركود Shukran App (العمود AJ) ----------
        with tab_shukran:
            coded = customers_all[customers_all["Shukran_Code"].notna()].copy()
            if coded.empty:
                st.info("لا توجد أكواد شكران في العمود AJ من شيت Data.")
            else:
                coded = coded.sort_values("Customer_Name")
                sk_labels = {}
                for row in coded.itertuples():
                    no = row.Customer_No
                    nm = str(row.Customer_Name)
                    sk_labels[row.Customer_Key] = f"{nm} — {no}" if pd.notna(no) and str(no) != nm else nm
                st.caption(f"🎫 {len(coded):,} عميل لديه كود شكران (من كل الفترات).")
                sk_key = st.selectbox(
                    "🔎 اختر العميل (اكتب للبحث):",
                    list(sk_labels.keys()),
                    format_func=lambda k: sk_labels[k],
                    key="shukran_customer",
                )
                sk = coded[coded["Customer_Key"] == sk_key].iloc[0]
                sk_no = "—" if pd.isna(sk["Customer_No"]) else str(sk["Customer_No"])
                sk_code = str(sk["Shukran_Code"])
                sk_safe = re.sub(r"[^\w\-]+", "_", str(sk["Customer_Name"])).strip("_")[:40] or "customer"
                try:
                    components.html(
                        shukran_card_html(sk["Customer_Name"], sk_no, sk_code, f"Shukran_{sk_safe}_{sk_code}.png"),
                        height=560,
                        scrolling=False,
                    )
                except ValueError:
                    st.warning(f"⚠️ الكود «{sk_code}» يحتوي رموزاً لا يدعمها Code 128، تعذّر إنشاء الباركود.")



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
    # إجمالي المبيعات اليومية يظهر داخل تحليل الشهر أعلى المبيعات حسب المنطقة (إن لم يتوفر فهنا)
    totals_slot = _SLOTS.get("totals") or st.container()

with daily_col:
    statement_view = None  # الفترة المعروضة، تُستخدم في كشف حساب العملاء أسفل الجدول
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
            period_nums = _SLOTS.get("months") or [selected_month_number]
            dy_filtered = year_daily[year_daily["Month_Num"].isin(period_nums)].copy()

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

                is_holiday = len(period_nums) == 1 and (
                    (month in HOLIDAY_MONTHS)
                    or (selected_month_number < int(year_daily["Month_Num"].max()))
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

                    statement_view = daily_view
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

    # كشف حساب وفواتير وإجمالي كميات العملاء (تحت الجدول اليومي)
    if statement_view is not None and not statement_view.empty:
        render_customer_statement(daily_df, statement_view, year)


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
