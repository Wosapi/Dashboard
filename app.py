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
VALID_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# تنسيق CSS
st.markdown("""
<style>
body { background-color: #F4F7FB; color: #263445; direction: rtl; text-align: right; }
.stMetric { background-color: #FFFFFF; padding: 14px; border-radius: 10px; box-shadow: 0 3px 6px rgba(0,0,0,0.05); }
h1, h2, h3 { color: #142B4A; }
</style>
""", unsafe_allow_html=True)

st.title("📊 لوحة تحكم أداء المبيعات والتحليل المتقدم")
st.markdown("تحليل شامل للمستهدف والمبيعات الفعلية (سنوي، ربعي، شهري مفصل لكل شهر، والمبيعات اليومية).")

# --- 1. محرك تحميل جميع الشيتات ---
@st.cache_data
def load_all_sheets(uploaded_file):
    try:
        if uploaded_file is None:
            return None
        file_name = uploaded_file.name.lower()
        if file_name.endswith('.xlsb'):
            xls = pd.ExcelFile(uploaded_file, engine='pyxlsb')
        else:
            xls = pd.ExcelFile(uploaded_file)
        
        sheets_dict = {}
        for name in xls.sheet_names:
            sheets_dict[name] = pd.read_excel(xls, sheet_name=name)
        return sheets_dict
    except Exception as e:
        st.error(f"خطأ في قراءة ملف Excel: {e}")
        return None

# --- 2. معالجة هيكل شيت Target ---
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
        if prod_val in PRODUCTS and current_year is not None:
            col_mapping[col_idx] = (current_year, prod_val)

    data_rows = raw_df.iloc[header_row_idx + 1:].copy()
    records = []
    current_month = None
    quarter_map = {"Jan": "Q1", "Feb": "Q1", "Mar": "Q1", "Apr": "Q2", "May": "Q2", "Jun": "Q2", "Jul": "Q3", "Aug": "Q3", "Sep": "Q3", "Oct": "Q4", "Nov": "Q4", "Dec": "Q4"}
    half_map = {"Jan": "H1", "Feb": "H1", "Mar": "H1", "Apr": "H1", "May": "H1", "Jun": "H1", "Jul": "H2", "Aug": "H2", "Sep": "H2", "Oct": "H2", "Nov": "H2", "Dec": "H2"}

    for _, row in data_rows.iterrows():
        col0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        col1 = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        if any(w in col0.lower() for w in ["total", "q1", "quarter", "annual", "ytd"]):
            break
        if col0 in VALID_MONTHS:
            current_month = col0
        if current_month and col1 in ["Target", "Actual"]:
            for col_idx, (year, product) in col_mapping.items():
                num_val = pd.to_numeric(row.iloc[col_idx], errors='coerce')
                records.append({
                    "Year": year, "Month": current_month, "Month_Num": VALID_MONTHS.index(current_month) + 1,
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

# --- 3. محرك استخراج وتحليل المبيعات اليومية ---
def detect_daily_sales_data(sheets_dict):
    candidate_sheets = {}
    for sheet_name, df in sheets_dict.items():
        if sheet_name == "Target" or df is None or df.empty:
            continue
        
        clean_sheet = df.copy()
        for idx in range(min(10, len(clean_sheet))):
            row_vals = [str(v).lower() for v in clean_sheet.iloc[idx].values if pd.notna(v)]
            if any(k in " ".join(row_vals) for k in ["date", "تاريخ", "day", "يوم", "qty", "quantity", "sales", "amount", "ton", "volume", "مبيعات", "كمية"]):
                clean_sheet.columns = clean_sheet.iloc[idx]
                clean_sheet = clean_sheet.iloc[idx + 1:].reset_index(drop=True)
                break

        clean_sheet = clean_sheet.loc[:, clean_sheet.columns.notna()]
        clean_sheet.columns = [str(c).strip() for c in clean_sheet.columns]
        
        date_col = None
        for col in clean_sheet.columns:
            col_l = col.lower()
            if any(k in col_l for k in ["date", "تاريخ", "day", "يوم"]):
                s = clean_sheet[col]
                if pd.api.types.is_numeric_dtype(s):
                    parsed = pd.to_datetime(s, unit='D', origin='1899-12-30', errors='coerce')
                else:
                    parsed = pd.to_datetime(s, errors='coerce')
                
                if parsed.notna().sum() >= 3:
                    clean_sheet["Parsed_Date"] = parsed
                    date_col = col
                    break
        
        if date_col is not None:
            valid_daily = clean_sheet.dropna(subset=["Parsed_Date"]).copy()
            valid_daily = valid_daily[(valid_daily["Parsed_Date"].dt.year >= 2020) & (valid_daily["Parsed_Date"].dt.year <= 2030)]
            if not valid_daily.empty:
                candidate_sheets[sheet_name] = (valid_daily, date_col)
                
    return candidate_sheets

# --- 4. المعادلات ---
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

# --- 5. الرسوم البيانية ---
def plot_monthly_target_vs_actual(monthly_df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_df["Month"], y=monthly_df["Target"], name="المستهدف (Target)", marker_color=COLORS["navy_blue"], text=monthly_df["Target"].round(2), textposition="auto"))
    fig.add_trace(go.Bar(x=monthly_df["Month"], y=monthly_df["Actual"], name="الفعلي (Actual)", marker_color=COLORS["teal"], text=monthly_df["Actual"].round(2), textposition="auto"))
    fig.update_layout(barmode="group", plot_bgcolor=COLORS["white"], paper_bgcolor=COLORS["white"], font_color=COLORS["text"], margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

def create_donut_chart(percentage, color):
    display_val = min(max(percentage, 0), 100) if (percentage is not None and not pd.isna(percentage)) else 0
    label_text = f"{percentage:.1f}%" if (percentage is not None and not pd.isna(percentage)) else "N/A"
    fig = go.Figure(data=[go.Pie(values=[display_val, 100 - display_val], hole=0.75, marker_colors=[color, "#E2E8F0"], textinfo="none", hoverinfo="none", sort=False)])
    fig.update_layout(showlegend=False, annotations=[dict(text=label_text, x=0.5, y=0.5, font_size=19, font_weight="bold", font_color=COLORS["text"], showarrow=False)], plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=5, r=5, t=5, b=5), height=150)
    return fig

def convert_dfs_to_excel(sheets_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for s_name, df in sheets_dict.items():
            df.to_excel(writer, sheet_name=s_name[:31], index=False)
    return output.getvalue()

# --- خانة رفع الملف ---
st.sidebar.header("📂 مصدر البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف Excel (.xlsx أو .xlsb)", type=["xlsx", "xls", "xlsb"])

sheets_dict = load_all_sheets(uploaded_file)

if sheets_dict is None:
    st.markdown("### 📤 يرجى رفع ملف الإكسل (Total_Sales.xlsb أو .xlsx) للبدء:")
    uploaded_file_main = st.file_uploader("اختر ملف الإكسل من هنا:", type=["xlsx", "xls", "xlsb"], key="main_uploader")
    if uploaded_file_main is not None:
        sheets_dict = load_all_sheets(uploaded_file_main)
        st.rerun()
    else:
        st.info("👈 ارفع الملف أعلاه أو من القائمة الجانبية لتظهر لك لوحة التحكم بكامل ميزاتها.")

if sheets_dict is not None:
    if "Target" not in sheets_dict:
        st.error("شيت 'Target' غير موجود في الملف المرفق.")
    else:
        clean_df = parse_target_sheet(sheets_dict["Target"])
        if clean_df is None or clean_df.empty:
            st.error("تعذر التعرف على هيكل شيت Target.")
        else:
            available_years = sorted(clean_df["Year"].unique().tolist())
            st.sidebar.header("🎛️ الفلاتر التفاعلية")
            selected_year = st.sidebar.selectbox("اختر السنة", available_years, index=len(available_years)-1)
            selected_products = st.sidebar.multiselect("فئات المنتجات", PRODUCTS, default=PRODUCTS)
            selected_quarters = st.sidebar.multiselect("الأرباع السنوية", ["Q1", "Q2", "Q3", "Q4"], default=["Q1", "Q2", "Q3", "Q4"])

            filtered_df = clean_df[(clean_df["Year"] == selected_year) & (clean_df["Product"].isin(selected_products)) & (clean_df["Quarter"].isin(selected_quarters))].copy()

            # --- 1. KPIs ---
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

            # --- 2. الأداء الشهري العام ---
            st.subheader(f"📈 نظرة عامة على الأداء الشهري لعام {selected_year}")
            st.plotly_chart(plot_monthly_target_vs_actual(m_summary), use_container_width=True, config={'displayModeBar': False})

            # --- 3. تصميم نسب تحقيق المستهدف حسب فئة المنتج (المطابق للصورة المطلوبة تماماً) ---
            st.markdown("### 🎯 نسب تحقيق المستهدف حسب فئة المنتج")
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
                    st.plotly_chart(create_donut_chart(pct, prod_colors[prod]), use_container_width=True, config={'displayModeBar': False})
                    a_str = f"{a_val:,.2f}" if pd.notna(a_val) else "0.00"
                    st.markdown(f"**فئة {prod}**<br><span style='font-size:12px; color:#555;'>الفعلي: {a_str} / المستهدف: {t_val:,.2f}</span></div>", unsafe_allow_html=True)

            st.markdown("---")

            # --- 4. تفاصيل المبيعات الشهرية عبر بطاقات دائرية للشهر المحدد ---
            st.subheader(f"🔍 مقارنة منتجات الشهر المفصل (بطاقات نسب الإنجاز) - {selected_year}")
            selected_single_month = st.selectbox("اختر الشهر لعرض دوائر نسب تحقيقه الكاملة:", VALID_MONTHS, index=0)
            
            single_month_df = clean_df[
                (clean_df["Year"] == selected_year) & 
                (clean_df["Month"] == selected_single_month) &
                (clean_df["Product"].isin(selected_products))
            ].copy()
            single_month_enriched = enrich_metrics(single_month_df)

            sm_target = single_month_enriched["Target"].sum()
            sm_actual = single_month_enriched["Actual"].sum(min_count=1)
            sm_ach = (sm_actual / sm_target * 100) if (pd.notna(sm_actual) and sm_target > 0) else np.nan
            sm_var = (sm_actual - sm_target) if pd.notna(sm_actual) else np.nan

            sm1, sm2, sm3, sm4 = st.columns(4)
            sm1.metric(f"مستهدف شهر {selected_single_month}", f"{sm_target:,.2f}")
            sm2.metric(f"فعلي شهر {selected_single_month}", f"{sm_actual:,.2f}" if pd.notna(sm_actual) else "غير مسجل")
            sm3.metric("نسبة تحقيق الشهر", f"{sm_ach:.1f}%" if pd.notna(sm_ach) else "—")
            sm4.metric("الفارق (Variance)", f"{sm_var:+,.2f}" if pd.notna(sm_var) else "—")

            st.markdown(f"**نسب تحقيق المنتجات لشهر {selected_single_month}:**")
            m_d_cols = st.columns(len(PRODUCTS))
            for idx, prod in enumerate(PRODUCTS):
                p_row = single_month_enriched[single_month_enriched["Product"] == prod]
                p_pct = p_row["Achievement %"].values[0] if not p_row.empty else np.nan
                p_t = p_row["Target"].values[0] if not p_row.empty else 0
                p_a = p_row["Actual"].values[0] if not p_row.empty else np.nan
                
                with m_d_cols[idx]:
                    st.markdown(f"<div style='background-color: white; padding: 12px; border-radius: 12px; text-align: center;'>", unsafe_allow_html=True)
                    st.plotly_chart(create_donut_chart(p_pct, prod_colors[prod]), use_container_width=True, config={'displayModeBar': False})
                    p_a_str = f"{p_a:,.2f}" if pd.notna(p_a) else "0.00"
                    st.markdown(f"**{prod}**<br><span style='font-size:11px; color:#555;'>الفعلي: {p_a_str} <br> المستهدف: {p_t:,.2f}</span></div>", unsafe_allow_html=True)

            st.markdown("---")

            # --- 5. تفاصيل المبيعات اليومية ---
            st.subheader("📅 تحليل المبيعات اليومية (Daily Sales Breakdown)")
            daily_sheets = detect_daily_sales_data(sheets_dict)

            if not daily_sheets:
                st.info("لم يتم العثور على شيت يحتوي على تواريخ يومية داخل الملف المرفوع.")
            else:
                chosen_daily_sheet = st.selectbox("اختر شيت البيانات اليومية:", list(daily_sheets.keys()))
                daily_df, date_col_name = daily_sheets[chosen_daily_sheet]

                daily_years = sorted(daily_df["Parsed_Date"].dt.year.unique().tolist())
                d_col_f1, d_col_f2, d_col_f3 = st.columns(3)
                with d_col_f1:
                    d_year = st.selectbox("سنة المبيعات اليومية:", daily_years, index=len(daily_years)-1)
                
                daily_year_df = daily_df[daily_df["Parsed_Date"].dt.year == d_year].copy()
                daily_year_df["Month_Name"] = daily_year_df["Parsed_Date"].dt.strftime("%b")
                
                with d_col_f2:
                    avail_d_months = ["الكل"] + [m for m in VALID_MONTHS if m in daily_year_df["Month_Name"].unique()]
                    d_month = st.selectbox("تصفية بشهر معين (يومي):", avail_d_months)
                
                numeric_cols = [c for c in daily_year_df.select_dtypes(include=[np.number]).columns if c not in ["Year", "Month"]]
                with d_col_f3:
                    val_col = st.selectbox("اختر عمود القيمة / الكمية:", numeric_cols) if numeric_cols else None

                if d_month != "الكل":
                    daily_year_df = daily_year_df[daily_year_df["Month_Name"] == d_month]

                if val_col and not daily_year_df.empty:
                    daily_year_df["Date_Only"] = daily_year_df["Parsed_Date"].dt.date
                    daily_grouped = daily_year_df.groupby("Date_Only", as_index=False)[val_col].sum().sort_values("Date_Only")

                    total_d_sales = daily_grouped[val_col].sum()
                    avg_d_sales = daily_grouped[val_col].mean()
                    max_d_row = daily_grouped.loc[daily_grouped[val_col].idxmax()]
                    active_days = len(daily_grouped[daily_grouped[val_col] > 0])

                    dk1, dk2, dk3, dk4 = st.columns(4)
                    dk1.metric("إجمالي المبيعات للفترة", f"{total_d_sales:,.2f}")
                    dk2.metric("متوسط البيع اليومي", f"{avg_d_sales:,.2f}")
                    dk3.metric("أعلى يوم مبيعاً", f"{max_d_row['Date_Only']} ({max_d_row[val_col]:,.2f})")
                    dk4.metric("عدد أيام البيع المسجلة", f"{active_days} يوم")

                    fig_daily = px.bar(
                        daily_grouped, x="Date_Only", y=val_col,
                        title=f"المبيعات اليومية ({val_col}) - {d_month} {d_year}",
                        color_discrete_sequence=[COLORS["teal"]]
                    )
                    fig_daily.update_layout(plot_bgcolor=COLORS["white"], paper_bgcolor=COLORS["white"], xaxis_title="التاريخ", yaxis_title=val_col)
                    st.plotly_chart(fig_daily, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.dataframe(daily_year_df.drop(columns=["Parsed_Date"], errors="ignore"), use_container_width=True)

            st.markdown("---")

            # --- 6. التحليل الربعي ونصف السنوي ---
            st.subheader("🗓️ التحليل الربعي ونصف السنوي")
            q_summary = summarize_by_period(filtered_df, ["Quarter"])
            h_summary = summarize_by_period(filtered_df, ["Half"])
            qc1, qc2 = st.columns([3, 2])
            with qc1:
                fig_q = go.Figure()
                fig_q.add_trace(go.Bar(x=q_summary["Quarter"], y=q_summary["Target"], name="مستهدف الربع", marker_color=COLORS["navy_blue"]))
                fig_q.add_trace(go.Bar(x=q_summary["Quarter"], y=q_summary["Actual"], name="فعلي الربع", marker_color=COLORS["teal"]))
                fig_q.update_layout(barmode="group", plot_bgcolor=COLORS["white"], paper_bgcolor=COLORS["white"], font_color=COLORS["text"], margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_q, use_container_width=True, config={'displayModeBar': False})
            with qc2:
                st.dataframe(q_summary.style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)
                st.dataframe(h_summary.style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)

            st.markdown("---")

            # --- 7. الجداول التحليلية والتصدير ---
            st.subheader("📋 الجداول التحليلية المفصلة")
            tab1, tab2, tab3, tab4 = st.tabs(["التفصيل الشهري العام", f"تفصيل شهر {selected_single_month}", "تفصيل المنتجات", "مقارنة السنوات"])
            with tab1: st.dataframe(m_summary.drop(columns=["Month_Num"]).style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)
            with tab2: st.dataframe(single_month_enriched.drop(columns=["Month_Num"]).style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)
            with tab3: st.dataframe(summarize_by_period(filtered_df, ["Product", "Quarter"]).style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)
            with tab4: st.dataframe(summarize_by_period(clean_df[clean_df["Product"].isin(selected_products)], ["Year"]).style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"), use_container_width=True)

            st.markdown("### 📥 تصدير التقارير")
            export_sheets = {
                "Monthly_All": m_summary.drop(columns=["Month_Num"]),
                f"Month_{selected_single_month}": single_month_enriched.drop(columns=["Month_Num"]),
                "Quarterly": q_summary,
                "Half_Yearly": h_summary,
                "Products": p_summary
            }
            if daily_sheets and 'daily_grouped' in locals():
                export_sheets["Daily_Sales"] = daily_grouped

            excel_bytes = convert_dfs_to_excel(export_sheets)
            st.download_button("📊 تحميل التقرير الشامل (Excel متعدد الشيتات)", data=excel_bytes, file_name=f"Sales_Analysis_{selected_year}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
