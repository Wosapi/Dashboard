import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_excel_data(uploaded_file):
    """قراءة جميع الشيتات والتركيز على شيت Target سواء من ملف مرفوع أو المسار الافتراضي"""
    try:
        if uploaded_file is not None:
            xls = pd.ExcelFile(uploaded_file)
        else:
            file_path = "data/sales_data.xlsx"
            if not os.path.exists(file_path):
                return None
            xls = pd.ExcelFile(file_path)
            
        sheet_names = xls.sheet_names
        
        if "Target" not in sheet_names:
            st.error("شيت 'Target' غير موجود في ملف Excel المرفق.")
            return None
            
        target_df = pd.read_excel(xls, sheet_name="Target")
        return target_df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة ملف Excel: {e}")
        return None
