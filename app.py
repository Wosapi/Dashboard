import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Advanced Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

C = {
    "navy": "#102D50",
    "navy2": "#173B63",
    "teal": "#0FA69E",
    "orange": "#E99A16",
    "blue": "#2873D8",
    "bg": "#F3F7FC",
    "white": "#FFFFFF",
    "text": "#142B46",
    "muted": "#4A5568",
    "border": "#DCE5EF",
    "red": "#DC3F43",
    "gray": "#E7EDF4",
}

PRODUCTS = ["Min", "Syn", "DEO", "Fluids"]

PCOLORS = {
    "Min": C["navy"],
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
        "product_perf": "أداء المنتجات",
        "total_chart": "الإجمالي (فعلي مقابل مستهدف)",
        "daily": "جدول تحليل المبيعات اليومية (شيت Data)",
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
        "period_display": "📅 الفترة النشطة:",
        "all": "الكل",
        "na": "غير متاحة",
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
        "product_perf": "Products Performance",
        "total_chart": "Total (Actual vs Target)",
        "daily": "Daily Sales Table Breakdown (Data Sheet)",
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
        "period_display": "📅 Active Period:",
        "all": "All",
        "na": "N/A",
    },
}

# =========================================================
# 2. CSS DESIGN
# =========================================================

st.markdown(f"""
<style>
.stApp {{
    background:{C['bg']};
    color:{C['text']};
}}

.block-container {{
    max-width:1600px;
    padding:1rem 1.25rem 2rem;
}}

h1,h2,h3,h4 {{
    color:{C['text']};
}}

div[data-testid="stMetric"] {{
    background:white;
    border:1px solid {C['border']};
    border-radius:12px;
    padding:10px 12px;
    box-shadow:0 2px 8px rgba(16,45,80,.05);
    min-height:84px;
}}

div[data-testid="stMetricLabel"] {{
    color:{C['muted']};
    font-weight:700;
    font-size:.78rem;
}}

div[data-testid="stMetricValue"] {{
    color:{C['navy']};
    font-weight:800;
    font-size:clamp(1.05rem,1.7vw,1.55rem);
}}

.dashboard-header {{
    background:linear-gradient(
        112deg,#0C2747 0%,#173B63 68%,#0E8294 100%
    );
    border-radius:15px;
    padding:18px 24px;
    color:white;
    margin-bottom:15px;
    box-shadow:0 5px 16px rgba(16,45,80,.14);
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
    color:#D6E4F1;
    margin:4px 0 0;
    font-size:.9rem;
}}

.year-pill {{
    color:white;
    font-weight:750;
    white-space:nowrap;
    padding:8px 14px;
    border:1px solid #ffffff38;
    border-radius:10px;
    background:#ffffff14;
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
    padding:10px 12px;
    border-radius:10px;
    margin:3px 0 10px;
    font-weight:750;
    min-height:44px;
    display:flex;
    align-items:center;
    gap:6px;
}}

.period-badge {{
    background:#e6fffa;
    border:1px solid #319795;
    color:#234e52;
    padding:6px 12px;
    border-radius:8px;
    font-weight:700;
    font-size:0.85rem;
    margin-bottom:10px;
    display:inline-block;
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
        engine = (
            "pyxlsb"
            if filename.lower().endswith(".xlsb")
            else None
        )

        book = pd.ExcelFile(
            io.BytesIO(file_bytes),
            engine=engine
        )

        result = {}

        for name in book.sheet_names:

            df = pd.read_excel(
                book,
                sheet_name=name,
                header=0
            )

            df.columns = [
                str(c).strip()
                if not pd.isna(c)
                else f"Unnamed_{i}"
                for i, c in enumerate(df.columns)
            ]

            result[name] = df

        return result

    except Exception as exc:

        return {
            "__ERROR__": pd.DataFrame({
                "error": [str(exc)]
            })
        }


# =========================================================
# 5. TARGET SHEET PROCESSING
# =========================================================

def parse_target(raw):

    if raw is None or raw.empty:
        return None

    header_pos = None

    for pos, (_, row) in enumerate(raw.iterrows()):

        vals = [
            str(val).strip()
            for val in row.values
            if pd.notna(val)
        ]

        if "Min" in vals and "Syn" in vals:
            header_pos = pos
            break

    if header_pos is None:
        return None

    year_row = (
        raw.iloc[header_pos - 1]
        if header_pos > 0
        else pd.Series(raw.columns)
    )

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

            mapping[j] = (
                current_year,
                prod
            )

    qmap = {
        m: f"Q{(i // 3) + 1}"
        for i, m in enumerate(MONTHS)
    }

    hmap = {
        m: ("H1" if i < 6 else "H2")
        for i, m in enumerate(MONTHS)
    }

    records = []
    current_month = None

    for _, row in raw.iloc[header_pos + 1:].iterrows():

        c0 = (
            str(row.iloc[0]).strip()
            if pd.notna(row.iloc[0])
            else ""
        )

        c1 = (
            str(row.iloc[1]).strip()
            if pd.notna(row.iloc[1])
            else ""
        )

        if any(
            x in c0.lower()
            for x in ["total", "annual", "ytd"]
        ):
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
                    "Value": pd.to_numeric(
                        row.iloc[j],
                        errors="coerce"
                    )
                })

    if not records:
        return None

    df = pd.DataFrame(records)

    df = df.pivot_table(
        index=[
            "Year", "Month", "Month_Num",
            "Quarter", "Half", "Product"
        ],
        columns="Type",
        values="Value",
        aggfunc="first"
    ).reset_index()

    df.columns.name = None

    for col in ["Target", "Actual"]:

        if col not in df:
            df[col] = np.nan

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    return df.sort_values(
        ["Year", "Month_Num", "Product"]
    ).reset_index(drop=True)


# =========================================================
# 6. GENERAL CALCULATIONS
# =========================================================

def total(series):

    return (
        series.sum(min_count=1)
        if series is not None
        else np.nan
    )


def metrics(df):

    out = df.copy()

    out["Variance"] = (
        out["Actual"] - out["Target"]
    )

    out["Remaining"] = (
        out["Target"] - out["Actual"]
    )

    out["Achievement %"] = np.where(
        out["Target"].notna()
        & (out["Target"] > 0)
        & out["Actual"].notna(),

        out["Actual"] / out["Target"] * 100,

        np.nan
    )

    return out


def summary(df, groups):

    if df.empty:

        return pd.DataFrame(
            columns=groups + [
                "Target",
                "Actual",
                "Variance",
                "Remaining",
                "Achievement %"
            ]
        )

    grouped = df.groupby(
        groups,
        as_index=False,
        sort=False
    ).agg(
        Target=(
            "Target",
            lambda s: s.sum(min_count=1)
        ),
        Actual=(
            "Actual",
            lambda s: s.sum(min_count=1)
        )
    )

    return metrics(grouped)


def num(v):

    return "—" if pd.isna(v) else f"{v:,.2f}"


def pct(v):

    return "—" if pd.isna(v) else f"{v:.1f}%"


# =========================================================
# 7. CHARTS
# =========================================================

def donut(actual, target, product, compact=False):

    valid = (
        pd.notna(actual)
        and pd.notna(target)
        and target > 0
    )

    rate = actual / target * 100 if valid else 0

    ring = (
        100 if rate >= 100
        else rate if rate > 0
        else 0.001
    )

    remainder = (
        max(100 - ring, 0.001)
        if rate < 100
        else 0.001
    )

    label = f"{rate:.1f}%" if valid else "N/A"

    y_domain = [0.22, 0.98] if compact else [0.20, 0.98]
    chart_height = 112 if compact else 128
    center_y = 0.60 if compact else 0.59
    title_size = 9.5 if compact else 10.5
    pct_size = 11.5 if compact else 13.5
    sub_size = 8.5 if compact else 9.5

    fig = go.Figure(
        go.Pie(
            values=[ring, remainder],
            hole=0.73,
            sort=False,
            direction="clockwise",
            rotation=0,
            domain=dict(
                x=[0.05, 0.95],
                y=y_domain
            ),
            marker=dict(
                colors=[
                    PCOLORS[product],
                    C["gray"]
                ],
                line=dict(
                    color="white",
                    width=1.2
                )
            ),
            textinfo="none",
            hovertemplate=(
                f"{product}<br>{label}<extra></extra>"
            )
        )
    )

    fig.add_annotation(
        x=0.5,
        y=center_y,
        xref="paper",
        yref="paper",
        text=(
            f"<b>{product}</b><br>"
            f"<span style='font-size:{pct_size}px;"
            f"font-weight:800'>{label}</span>"
        ),
        showarrow=False,
        align="center",
        font=dict(
            size=title_size,
            color=C["text"]
        )
    )

    fig.add_annotation(
        x=0.5,
        y=0.02,
        xref="paper",
        yref="paper",
        text=f"<b>{num(actual)} / {num(target)}</b>",
        showarrow=False,
        align="center",
        font=dict(
            size=sub_size,
            color=C["navy"]
        )
    )

    fig.update_layout(
        height=chart_height,
        showlegend=False,
        margin=dict(l=2, r=2, t=2, b=2),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig


def total_bar_chart(
    period_label,
    actual,
    target,
    height=235
):

    fig = go.Figure()

    fig.add_bar(
        x=[period_label],
        y=[target if pd.notna(target) else 0],
        name=t["target"],
        marker_color=C["navy"],
        text=[num(target)],
        textposition="auto",
        textfont=dict(
            size=11,
            color="white"
        )
    )

    fig.add_bar(
        x=[period_label],
        y=[actual if pd.notna(actual) else 0],
        name=t["actual"],
        marker_color=C["teal"],
        text=[num(actual)],
        textposition="auto",
        textfont=dict(
            size=11,
            color="white"
        )
    )

    fig.update_layout(
        barmode="group",
        height=height,
        margin=dict(l=6, r=6, t=24, b=6),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            color=C["text"],
            size=10
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9.5)
        ),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            rangemode="tozero",
            gridcolor=C["gray"]
        ),
        bargap=0.28,
        bargroupgap=0.10
    )

    return fig


def monthly_chart(month_df):

    base = pd.DataFrame({
        "Month": MONTHS
    }).merge(
        month_df[
            ["Month", "Target", "Actual"]
        ],
        on="Month",
        how="left"
    )

    fig = go.Figure()

    fig.add_bar(
        x=base.Month,
        y=base.Target,
        name=t["target"],
        marker_color=C["navy"],
        text=base.Target.map(
            lambda v: (
                "" if pd.isna(v)
                else f"{v:.2f}"
            )
        ),
        textposition="inside",
        textfont=dict(
            color="white",
            size=10
        )
    )

    fig.add_bar(
        x=base.Month,
        y=base.Actual,
        name=t["actual"],
        marker_color=C["teal"],
        text=base.Actual.map(
            lambda v: (
                "" if pd.isna(v)
                else f"{v:.2f}"
            )
        ),
        textposition="inside",
        textfont=dict(
            color="white",
            size=10
        )
    )

    fig.update_layout(
        barmode="group",
        height=275,
        margin=dict(l=12, r=12, t=12, b=8),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            color=C["text"],
            size=11
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            rangemode="tozero",
            gridcolor=C["gray"]
        ),
        bargap=.22,
        bargroupgap=.08
    )

    return fig


# =========================================================
# 8. RENDER ANALYSIS PANEL
# =========================================================

def render_panel(
    title,
    period,
    data,
    key,
    icon="📊",
    full_width=False,
    selector_widget=None
):

    st.markdown(
        f'<div class="panel-heading">'
        f'{icon} {title} ({period})</div>',
        unsafe_allow_html=True
    )

    if selector_widget is not None:
        selector_widget()

    if data.empty:
        st.info(t["no_data"])
        return

    target = total(data.Target)
    actual = total(data.Actual)

    variance = (
        actual - target
        if pd.notna(actual) and pd.notna(target)
        else np.nan
    )

    rate = (
        actual / target * 100
        if pd.notna(actual)
        and pd.notna(target)
        and target > 0
        else np.nan
    )

    a, b, c, d = st.columns(4)

    a.metric(t["variance"], num(variance))
    b.metric(t["achievement"], pct(rate))
    c.metric(t["actual"], num(actual))
    d.metric(t["target"], num(target))

    if full_width:

        bar_col, donuts_col = st.columns(
            [1, 2.2],
            gap="medium"
        )

        with bar_col:

            st.caption(
                f"📊 {t['total_chart']}"
            )

            st.plotly_chart(
                total_bar_chart(
                    period,
                    actual,
                    target,
                    height=180
                ),
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "staticPlot": True
                },
                key=f"{key}_bar"
            )

        with donuts_col:

            st.caption(
                f"🎯 {t['product_perf']} · {period}"
            )

            cols = st.columns(4)

            for col, product in zip(cols, PRODUCTS):

                subset = data[
                    data.Product == product
                ]

                with col:

                    st.plotly_chart(
                        donut(
                            total(subset.Actual),
                            total(subset.Target),
                            product
                        ),
                        use_container_width=True,
                        config={
                            "displayModeBar": False,
                            "staticPlot": True
                        },
                        key=f"{key}_{product}"
                    )

    else:

        bar_col, donuts_col = st.columns(
            [1, 1.4],
            gap="small"
        )

        with bar_col:

            st.caption(
                f"📊 {t['total_chart']}"
            )

            st.plotly_chart(
                total_bar_chart(
                    period,
                    actual,
                    target,
                    height=238
                ),
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "staticPlot": True
                },
                key=f"{key}_bar"
            )

        with donuts_col:

            st.caption(
                f"🎯 {t['product_perf']} · {period}"
            )

            for products_row in (
                PRODUCTS[:2],
                PRODUCTS[2:]
            ):

                cols = st.columns(2, gap="small")

                for col, product in zip(cols, products_row):

                    subset = data[
                        data.Product == product
                    ]

                    with col:

                        st.plotly_chart(
                            donut(
                                total(subset.Actual),
                                total(subset.Target),
                                product,
                                compact=True
                            ),
                            use_container_width=True,
                            config={
                                "displayModeBar": False,
                                "staticPlot": True
                            },
                            key=f"{key}_{product}"
                        )


# =========================================================
# 9. DAILY DATA - CORRECTED VERSION
# =========================================================

def clean_column_name(value):

    return (
        str(value)
        .replace("\n", " ")
        .strip()
        .lower()
    )


def find_column(df, possible_names):

    normalized = {
        clean_column_name(col): col
        for col in df.columns
    }

    for name in possible_names:

        key = clean_column_name(name)

        if key in normalized:
            return normalized[key]

    return None


def parse_excel_date(series):

    """
    يدعم:
    1- تاريخ Excel الرقمي مثل 45434.
    2- التاريخ النصي مثل 22-May-24.
    3- التاريخ بصيغة يوم/شهر/سنة.

    لا يغير السنة الأصلية أبداً.
    """

    result = pd.Series(
        pd.NaT,
        index=series.index,
        dtype="datetime64[ns]"
    )

    numeric = pd.to_numeric(
        series,
        errors="coerce"
    )

    numeric_mask = (
        numeric.notna()
        & (numeric > 20000)
        & (numeric < 80000)
    )

    if numeric_mask.any():

        result.loc[numeric_mask] = pd.to_datetime(
            numeric.loc[numeric_mask],
            unit="D",
            origin="1899-12-30",
            errors="coerce"
        )

    text_mask = (
        series.notna()
        & ~numeric_mask
    )

    if text_mask.any():

        result.loc[text_mask] = pd.to_datetime(
            series.loc[text_mask].astype(str).str.strip(),
            errors="coerce",
            dayfirst=True
        )

    return result


def clean_numeric(series):

    """
    تحويل الأرقام إلى قيم رقمية.
    يدعم الفواصل والمسافات والقيم النصية.
    """

    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("SAR", "", regex=False)
        .str.replace("SR", "", regex=False)
        .str.strip()
        .replace({
            "": np.nan,
            "nan": np.nan,
            "None": np.nan
        }),
        errors="coerce"
    )


def daily_data_from_sheet(sheets):

    """
    قراءة شيت Data باستخدام أسماء الأعمدة الفعلية.
    لا يعتمد على ترتيب الأعمدة.
    """

    # العثور على شيت Data بالاسم
    sheet_name = next(
        (
            name
            for name in sheets
            if clean_column_name(name) in [
                "data",
                "بيانات"
            ]
        ),
        None
    )

    if sheet_name is None:

        return None, (
            "لم يتم العثور على شيت Data."
        )

    df = sheets[sheet_name].copy()

    if df.empty:

        return None, (
            "شيت Data فارغ."
        )

    # البحث عن الأعمدة بأسمائها
    date_col = find_column(
        df,
        ["Date", "التاريخ"]
    )

    amount_col = find_column(
        df,
        ["Amount", "المبلغ"]
    )

    quantity_col = find_column(
        df,
        [
            "Total Quantities",
            "Total Quantities ",
            "اجمالي الكميه",
            "إجمالي الكمية"
        ]
    )

    customer_no_col = find_column(
        df,
        [
            "Customer - No",
            "Customer-No",
            "رقم العميل"
        ]
    )

    customer_name_col = find_column(
        df,
        [
            "Customer - name",
            "Customer - Name",
            "اسم العميل"
        ]
    )

    invoice_col = find_column(
        df,
        [
            "Invoice No",
            "Invoice",
            "رقم الفاتورة"
        ]
    )

    missing = []

    if date_col is None:
        missing.append("Date")

    if amount_col is None:
        missing.append("Amount")

    if quantity_col is None:
        missing.append("Total Quantities")

    if customer_no_col is None:
        missing.append("Customer - No")

    if missing:

        return None, (
            "الأعمدة التالية غير موجودة في شيت Data: "
            + ", ".join(missing)
        )

    # بناء جدول موحد
    res = pd.DataFrame(index=df.index)

    # التاريخ الأصلي بدون تغيير السنة
    res["Parsed_Date"] = parse_excel_date(
        df[date_col]
    )

    # مبلغ المبيعات
    res["Amount"] = clean_numeric(
        df[amount_col]
    )

    # إجمالي الكميات
    res["Total_I"] = clean_numeric(
        df[quantity_col]
    )

    # رقم العميل
    res["Customer_No"] = (
        df[customer_no_col]
        .astype("string")
        .str.strip()
    )

    # اسم العميل
    if customer_name_col is not None:

        res["Customer_Name"] = (
            df[customer_name_col]
            .astype("string")
            .str.strip()
        )

    else:

        res["Customer_Name"] = pd.NA

    # رقم الفاتورة
    if invoice_col is not None:

        res["Invoice_No"] = (
            df[invoice_col]
            .astype("string")
            .str.strip()
        )

    else:

        res["Invoice_No"] = pd.NA

    # حذف السجلات التي لا تحتوي على تاريخ صحيح
    res = res.dropna(
        subset=["Parsed_Date"]
    ).copy()

    # الاحتفاظ بحركات المبيعات الفعلية
    has_amount = (
        res["Amount"].notna()
        & (res["Amount"] != 0)
    )

    has_quantity = (
        res["Total_I"].notna()
        & (res["Total_I"] != 0)
    )

    res = res[
        has_amount | has_quantity
    ].copy()

    # تنظيف رقم العميل
    res["Customer_No"] = (
        res["Customer_No"]
        .replace({
            "": pd.NA,
            "nan": pd.NA,
            "<NA>": pd.NA
        })
    )

    # إضافة التاريخ بدون الوقت
    res["Date_Only"] = (
        res["Parsed_Date"].dt.date
    )

    # إضافة السنة والشهر
    res["Year"] = (
        res["Parsed_Date"].dt.year
    )

    res["Month_Num"] = (
        res["Parsed_Date"].dt.month
    )

    res["Month"] = (
        res["Parsed_Date"].dt.strftime("%b")
    )

    return (
        res.reset_index(drop=True),
        None
    )


# =========================================================
# 10. EXPORT FUNCTION
# =========================================================

def excel_bytes(sheet_map):

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        for name, frame in sheet_map.items():

            frame.to_excel(
                writer,
                sheet_name=name[:31],
                index=False
            )

    return output.getvalue()


# =========================================================
# 11. FILE UPLOADER
# =========================================================

st.sidebar.header(t["data"])

uploaded = st.sidebar.file_uploader(
    t["upload"],
    type=["xlsx", "xls", "xlsb"]
)

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

    st.info(
        "👈 ارفع ملف Excel للبدء / Upload your Excel workbook to begin."
    )

    st.stop()


# =========================================================
# 12. LOAD WORKBOOK
# =========================================================

sheets = load_sheets(
    uploaded.getvalue(),
    uploaded.name
)

if "__ERROR__" in sheets:

    st.error(
        sheets["__ERROR__"].iloc[0, 0]
    )

    st.stop()


# =========================================================
# 13. FIND TARGET SHEET
# =========================================================

target_name = next(
    (
        name
        for name in sheets
        if clean_column_name(name) == "target"
    ),
    None
)

if target_name is None:

    st.error(
        "⚠️ لم يتم العثور على شيت Target في الملف."
    )

    st.stop()


data = parse_target(
    sheets[target_name]
)

if data is None or data.empty:

    st.error(
        "⚠️ تعذر قراءة شيت Target. "
        "تأكد من وجود أسماء المنتجات Min وSyn في صف العناوين."
    )

    st.stop()


# =========================================================
# 14. SIDEBAR FILTERS
# =========================================================

years = sorted(
    data.Year.dropna().unique().tolist()
)

st.sidebar.header(t["filters"])

year = st.sidebar.selectbox(
    t["year"],
    years,
    index=len(years) - 1
)

chosen_products = st.sidebar.multiselect(
    t["products"],
    PRODUCTS,
    default=PRODUCTS
)

chosen_quarters = st.sidebar.multiselect(
    t["quarters"],
    ["Q1", "Q2", "Q3", "Q4"],
    default=["Q1", "Q2", "Q3", "Q4"]
)

if not chosen_products:

    st.warning(
        "⚠️ اختر منتجًا واحدًا على الأقل."
    )

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
# 16. TARGET DATA FILTERING
# =========================================================

year_data = data[
    (data.Year == year)
    & data.Product.isin(chosen_products)
].copy()

filtered = year_data[
    year_data.Quarter.isin(chosen_quarters)
].copy()


# =========================================================
# 17. EXECUTIVE KPIs
# =========================================================

target_total = total(filtered.Target)
actual_total = total(filtered.Actual)

achievement = (
    actual_total / target_total * 100
    if pd.notna(actual_total)
    and pd.notna(target_total)
    and target_total > 0
    else np.nan
)

remaining = (
    target_total - actual_total
    if pd.notna(actual_total)
    and pd.notna(target_total)
    else np.nan
)

month_summary = summary(
    filtered,
    ["Month_Num", "Month"]
).sort_values("Month_Num")

best_month_rows = month_summary.dropna(
    subset=["Actual"]
)

best_month = (
    best_month_rows.loc[
        best_month_rows.Actual.idxmax(),
        "Month"
    ]
    if not best_month_rows.empty
    else t["na"]
)

product_summary = summary(
    filtered,
    ["Product"]
)

best_prod_rows = product_summary.dropna(
    subset=["Actual"]
)

best_product = (
    best_prod_rows.loc[
        best_prod_rows.Actual.idxmax(),
        "Product"
    ]
    if not best_prod_rows.empty
    else t["na"]
)

k = st.columns(6)

k[0].metric(
    t["target"],
    num(target_total)
)

k[1].metric(
    t["actual"],
    num(actual_total)
)

k[2].metric(
    t["achievement"],
    pct(achievement)
)

k[3].metric(
    t["remaining"],
    num(remaining)
)

k[4].metric(
    t["best_month"],
    MONTH_AR.get(best_month, best_month)
    if lang == "ar"
    else best_month
)

k[5].metric(
    t["best_product"],
    best_product
)


# =========================================================
# 18. MONTHLY PERFORMANCE
# =========================================================

st.markdown(
    "<hr>",
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="section-heading">'
    f'📈 {t["monthly"]} {year}</div>',
    unsafe_allow_html=True
)

st.plotly_chart(
    monthly_chart(month_summary),
    use_container_width=True,
    config={"displayModeBar": False}
)

st.markdown(
    "<hr>",
    unsafe_allow_html=True
)


# =========================================================
# 19. HALF-YEAR AND QUARTER ANALYSIS
# =========================================================

half_col, quarter_col = st.columns(
    2,
    gap="medium"
)

with half_col:

    half = st.selectbox(
        t["select_half"],
        ["H1", "H2"],
        index=1,
        key="half_choice"
    )

    render_panel(
        t["half"],
        half,
        year_data[
            year_data.Half == half
        ],
        "half",
        icon="📆"
    )


with quarter_col:

    quarter = st.selectbox(
        t["select_quarter"],
        ["Q1", "Q2", "Q3", "Q4"],
        index=2,
        key="quarter_choice"
    )

    render_panel(
        t["quarter"],
        quarter,
        year_data[
            year_data.Quarter == quarter
        ],
        "quarter",
        icon="🗓️"
    )


st.markdown(
    "<hr>",
    unsafe_allow_html=True
)


# =========================================================
# 20. MONTH ANALYSIS + DAILY SALES
# =========================================================

month_col, daily_col = st.columns(
    2,
    gap="medium"
)


# -------------------------
# MONTH ANALYSIS
# -------------------------

with month_col:

    current_month = st.session_state.get("month_choice", MONTHS[10])

    st.markdown(
        f'<div class="panel-heading">'
        f'📅 {t["month"]} ({current_month})</div>',
        unsafe_allow_html=True
    )

    month = st.selectbox(
        t["select_month"],
        MONTHS,
        index=10,
        key="month_choice"
    )

    month_filtered = year_data[year_data.Month == month]

    if month_filtered.empty:
        st.info(t["no_data"])
    else:
        m_target = total(month_filtered.Target)
        m_actual = total(month_filtered.Actual)
        m_variance = m_actual - m_target if pd.notna(m_actual) and pd.notna(m_target) else np.nan
        m_rate = m_actual / m_target * 100 if pd.notna(m_actual) and pd.notna(m_target) and m_target > 0 else np.nan

        ma, mb, mc, md = st.columns(4)
        ma.metric(t["variance"], num(m_variance))
        mb.metric(t["achievement"], pct(m_rate))
        mc.metric(t["actual"], num(m_actual))
        md.metric(t["target"], num(m_target))

        bar_col, donuts_col = st.columns([1, 1.4], gap="small")

        with bar_col:
            st.caption(f"📊 {t['total_chart']}")
            st.plotly_chart(
                total_bar_chart(month, m_actual, m_target, height=238),
                use_container_width=True,
                config={"displayModeBar": False, "staticPlot": True},
                key="month_bar"
            )

        with donuts_col:
            st.caption(f"🎯 {t['product_perf']} · {month}")
            for products_row in (PRODUCTS[:2], PRODUCTS[2:]):
                cols = st.columns(2, gap="small")
                for col, product in zip(cols, products_row):
                    subset = month_filtered[month_filtered.Product == product]
                    with col:
                        st.plotly_chart(
                            donut(total(subset.Actual), total(subset.Target), product, compact=True),
                            use_container_width=True,
                            config={"displayModeBar": False, "staticPlot": True},
                            key=f"month_{product}"
                        )


# -------------------------
# DAILY SALES ANALYSIS
# -------------------------

with daily_col:

    st.markdown(
        f'<div class="panel-heading">'
        f'📋 {t["daily"]}</div>',
        unsafe_allow_html=True
    )

    daily_df, daily_error = daily_data_from_sheet(
        sheets
    )

    if daily_error:

        st.error(daily_error)

    elif daily_df is None or daily_df.empty:

        st.warning(
            "لا توجد بيانات مبيعات يومية صالحة في شيت Data."
        )

    else:

        # السنة الأصلية من التاريخ
        dy_filtered = daily_df[
            daily_df["Year"] == int(year)
        ].copy()

        # ربط الجدول بالشهر المختار
        selected_month_number = (
            MONTHS.index(month) + 1
        )

        dy_filtered = dy_filtered[
            dy_filtered["Month_Num"]
            == selected_month_number
        ].copy()

        if dy_filtered.empty:

            st.info(
                f"لا توجد مبيعات مسجلة في "
                f"{MONTH_AR[month]} {year}."
            )

        else:

            min_d = dy_filtered[
                "Date_Only"
            ].min()

            max_d = dy_filtered[
                "Date_Only"
            ].max()

            st.markdown(
                f'<div class="period-badge">'
                f'{t["period_display"]} '
                f'{min_d} إلى {max_d}'
                f'</div>',
                unsafe_allow_html=True
            )

            filter_mode = st.radio(
                "طريقة العرض:",
                [
                    "جميع الأيام",
                    "تاريخ محدد",
                    "نطاق تاريخي"
                ],
                horizontal=True,
                key="daily_filter_mode"
            )

            # نسخة مستقلة للفلاتر
            daily_view = dy_filtered.copy()

            # اختيار تاريخ محدد
            if filter_mode == "تاريخ محدد":

                selected_date = st.date_input(
                    "اختر اليوم المطلوب:",
                    value=max_d,
                    min_value=min_d,
                    max_value=max_d,
                    key="daily_single_date"
                )

                if selected_date:

                    daily_view = daily_view[
                        daily_view["Date_Only"]
                        == selected_date
                    ]

            # اختيار نطاق زمني
            elif filter_mode == "نطاق تاريخي":

                date_range = st.date_input(
                    "اختر نطاق التواريخ:",
                    value=(min_d, max_d),
                    min_value=min_d,
                    max_value=max_d,
                    key="daily_date_range"
                )

                if (
                    isinstance(date_range, tuple)
                    and len(date_range) == 2
                ):

                    start_d, end_d = date_range

                    if start_d and end_d:

                        daily_view = daily_view[
                            (
                                daily_view["Date_Only"]
                                >= start_d
                            )
                            &
                            (
                                daily_view["Date_Only"]
                                <= end_d
                            )
                        ]

            if not daily_view.empty:

                # حساب عدد الفواتير أو العمليات
                grouped_daily = (
                    daily_view
                    .groupby(
                        "Date_Only",
                        as_index=False
                    )
                    .agg(
                        Sales_Count=(
                            "Amount",
                            lambda s: s.notna().sum()
                        ),

                        Total_I_Sum=(
                            "Total_I",
                            lambda s: s.sum(
                                min_count=1
                            )
                        ),

                        Customer_Count=(
                            "Customer_No",
                            "nunique"
                        ),

                        Total_Amount=(
                            "Amount",
                            lambda s: s.sum(
                                min_count=1
                            )
                        )
                    )
                    .sort_values(
                        "Date_Only",
                        ascending=False
                    )
                )

                # عرض الأسماء بالعربية
                display_daily = grouped_daily.rename(
                    columns={
                        "Date_Only": "التاريخ",
                        "Sales_Count": t["sales_count"],
                        "Total_I_Sum": t["total_i"],
                        "Customer_Count": t["customer_count"],
                        "Total_Amount": t["total_amount"]
                    }
                )

                # تنسيق الأرقام بعد تغيير أسماء الأعمدة
                format_dict = {
                    t["total_i"]: "{:,.2f}",
                    t["total_amount"]: "{:,.2f}"
                }

                st.dataframe(
                    display_daily.style.format(
                        format_dict,
                        na_rep="—"
                    ),
                    use_container_width=True,
                    hide_index=True,
                    height=260
                )

                # إجماليات الفترة المعروضة
                st.markdown("#### 📊 إجمالي الفترة المعروضة")

                m1, m2, m3 = st.columns(3)

                m1.metric(
                    t["sales_count"],
                    f"{len(daily_view):,}"
                )

                m2.metric(
                    t["total_i"],
                    num(
                        daily_view["Total_I"].sum(
                            min_count=1
                        )
                    )
                )

                m3.metric(
                    t["total_amount"],
                    num(
                        daily_view["Amount"].sum(
                            min_count=1
                        )
                    )
                )

            else:

                st.warning(
                    "لا توجد مبيعات في التاريخ المحدد."
                )


# =========================================================
# 21. ANALYTICAL TABLES
# =========================================================

st.markdown(
    "<hr>",
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="section-heading">'
    f'📋 {t["tables"]}</div>',
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "📅 Monthly Summary",
    "🛢️ Products Breakdown",
    "📆 Yearly Comparison"
])


with tab1:

    st.dataframe(
        month_summary.drop(
            columns=["Month_Num"],
            errors="ignore"
        ).style.format(
            {
                "Target": "{:,.2f}",
                "Actual": "{:,.2f}",
                "Variance": "{:,.2f}",
                "Remaining": "{:,.2f}",
                "Achievement %": "{:.1f}%"
            },
            na_rep="—"
        ),
        use_container_width=True,
        hide_index=True
    )


with tab2:

    product_quarter = summary(
        filtered,
        ["Product", "Quarter"]
    )

    st.dataframe(
        product_quarter.style.format(
            {
                "Target": "{:,.2f}",
                "Actual": "{:,.2f}",
                "Variance": "{:,.2f}",
                "Remaining": "{:,.2f}",
                "Achievement %": "{:.1f}%"
            },
            na_rep="—"
        ),
        use_container_width=True,
        hide_index=True
    )


with tab3:

    yearly = summary(
        data[
            data.Product.isin(chosen_products)
        ],
        ["Year"]
    )

    st.dataframe(
        yearly.style.format(
            {
                "Target": "{:,.2f}",
                "Actual": "{:,.2f}",
                "Variance": "{:,.2f}",
                "Remaining": "{:,.2f}",
                "Achievement %": "{:.1f}%"
            },
            na_rep="—"
        ),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 22. EXPORT REPORTS
# =========================================================

st.markdown(
    f'<div class="section-heading">'
    f'📥 {t["export"]}</div>',
    unsafe_allow_html=True
)

exports = {
    "Monthly_Summary": month_summary.drop(
        columns=["Month_Num"],
        errors="ignore"
    ),

    "Half_Year": summary(
        year_data,
        ["Half"]
    ),

    "Quarterly": summary(
        year_data,
        ["Quarter"]
    ),

    "Products": product_summary,

    "Product_Quarter": product_quarter,

    "Yearly": yearly,
}

# إضافة تقرير المبيعات اليومية إلى ملف التصدير
if daily_df is not None and not daily_df.empty:

    daily_export = daily_df.copy()

    daily_export["Parsed_Date"] = (
        daily_export["Parsed_Date"].dt.strftime(
            "%Y-%m-%d"
        )
    )

    exports["Daily_Sales"] = daily_export


st.download_button(
    "📥 " + t["download"],

    data=excel_bytes(exports),

    file_name=f"Sales_Analysis_{year}.xlsx",

    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),

    use_container_width=True
)
