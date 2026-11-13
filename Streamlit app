# -*- coding: utf-8 -*-
"""لوحة تحليل المبيعات — التشغيل: streamlit run streamlit_app.py"""
import io

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="لوحة تحليل المبيعات", page_icon="📊", layout="wide")
st.markdown("""<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {direction: rtl; text-align: right;}
[data-testid="stMetric"] {background:#F3F6F9; border-radius:12px; padding:12px 16px;}
.js-plotly-plot, .stPlotlyChart {direction: ltr;}
</style>""", unsafe_allow_html=True)

PRODUCTS = ["PCMO-Min 24L", "PCMO-Min 12L", "PCMO-Syn", "DEO 5L", "DEO 4L", "DEO 1L", "Fluids 4L", "Fluids 12L"]
MONTHS = {1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
          7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"}
MNAMES = list(MONTHS.values())
PALETTE = ["#3E6D9C", "#7FB5A8", "#E3A857", "#C46A6A", "#8E7DBE", "#9AA5B1", "#5C8F6B", "#D98E73"]


# ───────────────────────── تحميل وتنظيف البيانات ─────────────────────────
def clean_raw(raw: pd.DataFrame) -> pd.DataFrame:
    """ورقة Data الخام -> صفوف مبيعات نظيفة (يحذف صفوف السداد/الإيداع ذات الكمية صفر)."""
    raw = raw.copy()
    raw.columns = [" ".join(str(c).split()) for c in raw.columns]
    raw = raw.rename(columns={"Invoice No": "Invoice", "Customer - name": "Customer", "Total Quantities": "Qty"})
    d = raw["Date"]
    if pd.api.types.is_numeric_dtype(d):  # xlsb قد يعيد التاريخ كرقم تسلسلي
        d = pd.to_datetime(d, unit="D", origin="1899-12-30", errors="coerce")
    else:
        d = pd.to_datetime(d, errors="coerce")
    df = pd.DataFrame({"Date": d, "Invoice": raw.get("Invoice"), "Customer": raw.get("Customer"),
                       "Area": raw.get("Area"), "Qty": pd.to_numeric(raw["Qty"], errors="coerce")})
    for p in PRODUCTS:  # خلية المنتج الفارغة = لا وحدات من هذا المنتج في الفاتورة
        df[p] = pd.to_numeric(raw[p], errors="coerce").fillna(0) if p in raw else 0
    df = df.dropna(subset=["Date"])
    df = df[df["Qty"].fillna(0) > 0]
    df["Area"] = df["Area"].replace({0: np.nan, "0": np.nan}).fillna("غير محدد").astype(str).str.strip()
    df["Invoice"] = df["Invoice"].astype(str)
    return df.reset_index(drop=True)


@st.cache_data
def load_data(content, name):
    if content is None:
        df = pd.read_csv("sales_clean.csv", parse_dates=["Date"], dtype={"Invoice": str})
    elif name.lower().endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content), parse_dates=["Date"], dtype={"Invoice": str})
    else:
        engine = "pyxlsb" if name.lower().endswith(".xlsb") else None
        df = clean_raw(pd.read_excel(io.BytesIO(content), sheet_name="Data", engine=engine))
    df["Year"], df["Month"], df["Quarter"] = df.Date.dt.year, df.Date.dt.month, df.Date.dt.quarter
    df["Half"] = np.where(df.Month <= 6, "H1", "H2")
    return df


def partial_months(df):
    """الشهر الأول/الأخير إن كان غير مكتمل — يُستثنى من مقارنات النمو والموسمية."""
    lo, hi, p = df.Date.min(), df.Date.max(), set()
    if lo.day > 1:
        p.add((lo.year, lo.month))
    if hi.normalize() != hi + pd.offsets.MonthEnd(0):
        p.add((hi.year, hi.month))
    return p


def common_months(d, cur, prev, partial):
    """الأشهر المسجّل فيها بيانات في السنتين معاً (غياب الشهر ≠ صفر مبيعات)."""
    have = d.groupby(["Year", "Month"]).Qty.sum().index
    return [m for m in range(1, 13) if (cur, m) in have and (prev, m) in have
            and (cur, m) not in partial and (prev, m) not in partial]


df = load_data(None, "")
up = st.sidebar.file_uploader("رفع ملف المبيعات (xlsx / xlsb / csv)", type=["xlsx", "xlsb", "csv"])
if up is not None:
    df = load_data(up.getvalue(), up.name)
PARTIAL = partial_months(df)

# ───────────────────────── الفلاتر ─────────────────────────
st.sidebar.header("الفلاتر")
years = sorted(df.Year.unique())
areas = sorted(df.Area.unique())
sel_y = st.sidebar.multiselect("السنة", years, default=years)
sel_h = st.sidebar.multiselect("النصف السنوي", ["H1", "H2"], default=["H1", "H2"])
sel_q = st.sidebar.multiselect("الربع السنوي", [1, 2, 3, 4], default=[1, 2, 3, 4], format_func=lambda q: f"Q{q}")
sel_m = st.sidebar.multiselect("الشهر", list(MONTHS), default=list(MONTHS), format_func=MONTHS.get)
sel_a = st.sidebar.multiselect("المنطقة", areas, default=areas)

scope = df[df.Half.isin(sel_h) & df.Quarter.isin(sel_q) & df.Month.isin(sel_m)]
base = scope[scope.Area.isin(sel_a)]
f = base[base.Year.isin(sel_y)]
st.title("📊 لوحة تحليل المبيعات")
st.caption(f"البيانات من {df.Date.min():%Y-%m-%d} إلى {df.Date.max():%Y-%m-%d} • الكميات بالوحدات • "
           "الشرطة (—) = لا توجد بيانات مسجلة لذلك الشهر وليست مبيعات صفرية")
if f.empty:
    st.warning("لا توجد بيانات مطابقة للفلاتر المختارة.")
    st.stop()

# ───────────────────────── KPIs ─────────────────────────
cur = max(sel_y)
prev = cur - 1
ms = common_months(scope, cur, prev, PARTIAL)
growth = None
if ms:
    a = base[(base.Year == prev) & base.Month.isin(ms)].Qty.sum()
    b = base[(base.Year == cur) & base.Month.isin(ms)].Qty.sum()
    growth = b / a - 1 if a else None
k1, k2, k3, k4 = st.columns(4)
k1.metric("إجمالي الكميات", f"{f.Qty.sum():,.0f}")
k2.metric(f"نمو {cur} مقابل {prev}", f"{growth:+.1%}" if growth is not None else "—",
          help=f"مقارنة على الأشهر المتاحة في السنتين فقط ({len(ms)} أشهر)، دون الأشهر الجزئية أو الغائبة")
k3.metric("عدد الطلبات", f"{len(f):,}")
k4.metric("متوسط الكمية للطلب", f"{f.Qty.mean():,.1f}")

# ───────────────────────── المبيعات الشهرية ─────────────────────────
st.subheader("المبيعات الشهرية")
mt = f.groupby(["Year", "Month"], as_index=False).Qty.sum()
pv = mt.pivot(index="Month", columns="Year", values="Qty").reindex(range(1, 13))
mt["الشهر"], mt["السنة"] = mt.Month.map(MONTHS), mt.Year.astype(str)
fig = px.bar(mt, x="الشهر", y="Qty", color="السنة", barmode="group", labels={"Qty": "الكمية"},
             category_orders={"الشهر": MNAMES}, color_discrete_sequence=PALETTE)
fig.update_yaxes(tickformat=",")
st.plotly_chart(fig, use_container_width=True)
tbl = pv.copy()
tbl.index = MNAMES
tbl.columns = [str(c) for c in tbl.columns]
tbl["الإجمالي"] = tbl.sum(axis=1, min_count=1)
st.dataframe(tbl.style.format("{:,.0f}", na_rep="—"), use_container_width=True)

st.subheader("المبيعات الشهرية حسب فئة المنتج")
pm = f.groupby(["Year", "Month"])[PRODUCTS].sum().reset_index()
pm["الفترة"] = pm.Year.astype(str) + "-" + pm.Month.astype(str).str.zfill(2)
long = pm.melt(id_vars="الفترة", value_vars=PRODUCTS, var_name="الفئة", value_name="الكمية")
t1, t2 = st.tabs(["رسم بياني", "جدول"])
fig = px.bar(long, x="الفترة", y="الكمية", color="الفئة", color_discrete_sequence=PALETTE)
fig.update_yaxes(tickformat=",")
t1.plotly_chart(fig, use_container_width=True)
t2.dataframe(pm.set_index("الفترة")[PRODUCTS].style.format("{:,.0f}"), use_container_width=True)

# ───────────────────────── الاتجاه والموسمية ─────────────────────────
st.subheader("اتجاه المبيعات والموسمية")
c1, c2 = st.columns(2)
fig = go.Figure()
for i, y in enumerate(pv.columns):
    fig.add_scatter(x=MNAMES, y=pv[y].values, mode="lines+markers", name=str(y), connectgaps=False,
                    line=dict(color=PALETTE[i % len(PALETTE)]))
fig.update_layout(title="الكمية الشهرية لكل سنة (الفجوات = أشهر بلا بيانات)")
fig.update_yaxes(tickformat=",")
c1.plotly_chart(fig, use_container_width=True)
pvc = pv.copy()
for (y, m) in PARTIAL:
    if y in pvc.columns:
        pvc.loc[m, y] = np.nan
pvc = pvc.loc[:, pvc.count() >= 8]  # سنوات شبه مكتملة فقط
if pvc.empty:
    c2.info("لا توجد سنوات كافية لحساب مؤشر الموسمية ضمن الفلاتر الحالية.")
else:
    idx = (pvc / pvc.mean()).mean(axis=1) * 100
    fig = px.bar(x=MNAMES, y=idx.values, labels={"x": "الشهر", "y": "مؤشر الموسمية"},
                 title=f"مؤشر الموسمية (100 = المتوسط) — سنوات: {', '.join(map(str, pvc.columns))}",
                 color_discrete_sequence=[PALETTE[0]])
    fig.add_hline(y=100, line_dash="dot")
    c2.plotly_chart(fig, use_container_width=True)

# ───────────────────────── المناطق ─────────────────────────
st.subheader("تحليل المناطق")
ar = f.groupby("Area", as_index=False).Qty.sum().sort_values("Qty", ascending=False)
ar["النسبة %"] = ar.Qty / ar.Qty.sum() * 100
c1, c2 = st.columns([3, 2])
fig = px.bar(ar, x="Qty", y="Area", orientation="h", text=ar["النسبة %"].map(lambda v: f"{v:.1f}%"),
             labels={"Qty": "الكمية", "Area": "المنطقة"}, color_discrete_sequence=[PALETTE[0]])
fig.update_yaxes(autorange="reversed")
fig.update_xaxes(tickformat=",")
c1.plotly_chart(fig, use_container_width=True)
c2.dataframe(ar.rename(columns={"Area": "المنطقة", "Qty": "الكمية"}).set_index("المنطقة")
             .style.format({"الكمية": "{:,.0f}", "النسبة %": "{:.1f}%"}), use_container_width=True)
sa = scope[scope.Area.isin(sel_a) & scope.Month.isin(ms)].groupby(["Area", "Year"]).Qty.sum().unstack(fill_value=0)
sa = sa.reindex(columns=[prev, cur], fill_value=0)
sa = sa[sa[prev] >= 20]  # تجاهل القواعد الصغيرة جداً
if sa.empty:
    st.info("لا تتوفر أشهر مشتركة كافية بين السنتين لحساب نمو المناطق.")
else:
    sa["growth"] = (sa[cur] / sa[prev] - 1) * 100
    sa["delta"] = sa[cur] - sa[prev]
    top = sa.sort_values(["growth", "delta"], ascending=False).iloc[0]
    low = sa.sort_values(["growth", "delta"]).iloc[0]
    g1, g2 = st.columns(2)
    g1.metric("الأسرع نمواً", top.name, f"{top.growth:+.1f}%")
    g2.metric("الأكثر تراجعاً", low.name, f"{low.growth:+.1f}%" if low.growth < 0 else "لا يوجد تراجع")
    st.caption(f"النمو: {cur} مقابل {prev} على الأشهر المشتركة ({len(ms)}) — مناطق كميتها ≥ 20 وحدة في {prev}")

# ───────────────────────── الأرباع ─────────────────────────
st.subheader("مقارنة الأرباع السنوية")
qt = f.groupby(["Year", "Quarter"], as_index=False).Qty.sum()
qt["الربع"], qt["السنة"] = "Q" + qt.Quarter.astype(str), qt.Year.astype(str)
fig = px.bar(qt, x="الربع", y="Qty", color="السنة", barmode="group", labels={"Qty": "الكمية"},
             category_orders={"الربع": ["Q1", "Q2", "Q3", "Q4"]}, color_discrete_sequence=PALETTE)
fig.update_yaxes(tickformat=",")
st.plotly_chart(fig, use_container_width=True)
st.caption("تنبيه: 2024 تبدأ من 15 مايو، وQ4-2026 جزئي (حتى آخر تاريخ في البيانات)، وأبريل 2026 / يوليو 2025 بلا سجلات.")

# ───────────────────────── أعلى 10 طلبات ─────────────────────────
st.subheader("أعلى 10 طلبات من حيث الكمية")
t = f.nlargest(10, "Qty").copy()
t["التاريخ"] = t.Date.dt.strftime("%Y-%m-%d")
t["المنتجات"] = t.apply(lambda r: " | ".join(f"{p}: {int(r[p]):,}" for p in PRODUCTS if r[p] > 0), axis=1)
t = t.rename(columns={"Invoice": "رقم الفاتورة", "Customer": "العميل", "Area": "المنطقة", "Qty": "الكمية"})
st.dataframe(t[["التاريخ", "رقم الفاتورة", "العميل", "المنطقة", "الكمية", "المنتجات"]]
             .style.format({"الكمية": "{:,.0f}"}), use_container_width=True, hide_index=True)

# ───────────────────────── الرؤى والتوصيات (مبنية على بيانات حتى 2026-11-11) ─────────────────────────
st.divider()
st.subheader("💡 رؤى تحليلية")
st.markdown("""
1. **أقوى وأضعف شهر:** أقوى شهر هو **مارس 2026 (547 وحدة)**، وأضعف شهر مكتمل هو **فبراير 2025 (246 وحدة)**. توجد قيم أدنى (مايو 2024: 61، مايو 2026: 116) لكنها على الأرجح غير مكتملة التسجيل (سجلات مايو 2026 من 11 إلى 24 فقط).
2. **النمط الموسمي:** فبراير الأضعف نسبةً لمتوسط السنة في 2025 و2026، وتتركز الذروة في نهاية السنة (ديسمبر 2025 = 128% من المتوسط) وفي مارس/يونيو 2026. العينة سنتان فقط، فالنمط **استرشادي**.
3. **تفوق المنتجات والمناطق:** PCMO-Min 24L الأكبر (≈40% من 2026) لكن **PCMO-Syn الأسرع نمواً (+82%)** على الأشهر المشتركة وارتفعت حصته من 15.7% إلى 28.1%، بينما تراجع Fluids 4L (−55%) وDEO 4L (−60%). جغرافياً **تبوك 53.8%** من الإجمالي ونمت +104%، والوجه +45%، في المقابل ضباء −66% والبير −97%، **وحقل والبدع بلا أي مبيعات في 2026**.
4. **شذوذ وفجوات:** لا سجلات إطلاقاً في **أبريل 2026** (مقابل 362 في أبريل 2025) ولا في **يوليو 2025** (مسجّل "Vacation" في ورقة Target)؛ وأكبر طلب في السجل **79 وحدة بتاريخ 2026-11-09** (محرك الذهبي: 30 Min 12L + 49 Syn).
5. **قفزة حجم الطلب:** متوسط الطلب ارتفع من 2.9 (2024) إلى 3.4 (2025) ثم **6.0 (2026)**، والطلبات بحجم 20 وحدة فأكثر: 2 ← 11 ← 32. نمو 2026 يأتي من طلبات أكبر مع **عدد طلبات أقل** (يناير–مارس 2026: 229 طلباً مقابل 376 في 2025).
""")
st.subheader("🎯 توصيات استراتيجية")
st.markdown("""
1. **استعادة المناطق المتراجعة (حقل، البدع، البير، ضباء):** فقدت نحو **1,069 وحدة** مقارنةً بنفس الأشهر من 2025. تحقق أولاً هل هو خلل في تسجيل المنطقة أم عملاء متوقفون، ثم ضع خطة زيارات وإعادة تنشيط لعملاء 2025 في هذه المناطق.
2. **إعادة توازن المزيج المنتجي:** عزّز PCMO-Syn وMin 12L (الأعلى نمواً) عبر عروض الكميات، واربط Fluids 4L وDEO 4L بحِزَم مع طلبات PCMO الكبيرة، وافحص هل DEO 5L (+17%) يحلّ محل DEO 4L.
3. **تخطيط موسمي وتوسيع قاعدة العملاء:** ارفع المخزون قبل ذروتي مارس وديسمبر، وأطلق حافزاً في فبراير، والتزم بجدول زيارات شهري يمنع فجوات مثل أبريل ومايو 2026؛ وبما أن النمو يعتمد على طلبات كبيرة، أضف عملاء صغاراً جدداً مع الحفاظ على الحسابات الكبرى (دار اليزيد، درة الراقي، محرك الذهبي).
""")

