import pandas as pd
import numpy as np

def parse_target_sheet(raw_df):
    """
    تحويل هيكل شيت Target الأفقي والمركب إلى جدول بيانات تحليلي نظيف (Tidy Data)
    مع الحفاظ التام على القيم الأصلية وعدم تحويل الفراغات أو النصوص إلى أصفار.
    """
    if raw_df is None or raw_df.empty:
        return None

    # تحديد صف العناوين الذي يحتوي على أسماء المنتجات (Min, Syn, DEO, Fluids)
    header_row_idx = None
    for idx, row in raw_df.iterrows():
        row_values = [str(val).strip() for val in row.values if pd.notna(val)]
        if "Min" in row_values and "Syn" in row_values:
            header_row_idx = idx
            break

    if header_row_idx is None:
        return None

    # استخراج صف السنوات (فوق صف المنتجات) وصف المنتجات
    year_row = raw_df.iloc[header_row_idx - 1] if header_row_idx > 0 else raw_df.columns
    prod_row = raw_df.iloc[header_row_idx]

    # ربط كل عمود بالسنة والمنتج الخاص به
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

    # استخراج البيانات الشهرية (بعد صف العناوين)
    data_rows = raw_df.iloc[header_row_idx + 1:].copy()
    records = []
    current_month = None
    valid_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    quarter_map = {
        "Jan": "Q1", "Feb": "Q1", "Mar": "Q1",
        "Apr": "Q2", "May": "Q2", "Jun": "Q2",
        "Jul": "Q3", "Aug": "Q3", "Sep": "Q3",
        "Oct": "Q4", "Nov": "Q4", "Dec": "Q4"
    }
    half_map = {
        "Jan": "H1", "Feb": "H1", "Mar": "H1", "Apr": "H1", "May": "H1", "Jun": "H1",
        "Jul": "H2", "Aug": "H2", "Sep": "H2", "Oct": "H2", "Nov": "H2", "Dec": "H2"
    }

    for _, row in data_rows.iterrows():
        col0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        col1 = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""

        # التوقف عند الوصول إلى الإجماليات السنوية أو ملخصات الأرباع في الشيت الأصلي
        if any(stop_word in col0.lower() for stop_word in ["total", "q1", "quarter", "annual", "ytd"]):
            break

        if col0 in valid_months:
            current_month = col0

        if current_month and col1 in ["Target", "Actual"]:
            metric_type = col1
            for col_idx, (year, product) in col_mapping.items():
                raw_val = row.iloc[col_idx]
                # تحويل القيم الرقمية فقط وترك النصوص (مثل Pre-joining) أو الفراغات كـ NaN
                num_val = pd.to_numeric(raw_val, errors='coerce')
                records.append({
                    "Year": year,
                    "Month": current_month,
                    "Month_Num": valid_months.index(current_month) + 1,
                    "Quarter": quarter_map[current_month],
                    "Half": half_map[current_month],
                    "Product": product,
                    "Type": metric_type,
                    "Value": num_val
                })

    if not records:
        return None

    long_df = pd.DataFrame(records)
    
    # تحويل Target و Actual إلى أعمدة متجاورة لكل شهر ومنتج وسنة
    pivoted = long_df.pivot_table(
        index=["Year", "Month", "Month_Num", "Quarter", "Half", "Product"],
        columns="Type",
        values="Value",
        aggfunc="first"
    ).reset_index()

    pivoted.columns.name = None
    if "Target" not in pivoted.columns:
        pivoted["Target"] = np.nan
    if "Actual" not in pivoted.columns:
        pivoted["Actual"] = np.nan

    return pivoted.sort_values(["Year", "Month_Num", "Product"])
