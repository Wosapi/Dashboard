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

# --- 
