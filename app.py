import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Advanced Sales Performance Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

C = {
    "navy": "#102D50", "navy2": "#173B63", "teal": "#0FA69E",
    "orange": "#E99A16", "blue": "#2873D8", "bg": "#F3F7FC",
    "white": "#FFFFFF", "text": "#142B46", "muted": "#4A5568",
    "border": "#DCE5EF", "red": "#DC3F43", "gray": "#E7EDF4",
}
PRODUCTS = ["Min", "Syn", "DEO", "Fluids"]
PCOLORS = {"Min": C["navy"], "Syn": C["orange"], "DEO": C["teal"], "Fluids": C["blue"]}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_AR = dict(zip(MONTHS, ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]))

TEXT = {
    "ar": {
        "title": "لوحة تحكم الأداء البيعي المتقدم", "subtitle": "تحليل شامل للمستهدف والمبيعات الفعلية",
        "data": "📂 مصدر البيانات", "upload": "ارفع ملف Excel", "filters": "🎛️ الفلاتر التفاعلية",
        "year": "السنة", "products": "المنتجات", "quarters": "الأرباع",
        "target": "المستهدف", "actual": "الفعلي", "achievement": "معدل الإنجاز",
        "remaining": "المتبقي", "best_month": "أفضل شهر", "best_product": "أفضل منتج",
        "monthly": "الأداء الشهري لعام", "half": "تحليل النصف السنوي",
        "quarter": "تحليل الربع السنوي", "month": "تحليل الشهر", "variance": "الفرق",
        "product_perf": "أداء المنتجات", "total_chart": "الإجمالي (فعلي مقابل مستهدف)",
        "daily": "تحليل المبيعات اليومية", "tables": "الجداول التحليلية", "export": "تصدير التقارير",
        "download": "تحميل التقرير الشامل (Excel)", "no_data": "لا توجد بيانات متاحة لهذه الفترة.",
        "select_half": "اختر النصف", "select_quarter": "اختر الربع", "select_month": "اختر الشهر",
        "daily_year": "السنة", "daily_month": "الشهر", "value_col": "عمود المبيعات",
        "all": "الكل", "na": "غير متاح",
    },
    "en": {
        "title": "Advanced Sales Performance Dashboard", "subtitle": "Comprehensive analysis of targets and actual sales",
        "data": "📂 Data Source", "upload": "Upload Excel file", "filters": "🎛️ Interactive Filters",
        "year": "Year", "products": "Products", "quarters": "Quarters",
        "target": "Target", "actual": "Actual", "achievement": "Achievement",
        "remaining": "Remaining", "best_month": "Best Month", "best_product": "Best Product",
        "monthly": "Monthly Performance for", "half": "Half-Year Analysis",
        "quarter": "Quarter Analysis", "month": "Month Analysis", "variance": "Variance",
        "product_perf": "Products Performance", "total_chart": "Total (Actual vs Target)",
        "daily": "Daily Sales Breakdown", "tables": "Detailed Analytical Tables", "export": "Export Reports",
        "download": "Download Comprehensive Report (Excel)", "no_data": "No data available for this period.",
        "select_half": "Select half-year", "select_quarter": "Select quarter", "select_month": "Select month",
        "daily_year": "Year", "daily_month": "Month", "value_col": "Sales column",
        "all": "All", "na": "N/A",
    },
}

st.markdown(f"""
<style>
.stApp {{background:{C['bg']}; color:{C['text']};}}
.block-container {{max-width:1600px; padding:1rem 1.25rem 2rem;}}
h1,h2,h3,h4 {{color:{C['text']};}}
div[data-testid="stMetric"] {{background:white;border:1px solid {C['border']};border-radius:12px;padding:10px 12px;box-shadow:0 2px 8px rgba(16,45,80,.05);min-height:84px;}}
div[data-testid="stMetricLabel"] {{color:{C['muted']};font-weight:650;font-size:.78rem;}}
div[data-testid="stMetricValue"] {{color:{C['navy']};font-weight:750;font-size:clamp(1.1rem,1.8vw,1.65rem);}}
.dashboard-header {{background:linear-gradient(112deg,#0C2747 0%,#173B63 68%,#0E8294 100%);border-radius:15px;padding:18px 24px;color:white;margin-bottom:15px;box-shadow:0 5px 16px rgba(16,45,80,.14);display:flex;justify-content:space-between;align-items:center;gap:12px;}}
.dashboard-header h1 {{color:white!important;margin:0;font-size:clamp(1.2rem,2.4vw,2rem);}}
.dashboard-header p {{color:#D6E4F1;margin:4px 0 0;font-size:.9rem;}}
.year-pill {{color:white;font-weight:750;white-space:nowrap;padding:8px 12px;border:1px solid #ffffff38;border-radius:10px;background:#ffffff12;}}
.section-heading {{background:linear-gradient(100deg,{C['navy']},{C['navy2']});color:white;padding:10px 14px;border-radius:11px;margin:4px 0 10px;font-size:1rem;font-weight:750;}}
.panel-heading {{background:linear-gradient(100deg,{C['navy']},{C['navy2']});color:white;padding:10px 12px;border-radius:10px;margin:3px 0 10px;font-weight:750;min-height:44px;}}
hr {{border:0;border-top:1px solid {C['border']};margin:0.85rem 0;}}
@media(max-width:700px) {{.block-container{{padding:.6rem .55rem 1.5rem;}} .dashboard-header{{padding:13px;}}}}
</style>
""", unsafe_allow_html=True)

lang_choice = st.sidebar.selectbox("🌍 Language / اللغة", ["العربية", "English"], index=0)
lang = "ar" if lang_choice == "العربية" else "en"
t = TEXT[lang]

@st.cache_data(show_spinner=False)
def load_sheets(file_bytes, filename):
    try:
        book = pd.ExcelFile(io.BytesIO(file_bytes), engine="pyxlsb" if filename.lower().endswith(".xlsb") else None)
        result = {}
        for name in book.sheet_names:
            df = pd.read_excel(book, sheet_name=name)
            result[name] = df.loc[:, ~df.columns.duplicated()]
        return result
    except Exception as exc:
        return {"__ERROR__": pd.DataFrame({"error": [str(exc)]})}

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
    mapping, current_year = {}, None
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
    records, current_month = [], None
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
                    "Year": year, "Month": current_month, "Month_Num": MONTHS.index(current_month) + 1,
                    "Quarter": qmap[current_month], "Half": hmap[current_month],
                    "Product": product, "Type": c1, "Value": pd.to_numeric(row.iloc[j], errors="coerce")
                })
    if not records:
        return None
    df = pd.DataFrame(records).pivot_table(
        index=["Year", "Month", "Month_Num", "Quarter", "Half", "Product"],
        columns="Type", values="Value", aggfunc="first"
    ).reset_index()
    df.columns.name = None
    for col in ["Target", "Actual"]:
        if col not in df:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values(["Year", "Month_Num", "Product"]).reset_index(drop=True)

def total(series):
    return series.sum(min_count=1) if series is not None else np.nan

def metrics(df):
    out = df.copy()
    out["Variance"] = out["Actual"] - out["Target"]
    out["Remaining"] = out["Target"] - out["Actual"]
    out["Achievement %"] = np.where(
        out["Target"].notna() & (out["Target"] > 0) & out["Actual"].notna(),
        out["Actual"] / out["Target"] * 100, np.nan
    )
    return out

def summary(df, groups):
    if df.empty:
        return pd.DataFrame(columns=groups + ["Target", "Actual", "Variance", "Remaining", "Achievement %"])
    return metrics(df.groupby(groups, as_index=False, sort=False).agg(
        Target=("Target", lambda s: s.sum(min_count=1)),
        Actual=("Actual", lambda s: s.sum(min_count=1))
    ))

def num(v):
    return "—" if pd.isna(v) else f"{v:,.2f}"

def pct(v):
    return "—" if pd.isna(v) else f"{v:.1f}%"

# دوائر متناسقة وكاملة (دائماً تظهر الدائرة كاملة بشكل احترافي بدون أي قص) مع خط وضح وأنيق بالأسفل للفعلي والمستهدف
def donut(actual, target, product):
    valid = pd.notna(actual) and pd.notna(target) and target > 0
    rate = actual / target * 100 if valid else 0
    # ضبط الحلقة لتكون متناسقة وكاملة دائماً
    ring = 100 if rate >= 100 else (rate if rate > 0 else 0.001)
    remainder = max(100 - ring, 0.001) if rate < 100 else 0.001
    
    label = f"{rate:.1f}%" if valid else "N/A"
    
    fig = go.Figure(go.Pie(
        values=[ring, remainder], hole=.72, sort=False,
        marker=dict(colors=[PCOLORS[product], C["gray"]], line=dict(color="white", width=1.5)),
        textinfo="none", hovertemplate=f"{product}<br>{label}<extra></extra>"
    ))
    fig.add_annotation(x=.5, y=.56, text=f"<b>{product}</b><br><b style='font-size:13.5px'>{label}</b>",
                       showarrow=False, font=dict(size=10.5, color=C["text"]))
    # تحسين الخط وتوضيحه تحت الدائرة للفعلي والمستهدف
    fig.add_annotation(x=.5, y=-0.12, text=f"<b>{num(actual)} / {num(target)}</b>",
                       showarrow=False, font=dict(size=9.5, color=C["navy"], weight="bold"), xref="paper", yref="paper")
    fig.update_layout(height=125, showlegend=False, margin=dict(l=2, r=2, t=2, b=16),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def total_bar_chart(period_label, actual, target, height=235):
    fig = go.Figure()
    fig.add_bar(
        x=[period_label], y=[target if pd.notna(target) else 0],
        name=t["target"], marker_color=C["navy"],
        text=[num(target)], textposition="auto", textfont=dict(size=11, color="white")
    )
    fig.add_bar(
        x=[period_label], y=[actual if pd.notna(actual) else 0],
        name=t["actual"], marker_color=C["teal"],
        text=[num(actual)], textposition="auto", textfont=dict(size=11, color="white")
    )
    fig.update_layout(
        barmode="group", height=height, margin=dict(l=6, r=6, t=22, b=6),
        plot_bgcolor="white", paper_bgcolor="white", font=dict(color=C["text"], size=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9.5)),
        xaxis=dict(showgrid=False), yaxis=dict(rangemode="tozero", gridcolor=C["gray"]),
        bargap=0.28, bargroupgap=0.10
    )
    return fig

def monthly_chart(month_df):
    base = pd.DataFrame({"Month": MONTHS}).merge(month_df[["Month","Target","Actual"]], on="Month", how="left")
    fig = go.Figure()
    fig.add_bar(x=base.Month, y=base.Target, name=t["target"], marker_color=C["navy"],
                text=base.Target.map(lambda v: "" if pd.isna(v) else f"{v:.2f}"), textposition="inside",
                textfont=dict(color="white", size=10))
    fig.add_bar(x=base.Month, y=base.Actual, name=t["actual"], marker_color=C["teal"],
                text=base.Actual.map(lambda v: "" if pd.isna(v) else f"{v:.2f}"), textposition="inside",
                textfont=dict(color="white", size=10))
    fig.update_layout(barmode="group", height=275, margin=dict(l=12,r=12,t=12,b=8),
        plot_bgcolor="white", paper_bgcolor="white", font=dict(color=C["text"],size=11),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        xaxis=dict(showgrid=False), yaxis=dict(rangemode="tozero",gridcolor=C["gray"]),
        bargap=.22, bargroupgap=.08)
    return fig

def render_panel(title, period, data, key, full_width=False):
    st.markdown(f'<div class="panel-heading">📊 {title} ({period})</div>', unsafe_allow_html=True)
    if data.empty:
        st.info(t["no_data"])
        return
    target, actual = total(data.Target), total(data.Actual)
    variance = actual - target if pd.notna(actual) and pd.notna(target) else np.nan
    rate = actual / target * 100 if pd.notna(actual) and pd.notna(target) and target > 0 else np.nan
    
    a, b, c, d = st.columns(4)
    a.metric(t["variance"], num(variance))
    b.metric(t["achievement"], pct(rate))
    c.metric(t["actual"], num(actual))
    d.metric(t["target"], num(target))
    
    if full_width:
        bar_col, donuts_col = st.columns([1, 2.2], gap="medium")
        with bar_col:
            st.caption(f"📊 {t['total_chart']}")
            st.plotly_chart(total_bar_chart(period, actual, target, height=175),
                            use_container_width=True, config={"displayModeBar": False, "staticPlot": True},
                            key=f"{key}_bar")
        with donuts_col:
            st.caption(f"🎯 {t['product_perf']} · {period}")
            cols = st.columns(4)
            for col, product in zip(cols, PRODUCTS):
                subset = data[data.Product == product]
                with col:
                    st.plotly_chart(donut(total(subset.Actual), total(subset.Target), product),
                        use_container_width=True, config={"displayModeBar": False, "staticPlot": True},
                        key=f"{key}_{product}")
    else:
        bar_col, donuts_col = st.columns([1, 1.35], gap="small")
        with bar_col:
            st.caption(f"📊 {t['total_chart']}")
            st.plotly_chart(total_bar_chart(period, actual, target, height=245),
                            use_container_width=True, config={"displayModeBar": False, "staticPlot": True},
                            key=f"{key}_bar")
        with donuts_col:
            st.caption(f"🎯 {t['product_perf']} · {period}")
            for products_row in (PRODUCTS[:2], PRODUCTS[2:]):
                cols = st.columns(2)
                for col, product in zip(cols, products_row):
                    subset = data[data.Product == product]
                    with col:
                        st.plotly_chart(donut(total(subset.Actual), total(subset.Target), product),
                            use_container_width=True, config={"displayModeBar": False, "staticPlot": True},
                            key=f"{key}_{product}")

def daily_data(sheets):
    name = next((n for n in sheets if n.strip().lower() == "sales report"), None)
    if not name:
        return None
    df = sheets[name].copy()
    for col in df.columns:
        if any(k in str(col).lower() for k in ["date", "تاريخ", "day", "يوم"]):
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().sum() == 0 and pd.api.types.is_numeric_dtype(df[col]):
                parsed = pd.to_datetime(df[col], unit="D", origin="1899-12-30", errors="coerce")
            if parsed.notna().sum():
                df["Parsed_Date"] = parsed
                return df.dropna(subset=["Parsed_Date"]).copy()
    return None

def excel_bytes(sheet_map):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, frame in sheet_map.items():
            frame.to_excel(writer, sheet_name=name[:31], index=False)
    return output.getvalue()

# File uploader
st.sidebar.header(t["data"])
uploaded = st.sidebar.file_uploader(t["upload"], type=["xlsx", "xls", "xlsb"])
if uploaded is None:
    st.markdown(f"""
    <div class="dashboard-header">
     <div><h1>📊 {t['title']}</h1><p>{t['subtitle']} · Advanced Sales Performance Dashboard</p></div>
     <div class="year-pill">📅 2026</div>
    </div>""", unsafe_allow_html=True)
    st.info("👈 ارفع ملف Excel للبدء / Upload your Excel workbook to begin.")
    st.stop()

sheets = load_sheets(uploaded.getvalue(), uploaded.name)
if "__ERROR__" in sheets:
    st.error(sheets["__ERROR__"].iloc[0,0])
    st.stop()
target_name = next((n for n in sheets if n.strip().lower() == "target"), None)
if target_name is None:
    st.error("لم يتم العثور على شيت Target في الملف.")
    st.stop()
data = parse_target(sheets[target_name])
if data is None or data.empty:
    st.error("تعذر قراءة شيت Target. تأكد من وجود أسماء المنتجات Min وSyn في صف العناوين.")
    st.stop()

# Sidebar filters
years = sorted(data.Year.dropna().unique().tolist())
st.sidebar.header(t["filters"])
year = st.sidebar.selectbox(t["year"], years, index=len(years)-1)
chosen_products = st.sidebar.multiselect(t["products"], PRODUCTS, default=PRODUCTS)
chosen_quarters = st.sidebar.multiselect(t["quarters"], ["Q1","Q2","Q3","Q4"], default=["Q1","Q2","Q3","Q4"])
if not chosen_products:
    st.warning("اختر منتجًا واحدًا على الأقل.")
    st.stop()

st.markdown(f"""
<div class="dashboard-header">
 <div><h1>📊 {t['title']}</h1><p>{t['subtitle']} · Advanced Sales Performance Dashboard</p></div>
 <div class="year-pill">📅 {year}</div>
</div>""", unsafe_allow_html=True)

year_data = data[(data.Year == year) & data.Product.isin(chosen_products)].copy()
filtered = year_data[year_data.Quarter.isin(chosen_quarters)].copy()

# Executive KPIs
target_total, actual_total = total(filtered.Target), total(filtered.Actual)
achievement = actual_total/target_total*100 if pd.notna(actual_total) and pd.notna(target_total) and target_total > 0 else np.nan
remaining = target_total-actual_total if pd.notna(actual_total) and pd.notna(target_total) else np.nan
month_summary = summary(filtered, ["Month_Num","Month"]).sort_values("Month_Num")
best_month_rows = month_summary.dropna(subset=["Actual"])
best_month = best_month_rows.loc[best_month_rows.Actual.idxmax(),"Month"] if not best_month_rows.empty else t["na"]
product_summary = summary(filtered, ["Product"])
best_prod_rows = product_summary.dropna(subset=["Actual"])
best_product = best_prod_rows.loc[best_prod_rows.Actual.idxmax(),"Product"] if not best_prod_rows.empty else t["na"]

k = st.columns(6)
k[0].metric(t["target"], num(target_total))
k[1].metric(t["actual"], num(actual_total))
k[2].metric(t["achievement"], pct(achievement))
k[3].metric(t["remaining"], num(remaining))
k[4].metric(t["best_month"], MONTH_AR.get(best_month,best_month) if lang=="ar" else best_month)
k[5].metric(t["best_product"], best_product)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f'<div class="section-heading">📈 {t["monthly"]} {year}</div>', unsafe_allow_html=True)
st.plotly_chart(monthly_chart(month_summary), use_container_width=True, config={"displayModeBar":False})
st.markdown("<hr>", unsafe_allow_html=True)

# الصف الأول: النصف السنوي والربع السنوي
half_col, quarter_col = st.columns(2, gap="medium")
with half_col:
    half = st.selectbox(t["select_half"], ["H1","H2"], index=1, key="half_choice")
    render_panel(t["half"], half, year_data[year_data.Half == half], "half", full_width=False)
with quarter_col:
    quarter = st.selectbox(t["select_quarter"], ["Q1","Q2","Q3","Q4"], index=2, key="quarter_choice") # Q3 افتراضياً تطابقاً مع الصورة
    render_panel(t["quarter"], quarter, year_data[year_data.Quarter == quarter], "quarter", full_width=False)

st.markdown("<hr>", unsafe_allow_html=True)

# الصف الثاني: تحليل الشهر في خانة مستقلة بعرض كامل
month = st.selectbox(t["select_month"], MONTHS, index=10, key="month_choice") # Nov افتراضياً
render_panel(t["month"], month, year_data[year_data.Month == month], "month", full_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Daily sales
st.markdown(f'<div class="section-heading">📅 {t["daily"]}</div>', unsafe_allow_html=True)
daily = daily_data(sheets)
if daily is not None and not daily.empty:
    daily_years = sorted(daily.Parsed_Date.dt.year.dropna().unique().tolist())
    d1,d2,d3 = st.columns(3)
    with d1:
        dy = st.selectbox(t["daily_year"], daily_years, index=len(daily_years)-1)
    dy_df = daily[daily.Parsed_Date.dt.year == dy].copy()
    dy_df["Month_Name"] = dy_df.Parsed_Date.dt.strftime("%b")
    with d2:
        available = [m for m in MONTHS if m in dy_df.Month_Name.unique()]
        dm = st.selectbox(t["daily_month"], [t["all"]] + available)
    numeric = [c for c in dy_df.select_dtypes(include=[np.number]).columns if c not in ["Year","Month","Month_Num"]]
    with d3:
        value_col = st.selectbox(t["value_col"], numeric) if numeric else None
    if dm != t["all"]:
        dy_df = dy_df[dy_df.Month_Name == dm]
    if value_col and not dy_df.empty:
        dy_df["Date_Only"] = dy_df.Parsed_Date.dt.date
        grouped = dy_df.groupby("Date_Only", as_index=False)[value_col].sum().sort_values("Date_Only")
        fig = go.Figure(go.Bar(x=grouped.Date_Only,y=grouped[value_col],marker_color=C["teal"]))
        fig.update_layout(height=260,margin=dict(l=10,r=10,t=10,b=10),plot_bgcolor="white",paper_bgcolor="white",
                          yaxis=dict(gridcolor=C["gray"]))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
else:
    st.caption("لم يتم العثور على بيانات يومية قابلة للقراءة في شيت Sales Report.")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f'<div class="section-heading">📋 {t["tables"]}</div>', unsafe_allow_html=True)
tab1,tab2,tab3 = st.tabs(["Monthly Summary","Products Breakdown","Yearly Comparison"])
with tab1:
    st.dataframe(month_summary.drop(columns=["Month_Num"],errors="ignore").style.format(
        {"Target":"{:,.2f}","Actual":"{:,.2f}","Variance":"{:,.2f}","Remaining":"{:,.2f}","Achievement %":"{:.1f}%"},
        na_rep="—"),use_container_width=True,hide_index=True)
with tab2:
    product_quarter = summary(filtered,["Product","Quarter"])
    st.dataframe(product_quarter.style.format(
        {"Target":"{:,.2f}","Actual":"{:,.2f}","Variance":"{:,.2f}","Remaining":"{:,.2f}","Achievement %":"{:.1f}%"},
        na_rep="—"),use_container_width=True,hide_index=True)
with tab3:
    yearly = summary(data[data.Product.isin(chosen_products)],["Year"])
    st.dataframe(yearly.style.format(
        {"Target":"{:,.2f}","Actual":"{:,.2f}","Variance":"{:,.2f}","Remaining":"{:,.2f}","Achievement %":"{:.1f}%"},
        na_rep="—"),use_container_width=True,hide_index=True)

st.markdown(f'<div class="section-heading">📥 {t["export"]}</div>', unsafe_allow_html=True)
exports = {
    "Monthly_Summary": month_summary.drop(columns=["Month_Num"],errors="ignore"),
    "Half_Year": summary(year_data,["Half"]),
    "Quarterly": summary(year_data,["Quarter"]),
    "Products": product_summary,
    "Product_Quarter": product_quarter,
    "Yearly": yearly,
}
st.download_button("📊 " + t["download"], data=excel_bytes(exports),
    file_name=f"Sales_Analysis_{year}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True)
