import streamlit as st
import pandas as pd
from config import COLORS, YEARS, PRODUCTS
from modules.data_loader import load_excel_data
from modules.exports import convert_df_to_csv
from modules.charts import create_bar_chart, create_line_chart, create_donut_chart

st.set_page_config(
    page_title="لوحة تحكم أداء المبيعات",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق ملف الـ CSS
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.title("📊 لوحة تحكم أداء المبيعات والتحليل المتقدم")
st.markdown("متابعة المستهدف والمبيعات الفعلية ومقارنة الأداء للشركات الكبرى.")

# القائمة الجانبية لإدارة الملفات والفلاتر
st.sidebar.header("إدارة البيانات والفلاتر")
uploaded_file = st.sidebar.file_uploader("اختر ملف Excel (.xlsx أو .xlsb)", type=["xlsx", "xls", "xlsb"])

df = load_excel_data(uploaded_file)

if df is not None:
    st.sidebar.success("تم تحميل البيانات بنجاح!")
    
    selected_year = st.sidebar.selectbox("اختر السنة", YEARS)
    selected_product = st.sidebar.multiselect("اختر فئات المنتجات", PRODUCTS, default=PRODUCTS)
    
    # --- القسم العلوي: الرسوم البيانية (Bar Chart & Line Chart) ---
    st.markdown("### نظرة عامة على الأداء والنمو")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### المقارنة السنوية / الأداء")
        bar_fig = create_bar_chart(df.select_dtypes(include='number').head(4))
        st.plotly_chart(bar_fig, use_container_width=True)
        
    with col2:
        st.markdown("#### مسار النمو الشهري")
        line_fig = create_line_chart(df)
        st.plotly_chart(line_fig, use_container_width=True)

    # --- القسم السفلي: 4 بطاقات مؤشرات أداء دائرية (KPI Donut Charts) ---
    st.markdown("### نسب تحقيق المستهدف حسب الفئات")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown("<div style='background-color: white; padding: 15px; border-radius: 10px; text-align: center;'>", unsafe_allow_html=True)
        st.plotly_chart(create_donut_chart(85, "Min Product", COLORS["dark_blue"]), use_container_width=True)
        st.markdown("<p style='text-align: center; font-weight: bold;'>فئة Min</p></div>", unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown("<div style='background-color: white; padding: 15px; border-radius: 10px; text-align: center;'>", unsafe_allow_html=True)
        st.plotly_chart(create_donut_chart(75, "Syn Product", COLORS["orange"]), use_container_width=True)
        st.markdown("<p style='text-align: center; font-weight: bold;'>فئة Syn</p></div>", unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown("<div style='background-color: white; padding: 15px; border-radius: 10px; text-align: center;'>", unsafe_allow_html=True)
        st.plotly_chart(create_donut_chart(98, "DEO Product", COLORS["teal"]), use_container_width=True)
        st.markdown("<p style='text-align: center; font-weight: bold;'>فئة DEO</p></div>", unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown("<div style='background-color: white; padding: 15px; border-radius: 10px; text-align: center;'>", unsafe_allow_html=True)
        st.plotly_chart(create_donut_chart(55, "Fluids Product", COLORS["navy_blue"]), use_container_width=True)
        st.markdown("<p style='text-align: center; font-weight: bold;'>فئة Fluids</p></div>", unsafe_allow_html=True)

    # عرض جدول البيانات للتفصيل
    with st.expander("عرض تفاصيل جدول بيانات Target"):
        st.dataframe(df, use_container_width=True)
        
    # زر التنزيل
    csv = convert_df_to_csv(df)
    st.download_button(
        label="تنزيل البيانات بصيغة CSV",
        data=csv,
        file_name='sales_target_data.csv',
        mime='text/csv',
    )
else:
    st.warning("⚠️ يرجى رفع ملف Excel باستخدام القائمة الجانبية لعرض لوحة التحكم بالرسوم البيانية الكاملة.")
