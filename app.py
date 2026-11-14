# الصف الثاني: تحليل الشهر والمبيعات اليومية
month_col, daily_col = st.columns(2, gap="medium")

with month_col:

    month = st.selectbox(
        t["select_month"],
        MONTHS,
        index=10,
        key="month_choice"
    )

    render_panel(
        t["month"],
        month,
        year_data[year_data.Month == month],
        "month",
        icon="📅",
        full_width=False
    )


with daily_col:

    st.markdown(
        f'<div class="panel-heading">📋 {t["daily"]}</div>',
        unsafe_allow_html=True
    )

    daily_df = daily_data_from_sheet(
        sheets,
        active_year=year
    )

    if daily_df is None or daily_df.empty:

        st.warning(
            "⚠️ لم يتم العثور على بيانات صحيحة في شيت Data. "
            "تأكد من وجود الأعمدة Amount وDate."
        )

    else:

        # فلترة السنة الفعلية دون تغيير التواريخ
        dy_filtered = daily_df[
            daily_df["Parsed_Date"].dt.year == int(year)
        ].copy()

        # فلترة الشهر المختار
        dy_filtered = dy_filtered[
            dy_filtered["Parsed_Date"].dt.month
            == MONTHS.index(month) + 1
        ].copy()

        if dy_filtered.empty:

            st.info(
                f"لا توجد مبيعات خلال {month} لعام {year}."
            )

        else:

            min_d = dy_filtered["Date_Only"].min().date()
            max_d = dy_filtered["Date_Only"].max().date()

            st.markdown(
                f'<div class="period-badge">'
                f'📅 {month} {year} | من {min_d} إلى {max_d}'
                f'</div>',
                unsafe_allow_html=True
            )

            filter_mode = st.radio(
                "طريقة عرض المبيعات:",
                [
                    "جميع الأيام",
                    "تاريخ محدد",
                    "نطاق تاريخي"
                ],
                horizontal=True,
                key="daily_filter_mode"
            )

            if filter_mode == "تاريخ محدد":

                selected_date = st.date_input(
                    "اختر تاريخ المبيعات:",
                    value=max_d,
                    min_value=min_d,
                    max_value=max_d,
                    key="daily_single_date"
                )

                dy_filtered = dy_filtered[
                    dy_filtered["Date_Only"].dt.date
                    == selected_date
                ]

            elif filter_mode == "نطاق تاريخي":

                date_range = st.date_input(
                    "اختر فترة المبيعات:",
                    value=(min_d, max_d),
                    min_value=min_d,
                    max_value=max_d,
                    key="daily_date_range"
                )

                if isinstance(date_range, (tuple, list)):

                    if len(date_range) == 2:

                        start_d, end_d = date_range

                        if start_d and end_d:

                            dy_filtered = dy_filtered[
                                (dy_filtered["Date_Only"].dt.date >= start_d)
                                &
                                (dy_filtered["Date_Only"].dt.date <= end_d)
                            ]

            if not dy_filtered.empty:

                # تجميع المبيعات حسب التاريخ
                grouped_daily = (
                    dy_filtered.groupby("Date_Only")
                    .agg(
                        Sales_Count=(
                            "Invoice_No",
                            lambda x: x.nunique()
                        ),
                        Total_I_Sum=(
                            "Total_I",
                            lambda x: x.sum(min_count=1)
                        ),
                        Customer_Count=(
                            "Customer",
                            "nunique"
                        ),
                        Total_Amount=(
                            "Amount",
                            lambda x: x.sum(min_count=1)
                        )
                    )
                    .reset_index()
                    .sort_values("Date_Only", ascending=False)
                )

                # عرض أسماء الأعمدة بالعربية
                grouped_daily = grouped_daily.rename(
                    columns={
                        "Date_Only": "التاريخ",
                        "Sales_Count": "عدد الفواتير",
                        "Total_I_Sum": "إجمالي الكميات",
                        "Customer_Count": "عدد العملاء",
                        "Total_Amount": "مبيعات SAR"
                    }
                )

                # تنسيق الجدول
                st.dataframe(
                    grouped_daily.style.format(
                        {
                            "إجمالي الكميات": "{:,.2f}",
                            "مبيعات SAR": "{:,.2f}"
                        },
                        na_rep="—"
                    ),
                    use_container_width=True,
                    hide_index=True,
                    height=250
                )

                # إجماليات الفترة المعروضة
                st.markdown("**ملخص المبيعات اليومية**")

                total_amount = dy_filtered["Amount"].sum()
                total_qty = dy_filtered["Total_I"].sum()

                invoice_count = dy_filtered[
                    "Invoice_No"
                ].nunique()

                customer_count = dy_filtered[
                    "Customer"
                ].nunique()

                m1, m2 = st.columns(2)

                m1.metric(
                    "إجمالي المبيعات",
                    f"{total_amount:,.2f} SAR"
                )

                m2.metric(
                    "إجمالي الكميات",
                    f"{total_qty:,.2f}"
                )

                m3, m4 = st.columns(2)

                m3.metric(
                    "عدد الفواتير",
                    f"{invoice_count:,}"
                )

                m4.metric(
                    "عدد العملاء",
                    f"{customer_count:,}"
                )

            else:

                st.warning(
                    "لا توجد مبيعات في التاريخ المحدد."
                )
