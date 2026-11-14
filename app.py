# --- 3. محرك استخراج وتحليل المبيعات اليومية (المحدث لتجنب تكرار الأعمدة) ---
def detect_daily_sales_data(sheets_dict):
    candidate_sheets = {}
    for sheet_name, df in sheets_dict.items():
        if sheet_name == "Target" or df is None or df.empty:
            continue
        
        clean_sheet = df.copy()
        
        # إزالة الأعمدة ذات الأسماء المتكررة أو الفارغة لمنع خطأ duplicate keys
        clean_sheet = clean_sheet.loc[:, ~clean_sheet.columns.duplicated()]
        
        for idx in range(min(10, len(clean_sheet))):
            row_vals = [str(v).lower() for v in clean_sheet.iloc[idx].values if pd.notna(v)]
            if any(k in " ".join(row_vals) for k in ["date", "تاريخ", "day", "يوم", "qty", "quantity", "sales", "amount", "ton", "volume", "مبيعات", "كمية"]):
                clean_sheet.columns = clean_sheet.iloc[idx]
                clean_sheet = clean_sheet.iloc[idx + 1:].reset_index(drop=True)
                clean_sheet = clean_sheet.loc[:, ~clean_sheet.columns.duplicated()]
                break

        clean_sheet = clean_sheet.loc[:, clean_sheet.columns.notna()]
        clean_sheet.columns = [str(c).strip() for c in clean_sheet.columns]
        
        date_col = None
        for col in clean_sheet.columns:
            col_l = col.lower()
            if any(k in col_l for k in ["date", "تاريخ", "day", "يوم"]):
                s = clean_sheet[col]
                try:
                    if pd.api.types.is_numeric_dtype(s):
                        parsed = pd.to_datetime(s, unit='D', origin='1899-12-30', errors='coerce')
                    else:
                        parsed = pd.to_datetime(s, errors='coerce')
                    
                    if parsed.notna().sum() >= 3:
                        clean_sheet["Parsed_Date"] = parsed
                        date_col = col
                        break
                except Exception:
                    continue
        
        if date_col is not None:
            valid_daily = clean_sheet.dropna(subset=["Parsed_Date"]).copy()
            valid_daily = valid_daily[(valid_daily["Parsed_Date"].dt.year >= 2020) & (valid_daily["Parsed_Date"].dt.year <= 2030)]
            if not valid_daily.empty:
                candidate_sheets[sheet_name] = (valid_daily, date_col)
                
    return candidate_sheets
