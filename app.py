import streamlit as st
import pandas as pd
import numpy as np
from config import COLORS, PRODUCTS
from modules.data_loader import load_excel_data
from modules.data_processor import parse_target_sheet
from modules.calculations import enrich_metrics, summarize_by_period
from modules.charts import (
    plot_monthly_target_vs_actual,
    plot_monthly_growth_line,
    plot_quarterly_comparison,
    create_donut_chart
)
from modules.exports import convert_df_to_csv, convert_dfs_to_excel

st.set_page_config(
    page_title="لوحة تحكم أداء المبيعات المتقدمة",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.title("📊 لوحة تحكم أداء المبيعات والتحليل المتقدم")
st.markdown("تحليل شامل للمستهدف والمبيعات الفعلية (شهري، ربعي، نصف سنوي، وحسب فئات المنتجات).")

# --- القائمة الجانبية ---
st.sidebar.header("📂 مصدر البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف Excel (.xlsx أو .xlsb)", type=["xlsx", "xls", "xlsb"])

raw_df = load_excel_data(uploaded_file)

if raw_df is not None:
    clean_df = parse_target_sheet(raw_df)
    
    if clean_df is None or clean_df.empty:
        st.error("تعذر التعرف على هيكل البيانات داخل شيت Target. تأكد من وجود أسماء المنتجات (Min, Syn, DEO, Fluids).")
    else:
        available_years = sorted(clean_df["Year"].unique().tolist())
        
        st.sidebar.header("🎛️ الفلاتر التفاعلية")
        selected_year = st.sidebar.selectbox("اختر السنة", available_years, index=len(available_years)-1)
        selected_products = st.sidebar.multiselect("فئات المنتجات", PRODUCTS, default=PRODUCTS)
        selected_quarters = st.sidebar.multiselect("الأرباع السنوية", ["Q1", "Q2", "Q3", "Q4"], default=["Q1", "Q2", "Q3", "Q4"])

        # تطبيق الفلاتر
        filtered_df = clean_df[
            (clean_df["Year"] == selected_year) &
            (clean_df["Product"].isin(selected_products)) &
            (clean_df["Quarter"].isin(selected_quarters))
        ].copy()

        # --- 1. بطاقات المؤشرات الرئيسية (KPI Cards) ---
        total_target = filtered_df["Target"].sum()
        total_actual = filtered_df["Actual"].sum(min_count=1)
        ach_pct = (total_actual / total_target * 100) if (pd.notna(total_actual) and total_target > 0) else np.nan
        remaining = (total_target - total_actual) if pd.notna(total_actual) else total_target

        # أفضل شهر وأفضل منتج
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
        k4.metric("المتبقي للمستهدف", f"{remaining:,.2f}")
        k5.metric("أفضل شهر مبيعاً", best_month)
        k6.metric("أفضل منتج", best_prod)

        st.markdown("---")

        # --- 2. القسم العلوي: التحليل الشهري (Bar + Line) ---
        st.subheader(f"📈 الأداء الشهري المفصل لعام {selected_year}")
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown("**مقارنة المستهدف بالفعلي شهرياً**")
            st.plotly_chart(plot_monthly_target_vs_actual(m_summary), use_container_width=True)
        with c2:
            st.markdown("**مسار النمو الشهري (Trend)**")
            st.plotly_chart(plot_monthly_growth_line(m_summary), use_container_width=True)

        # --- 3. القسم السفلي: دوائر الإنجاز الحقيقية للمنتجات الأربعة ---
        st.subheader("🎯 نسب تحقيق المستهدف حسب فئة المنتج")
        year_prod_df = summarize_by_period(
            clean_df[(clean_df["Year"] == selected_year) & (clean_df["Quarter"].isin(selected_quarters))],
            ["Product"]
        )
        
        prod_colors = {
            "Min": COLORS["dark_blue"],
            "Syn": COLORS["orange"],
            "DEO": COLORS["teal"],
            "Fluids": COLORS["navy_blue"]
        }
        
        d_cols = st.columns(4)
        for idx, prod in enumerate(PRODUCTS):
            row = year_prod_df[year_prod_df["Product"] == prod]
            pct = row["Achievement %"].values[0] if not row.empty else np.nan
            t_val = row["Target"].values[0] if not row.empty else 0
            a_val = row["Actual"].values[0] if not row.empty else np.nan
            
            with d_cols[idx]:
                st.markdown(f"<div style='background-color: white; padding: 12px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); text-align: center;'>", unsafe_allow_html=True)
                st.plotly_chart(create_donut_chart(pct, prod_colors[prod]), use_container_width=True)
                a_str = f"{a_val:,.2f}" if pd.notna(a_val) else "0.00"
                st.markdown(f"**فئة {prod}**<br><span style='font-size:13px; color:#555;'>الفعلي: {a_str} / المستهدف: {t_val:,.2f}</span></div>", unsafe_allow_html=True)

        st.markdown("---")

        # --- 4. التحليل الربعي ونصف السنوي ومقارنة السنوات ---
        st.subheader("🗓️ التحليل الربعي (Q1 - Q4) ونصف السنوي (H1 - H2)")
        q_summary = summarize_by_period(filtered_df, ["Quarter"])
        h_summary = summarize_by_period(filtered_df, ["Half"])

        qc1, qc2 = st.columns([3, 2])
        with qc1:
            st.markdown("**أداء الأرباع السنوية (المستهدف مقابل الفعلي)**")
            st.plotly_chart(plot_quarterly_comparison(q_summary), use_container_width=True)
        with qc2:
            st.markdown("**ملخص الأرباع (Q1 - Q4)**")
            st.dataframe(
                q_summary.style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Variance": "{:,.2f}", "Remaining": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"),
                use_container_width=True
            )
            st.markdown("**ملخص النصف الأول والثاني (H1 - H2)**")
            st.dataframe(
                h_summary.style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Variance": "{:,.2f}", "Remaining": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"),
                use_container_width=True
            )

        st.markdown("---")

        # --- 5. الجداول التفصيلية والتصدير ---
        st.subheader("📋 الجداول التحليلية المفصلة")
        tab1, tab2, tab3, tab4 = st.tabs(["التفصيل الشهري", "تفصيل المنتجات", "مقارنة السنوات", "البيانات الخام المعالجة"])

        with tab1:
            st.dataframe(
                m_summary.drop(columns=["Month_Num"]).style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Variance": "{:,.2f}", "Remaining": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"),
                use_container_width=True
            )

        with tab2:
            prod_detail = summarize_by_period(filtered_df, ["Product", "Quarter"])
            st.dataframe(
                prod_detail.style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Variance": "{:,.2f}", "Remaining": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"),
                use_container_width=True
            )

        with tab3:
            annual_comp = summarize_by_period(clean_df[clean_df["Product"].isin(selected_products)], ["Year"])
            st.dataframe(
                annual_comp.style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Variance": "{:,.2f}", "Remaining": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"),
                use_container_width=True
            )

        with tab4:
            enriched_all = enrich_metrics(filtered_df).drop(columns=["Month_Num"])
            st.dataframe(
                enriched_all.style.format({"Target": "{:,.2f}", "Actual": "{:,.2f}", "Variance": "{:,.2f}", "Remaining": "{:,.2f}", "Achievement %": "{:.1f}%"}, na_rep="—"),
                use_container_width=True
            )

        # أزرار التصدير الاحترافية
        st.markdown("### 📥 تصدير التقارير")
        exp1, exp2 = st.columns(2)
        with exp1:
            excel_bytes = convert_dfs_to_excel({
                "Monthly_Summary": m_summary.drop(columns=["Month_Num"]),
                "Quarterly_Summary": q_summary,
                "Half_Yearly_Summary": h_summary,
                "Product_Summary": p_summary,
                "Full_Detailed_Data": enrich_metrics(filtered_df).drop(columns=["Month_Num"])
            })
            st.download_button(
                label="📊 تحميل التقرير الشامل (Excel متعدد الشيتات)",
                data=excel_bytes,
                file_name=f"Sales_Analysis_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with exp2:
            csv_bytes = convert_df_to_csv(enrich_metrics(filtered_df).drop(columns=["Month_Num"]))
            st.download_button(
                label="📄 تحميل البيانات المفصلة (CSV)",
                data=csv_bytes,
                file_name=f"Sales_Data_{selected_year}.csv",
                mime="text/csv"
            )
else:
    st.info("👈 ارفع ملف Excel الخاص بالمبيعات من القائمة الجانبية لعرض التحليل الشهري والربعي الكامل.")
