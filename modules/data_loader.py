import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_excel_data(file_path):
    """قراءة جميع الشيتات والتركيز على شيت Target مع معالجة الأخطاء"""
    if not os.path.exists(file_path):
        st.error(f"ملف البيانات غير موجود في المسار: {file_path}")
        return None
    
    try:
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
