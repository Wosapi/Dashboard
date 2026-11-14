import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_excel_data(uploaded_file):
    """قراءة ملفات إكسل (بما فيها .xlsb و .xlsx) والتركيز على شيت Target"""
    try:
        if uploaded_file is not None:
            # التحقق من امتداد الملف المرفوع لمعرفة المحرك المناسب للقراءة
            file_name = uploaded_file.name.lower()
            if file_name.endswith('.xlsb'):
                xls = pd.ExcelFile(uploaded_file, engine='pyxlsb')
            else:
                xls = pd.ExcelFile(uploaded_file)
        else:
            file_path = "data/sales_data.xlsx"
            if not os.path.exists(file_path):
                return None
            xls = pd.ExcelFile(file_path)
            
        sheet_names = xls.sheet_names
        
        if "Target" not in sheet_names:
            st.error(f"شيت 'Target' غير موجود في الملف. الشيتات الموجودة هي: {sheet_names}")
            return None
            
        target_df = pd.read_excel(xls, sheet_name="Target")
        return target_df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة ملف Excel: {e}")
        return None

