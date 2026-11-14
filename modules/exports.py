import pandas as pd
import io

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

def convert_dfs_to_excel(sheets_dict):
    """تصدير عدة جداول (شهري، ربعي، منتجات) في ملف Excel واحد متعدد الشيتات"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, dataframe in sheets_dict.items():
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()
