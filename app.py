def daily_data_from_sheet(sheets, active_year=None):
    """
    استخراج المبيعات اليومية من شيت Data.
    يعتمد على أسماء الأعمدة، مع دعم ترتيب الأعمدة الأصلي.
    """

    # البحث عن شيت Data
    sheet_name = next(
        (
            n for n in sheets
            if n.strip().lower() in ["data", "بيانات", "البيانات"]
        ),
        None
    )

    if sheet_name is None:
        return None

    df = sheets[sheet_name].copy()

    if df.empty or df.shape[1] < 9:
        return None

    # تنظيف أسماء الأعمدة
    def clean_name(name):
        return (
            str(name)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

    headers = {clean_name(c): c for c in df.columns}

    # البحث عن الأعمدة حسب الاسم
    def find_column(names, fallback_index):
        for name in names:
            key = clean_name(name)
            if key in headers:
                return headers[key]

        # الرجوع إلى ترتيب الأعمدة في صورة Excel
        if fallback_index < len(df.columns):
            return df.columns[fallback_index]

        return None

    amount_col = find_column(
        ["Amount"], 2
    )

    invoice_col = find_column(
        ["Invoice No", "Invoice Number"], 3
    )

    customer_col = find_column(
        ["Customer - No", "Customer No", "Customer-No"], 4
    )

    quantity_col = find_column(
        ["Total Quantities", "Total Quantity"], 7
    )

    date_col = find_column(
        ["Date", "Sales Date", "Invoice Date"], 8
    )

    if date_col is None:
        return None

    # تحويل البيانات إلى جدول موحد
    res = pd.DataFrame(index=df.index)

    res["Parsed_Date"] = parse_excel_date(df[date_col])

    def to_number(series):
        return pd.to_numeric(
            series.astype(str)
            .str.replace(",", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace("SAR", "", regex=False),
            errors="coerce"
        )

    res["Amount"] = (
        to_number(df[amount_col])
        if amount_col is not None
        else np.nan
    )

    res["Total_I"] = (
        to_number(df[quantity_col])
        if quantity_col is not None
        else np.nan
    )

    res["Customer"] = (
        df[customer_col]
        if customer_col is not None
        else None
    )

    res["Invoice_No"] = (
        df[invoice_col]
        if invoice_col is not None
        else None
    )

    # حذف الصفوف التي لا تحتوي على تاريخ صحيح
    res = res.dropna(subset=["Parsed_Date"]).copy()

    # تنظيف أرقام العملاء
    res["Customer"] = res["Customer"].astype("string").str.strip()
    res["Invoice_No"] = res["Invoice_No"].astype("string").str.strip()

    valid_customer = (
        res["Customer"].notna()
        & ~res["Customer"].isin(["", "nan", "None"])
    )

    valid_invoice = (
        res["Invoice_No"].notna()
        & ~res["Invoice_No"].isin(["", "nan", "None"])
    )

    valid_amount = res["Amount"].fillna(0) != 0
    valid_quantity = res["Total_I"].fillna(0) != 0

    # الاحتفاظ بحركات البيع الفعلية فقط
    res = res[
        valid_customer
        | valid_invoice
        | valid_amount
        | valid_quantity
    ].copy()

    # إضافة التاريخ بدون الوقت
    res["Date_Only"] = res["Parsed_Date"].dt.normalize()

    return res.reset_index(drop=True)
