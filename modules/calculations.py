import pandas as pd
import numpy as np

def enrich_metrics(df):
    """إضافة أعمدة الإنجاز والفجوة والباقي وفق القواعد الصارمة"""
    if df is None or df.empty:
        return df
    
    res = df.copy()
    # حساب الفجوة (Variance) والمتبقي (Remaining) فقط عند وجود بيانات فعلية ومستهدفة
    res["Variance"] = res["Actual"] - res["Target"]
    res["Remaining"] = res["Target"] - res["Actual"]
    
    # حساب نسبة التحقيق فقط إذا كان Target أكبر من صفر و Actual مسجلاً
    res["Achievement %"] = np.where(
        (res["Target"].notna()) & (res["Target"] > 0) & (res["Actual"].notna()),
        (res["Actual"] / res["Target"]) * 100,
        np.nan
    )
    return res

def summarize_by_period(df, group_cols):
    """تجميع البيانات (شهري، ربعي، نصف سنوي، أو حسب المنتج) مع الحفاظ على دقة النسب"""
    summary = df.groupby(group_cols, as_index=False, sort=False).agg(
        Target=("Target", "sum"),
        Actual=("Actual", lambda x: x.sum(min_count=1)) # تبقى NaN إذا كانت كل الأشهر غير مسجلة
    )
    return enrich_metrics(summary)
