import streamlit as st
import pandas as pd
from config import COLORS, YEARS, PRODUCTS
from modules.data_loader import load_excel_data
from modules.exports import convert_df_to_csv

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

# تحميل البيانات
file_path = "data/sales_data.xlsx"
df = load_excel_data(file_path)

if df is not None:
    st.sidebar.header("الفلاتر التفاعلية")
    selected_year = st.sidebar.selectbox("اختر السنة", YEARS)
    selected_product = st.sidebar.multiselect("اختر فئات المنتجات", PRODUCTS, default=PRODUCTS)
    
    st.subheader("عرض البيانات الأساسية لشيت Target")
    st.dataframe(df.head(10), use_container_width=True)
    
    # زر التنزيل
    csv = convert_df_to_csv(df)
    st.download_button(
        label="تنزيل البيانات بصيغة CSV",
        data=csv,
        file_name='sales_target_data.csv',
        mime='text/csv',
    )
else:
    st.warning("يرجى التأكد من وضع ملف Excel في مجلد data باسم sales_data.xlsx")
