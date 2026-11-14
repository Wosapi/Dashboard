import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(
    page_title="لوحة تحكم أداء المبيعات المتقدمة",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# الثوابت والألوان
COLORS = {
    "navy_blue": "#142B4A",
    "dark_blue": "#1E3A5F",
    "teal": "#00A6A6",
    "green": "#16A36A",
    "orange": "#F59E0B",
    "red": "#DC3545",
    "background": "#F4F7FB",
    "white": "#FFFFFF",
    "text": "#263445"
}
PRODUCTS = ["Min", "Syn", "DEO", "Fluids"]

# تنسيق CSS
st.markdown("""
<style>
body { background-color: #F4F7FB; color: #263445; direction: rtl; text-align: right; }
.stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
h1, h2, h3 { color: #142B4A; }
</style>
""", unsafe_allow_html=True)

st.title("📊 لوحة تحكم أداء المبيعات والتحليل المتقدم")
st.markdown("تحليل شامل للمستهدف والمبيعات الفعلية (شهري، ربعي، نصف سنوي، وحسب فئات المنتجات).")

# --- محرك تحميل البيانات ---
@st.cache_data
def load_excel_data(uploaded_file):
    try:
        if uploaded_file is not None:
            file_name = uploaded_file.name.lower()
            if file_name.endswith('.xlsb'):
                xls = pd.ExcelFile(uploaded_file, engine='pyxlsb')
            else:
                xls = pd.ExcelFile(uploaded_file)
        else:
            return None
            
        if "Target" not in xls.sheet_names:
            st.error("شيت 'Target' غير موجود في الملف.")
            return None
        return pd.read_excel(xls, sheet_name="Target")
    except Exception as e:
        st.error(f"خطأ في قراءة ملف Excel: {e}")
        return None

# --- معالجة هيكل شيت Target ---
def parse_target_sheet(raw_df):
    if raw_df is None or raw_df.empty:
        return None
    header_row_idx = None
    for idx, row in raw_df.iterrows():
        row_values = [str(val).strip() for val in row.values if pd.notna(val)]
        if "Min" in row_values and "Syn" in row_values:
            header_row_idx = idx
            break
    if header_row_idx is None:
        return None

    year_row = raw_df.iloc[header_row_idx - 1] if header_row_idx > 0 else raw_df.columns
    prod_row = raw_df.iloc[header_row_idx]

    col_mapping = {}
    current_year = None
    for col_idx in range(2, len(raw_df.columns)):
        yr_val = str(year_row.iloc[col_idx]) if header_row_idx > 0 else str(raw_df.columns[col_idx])
        for y in ["2024", "2025", "2026", "2027"]:
            if y in yr_val:
                current_year = int(y)
                break
        prod_val = str(prod_row.iloc[col_idx]).strip()
        if prod_val in ["Min", "Syn", "DEO", "Fluids"] and current_year is not None:
            col_mapping[col_idx] = (current_year, prod_val)

    data_rows = raw_df.iloc[header_row_idx + 1:].copy()
    records = []
    current_month = None
    valid_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    quarter_map = {"Jan": "Q1", "Feb": "Q1", "Mar": "Q1", "Apr": "Q2", "May": "Q2", "Jun": "Q2", "Jul": "Q3", "Aug": "Q3", "Sep": "Q3", "Oct": "Q4", "Nov": "Q4", "Dec": "Q4"}
    half_map = {"Jan": "H1", "Feb": "H1", "Mar": "H1", "Apr": "H1", "May": "H1", "Jun": "H1", "Jul": "H2", "Aug": "H2", "Sep": "H2", "Oct": "H2", "Nov": "H2", "Dec": "H2"}

    for _, row in data_rows.iterrows():
        col0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        col1 = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        if any(w in col0.lower() for w in ["total", "q1", "quarter", "annual", "ytd"]):
            break
        if col0 in valid_months:
            current_month = col0
        if current_month and col1 in ["Target", "Actual"]:
            for col_idx, (year, product) in col_mapping.items():
                num_val = pd.to_numeric(row.iloc[col_idx], errors='coerce')
                records.append({
                    "Year": year, "Month": current_month, "Month_Num": valid_months.index(current_month) + 1,
                    "Quarter": quarter_map[current_month], "Half": half_map[current_month],
                    "Product": product, "Type": col1, "Value": num_val
                })
    if not records:
        return None
    long_df = pd.DataFrame(records)
    pivoted = long_df.pivot_table(
        index=["Year", "Month", "Month_Num", "Quarter", "Half", "Product"],
        columns="Type", values="Value", aggfunc="first"
    ).reset_index()
    pivoted.columns.name = None
    if "Target" not in pivoted.columns: pivoted["Target"] = np.nan
    if "Actual" not in pivoted.columns: pivoted["Actual"] = np.nan
    return pivoted.sort_values(["Year", "Month_Num", "Product"])

# --- المعادلات والتحليلات ---
def enrich_metrics(df):
    if df is None or df.empty: return df
    res = df.copy()
    res["Variance"] = res["Actual"] - res["Target"]
    res["Remaining"] = res["Target"] - res["Actual"]
    res["Achievement %"] = np.where((res["Target"].notna()) & (res["Target"] > 0) & (res["Actual"].notna()), (res["Actual"] / res["Target"]) * 100, np.nan)
    return res

def summarize_by_period(df, group_cols):
    summary = df.groupby(group_cols, as_index=False, sort=False).agg(
        Target=("Target", "sum"), Actual=("Actual", lambda x: x.sum(min_count=1))
    )
    return enrich_metrics(summary)

# --- دوائر ورسوم بيانية ---
def plot_monthly_target_vs_actual(monthly_df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_df["Month"], y=monthly_df["Target"], name="المستهدف (Target)", marker_color=COLORS["navy_blue"]))
    fig.add_trace(go.Bar(x=monthly_df["Month"], y=monthly_df["Actual"], name="الفعلي (Actual)", marker_color=COLORS["teal"]))
    fig.update_layout(barmode="group", plot_bgcolor=COLORS["white"], paper_bgcolor=COLORS["white"], font_color=COLORS["text"], margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

def plot_monthly_growth_line(monthly_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly_df["Month"], y=monthly_df["Target"], mode="lines+markers", name="مسار المستهدف", line=dict(color=COLORS["orange"], width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=monthly_df["Month"], y=monthly_df["Actual"], mode="lines+markers", name="المبيعات الفعلية", line=dict(color=COLORS["dark_blue"], width=3), marker=dict(size=8)))
    fig.update_layout(plot_bgcolor=COLORS["white"], paper_bgcolor=COLORS["white"], font_color=COLORS["text"], margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

def plot_quarterly_comparison(quarterly_df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=quarterly_df["Quarter"], y=quarterly_df["Target"], name="مستهدف الربع", marker_color="#1E3A5F"))
    fig.add_trace(go.Bar(x=quarterly_df["Quarter"], y=quarterly_df["Actual"], name="فعلي الربع", marker_color="#16A36A"))
    fig.update_layout(barmode="group", plot_bgcolor=COLORS["white"], paper_bgcolor=COLORS["white"], font_color=COLORS["text"], margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

def create_donut_chart(percentage, color):
    display_val = min(max(percentage, 0), 100) if (percentage is not None and not pd.isna(percentage)) else 0
    label_text = f"{percentage:.1f}%" if (percentage is not None and not pd.isna(percentage)) else "N/A"
    fig = go.Figure(data=[go.Pie(values=[display_val, 100 - display_val], hole=0.75, marker_colors=[color, "#E2E8F0"], textinfo="none", hoverinfo="none", sort=False)])
    fig.update_layout(showlegend=False, annotations=[dict(text=label_text, x=0.5, y=0.5, font_size=20, font_weight="bold", font_color=COLORS["text"], showarrow=False)], plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=5, r=5, t=5, b=5), height=160)
    return fig

def convert_dfs_to_excel(sheets_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for s_name, df in sheets_dict.items():
            df.to_excel(writer, sheet_name=s_name, index=False)
    return output.getvalue()

# --- القائمة الجانبية وتطبيق الواجهة ---
st.sidebar.header("📂 مصدر البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف Excel (.xlsx أو .xlsb)", type=["xlsx", "xls", "xlsb"])

raw_df = load_excel_data(uploaded_file)

if raw_df is not None:
    clean_df = parse_target_sheet(raw_df)
    if clean_df is None or clean_df.empty:
        st.error("تعذر التعرف على هيكل شيت Target.")
    else:
        available_years = sorted(clean_df["Year"].unique().tolist())
        st.sidebar.header("🎛️ الفلاتر التفاعلية")
        selected_year = st.sidebar.selectbox("اختر السنة", available_years, index=len(available_years)-1)
        selected_products = st.sidebar.multiselect("فئات المنتجات", PRODUCTS, default=PRODUCTS)
        selected_quarters = st.sidebar.multiselect("الأرباع السنوية", ["Q1", "Q2", "Q3", "Q4"], default=["Q1", "Q2", "Q3", "Q4"])

        filtered_df = clean_df[(clean_df["Year"] == selected_year) & (clean_df["Product"].isin(selected_products)) & (clean_df["Quarter"].isin(selected_quarters))].copy()

        # KPIs
        total_target = filtered_df["Target"].sum()
        total_actual = filtered_df["Actual"].sum(min_count=1)
        ach_pct = (total_actual / total_target * 100) if (pd.notna(total_actual) and total_target > 0) else np.nan
        remaining = (total_target - total_actual) if pd.notna(total_actual) else total_target

        m_summary = summarize_by_period(filtered_df, ["Month_Num", "Month"]).sort_values("Month_Num")
        valid_m = m_summary.dropna(subset=["Actual"])
        best_month = valid_m.loc[valid_m["Actual"].idxmax(), "Month"] if not valid_m.empty else "لا يوجد"

        p_summary = summarize_by_period(filtered_df, ["Product"])
        valid_p = p_summary.dropna(subset=["Actual"])
        best_prod = valid_p.loc[valid_p["Actual"].idxmax(), "Product"] if not valid_p.empty else "لا يوجد"

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("إجمالي المستهدف", f"{total_target:,.2f}")
        k2.metric("إجمالي الفعلي", f"{total_actual:,.2f}" if pd.notna(total_actual) else "غير مسجل")
        k3.metric("نسبة التحقيق", f"{ach_pct:.1f}%" if pd.notna(ach_pct) else "—")
        k4.metric("المتبقي", f"{remaining:,.2f}")
        k5.metric("أفضل شهر", best_month)
        k6.metric("أفضل منتج", best_prod)

        st.markdown("---")
        st.subheader(f"📈 الأداء الشهري المفصل لعام {selected_year}")
        c1, c2 = st.columns([3, 2])
        with c1: st.plotly_chart(plot_monthly_target_vs_actual(m_summary), use_container_width=True)
        with c2: st.plotly_chart(plot_monthly_growth_line(m_summary), use_container_width=True)

        st.subheader("🎯 نسب تحقيق المستهدف حسب فئة المنتج")
        year_prod_df = summarize_by_period(clean_df[(clean_df["Year"] == selected_year) & (clean_df["Quarter"].isin(selected_quarters))], ["Product"])
        prod_colors = {"Min": COLORS["dark_blue"], "Syn": COLORS["orange"], "DEO": COLORS["teal"], "Fluids": COLORS["navy_blue"]}
        d_cols = st.columns(4)
        for idx, prod in enumerate(PRODUCTS):
            row = year_prod_df[year_prod_df["Product"] == prod]
            pct = row["Achievement %"].values[0] if not row.empty else np.nan
            t_val = row["Target"].values[0] if not row.empty else 0
            a_val = row["Actual"].values[0] if not row.empty else np.nan
            with d_cols[idx]:
                st.markdown(f"<div style='background-color: white; padding: 12px; border-radius: 12px; text-align: center;'>", unsafe_allow_html=True)
                st.plotly_chart(create_donut_chart(pct, prod_colors[prod]), use_container_width=True)
                a_str = f"{a_val:,.2f}" if pd.notna(a_val) else "0.00"
                st.markdown(f"**فئة {prod}**<br><span style='font-size:12px; color:#555;'>الفعلي: {a_str} / المستهدف: {t_val:,.2f}</span></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🗓️ التحليل الربعي ونصف السنوي")
        q_summary = summarize_by_period(filtered_df, ["Quarter"])
        h_summary = summarize_by_period(filtered_df, ["Half"])
        qc1, qc2 = st.columns([3, 2])
        with qc1: st.plotly_chart(plot_quarterly_comparison(q_summary), use_container_width=True)
        with qc2:
            st.dataframe(q_summary.style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)
            st.dataframe(h_summary.style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)

        st.markdown("---")
        st.subheader("📋 الجداول التحليلية المفصلة")
        tab1, tab2, tab3 = st.tabs(["التفصيل الشهري", "تفصيل المنتجات", "مقارنة السنوات"])
        with tab1: st.dataframe(m_summary.drop(columns=["Month_Num"]).style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)
        with tab2: st.dataframe(summarize_by_period(filtered_df, ["Product", "Quarter"]).style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)
        with tab3: st.dataframe(summarize_by_period(clean_df[clean_df["Product"].isin(selected_products)], ["Year"]).style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)

        st.markdown("### 📥 تصدير التقارير")
        excel_bytes = convert_dfs_to_excel({
            "Monthly": m_summary.drop(columns=["Month_Num"]),
            "Quarterly": q_summary,
            "Half_Yearly": h_summary,
            "Products": p_summary
        })
        st.download_button("📊 تحميل التقرير الشامل (Excel)", data=excel_bytes, file_name=f"Sales_Analysis_{selected_year}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("👈 ارفع ملف Excel الخاص بالمبيعات من القائمة الجانبية لعرض لوحة التحكم بالرسوم البيانية الكاملة.")
