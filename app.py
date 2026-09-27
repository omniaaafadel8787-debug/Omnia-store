import html
import re

import pandas as pd
import streamlit as st

# ---------------- إعدادات عامة ----------------
STORE_NAME_EN = "OmAmin Store"
STORE_NAME_AR = "أم آمن ستور"
SHEET_ID = "1ir7FX_oIRJOx-7JPOmahyYPW7hUPbLpwAxqdRrMNbFQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
PLACEHOLDER_IMG = (
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'>"
    "<rect width='400' height='400' fill='%23F6F3EE'/>"
    "<circle cx='185' cy='190' r='60' fill='%231F6F66'/>"
    "<circle cx='240' cy='232' r='32' fill='%23E8A33D' stroke='%23F6F3EE' stroke-width='8'/></svg>"
)
COLUMNS_PER_ROW = 4

st.set_page_config(page_title=STORE_NAME_EN, page_icon="🛍️", layout="wide")

# ---------------- التصميم ----------------
st.markdown(
    """
    <style>
    html, body, [class*="css"] { direction: rtl; }
    .block-container { padding-top: 1.5rem; }
    .brand { text-align:center; margin-bottom: .25rem; }
    .brand h1 { color:#163F3A; margin:0; font-size:2.2rem; }
    .brand p { color:#6B645A; margin:.25rem 0 0; }
    .card {
        background:#fff; border:1px solid #E7E1D6; border-radius:14px;
        padding:12px; display:flex; flex-direction:column;
        margin-bottom: 18px;
    }
    .card img {
        width:100%; aspect-ratio:1/1; object-fit:contain;
        background:#F6F3EE; border-radius:10px;
    }
    .card .title {
        font-weight:700; color:#163F3A; font-size:1rem; line-height:1.5;
        margin:10px 0 4px; min-height:3em;
        display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;
    }
    .card .desc {
        color:#6B645A; font-size:.85rem; line-height:1.6; flex-grow:1;
        display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;
        min-height:4.8em;
    }
    .card .tag {
        display:inline-block; font-size:.72rem; color:#1F6F66; background:#E6F2F0;
        border-radius:20px; padding:2px 10px; margin-top:6px; align-self:flex-start;
    }
    .card a.buy {
        display:block; text-align:center; text-decoration:none; font-weight:700;
        border-radius:10px; padding:9px; margin-top:10px;
    }
    .card a.amazon { background:#1F6F66; color:#fff !important; }
    .card a.noon { background:#FEEE00; color:#1a1a1a !important; }
    .card a.other { background:#E8A33D; color:#fff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- تحميل البيانات ----------------
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL, dtype=str).fillna("")
    except Exception:
        return None
    df.columns = df.columns.str.strip()
    # نخلي أسماء الأعمدة مش حساسة لحروف كبيرة وصغيرة (image / Image)
    lower = {c.lower(): c for c in df.columns}
    def col(name):
        return df[lower[name]] if name in lower else pd.Series([""] * len(df))
    out = pd.DataFrame({
        "category": col("category").str.strip(),
        "link": col("product_id").str.strip(),
        "name": col("name").str.strip(),
        "description": col("description").str.strip(),
        "image": col("image").str.strip(),
        "store": col("store").str.strip(),
    })
    out = out[out["link"] != ""]
    return out


def clean(text):
    return re.sub(r"\s+", " ", str(text)).strip()


def product_title(row):
    name, cat, desc = clean(row["name"]), clean(row["category"]), clean(row["description"])
    # لو عمود Name فاضي أو فيه اسم القسم، ناخد الاسم من الوصف
    if name and name != cat:
        return name
    if desc:
        first = re.split(r"[،,|\-–]", desc)[0].strip()
        return first if len(first) >= 12 else desc[:80]
    return cat or "منتج"


def product_link(link):
    link = link.strip()
    if link.startswith("http"):
        return link
    return f"https://www.amazon.eg/dp/{link}"


def store_of(row):
    s = (row["store"] or row["link"]).lower()
    if "noon" in s or "نون" in s:
        return "noon"
    if "amazon" in s or "amzn" in s or "أمازون" in s or not row["link"].startswith("http"):
        return "amazon"
    return "other"


BUTTON = {
    "amazon": ("amazon", "اشتري من أمازون"),
    "noon": ("noon", "اشتري من نون"),
    "other": ("other", "عرض المنتج"),
}


def card_html(row):
    title = product_title(row)
    desc = clean(row["description"])
    if desc.startswith(title):
        desc = desc[len(title):].lstrip(" ،,-–|")
    img = row["image"] if row["image"].startswith("http") else PLACEHOLDER_IMG
    cls, label = BUTTON[store_of(row)]
    return f"""
    <div class="card">
        <img src="{html.escape(img, quote=True)}" loading="lazy"
             onerror="this.onerror=null;this.src=&quot;{PLACEHOLDER_IMG}&quot;">
        <div class="title">{html.escape(title)}</div>
        <div class="desc">{html.escape(desc)}</div>
        <span class="tag">{html.escape(clean(row['category']))}</span>
        <a class="buy {cls}" href="{html.escape(product_link(row['link']), quote=True)}"
           target="_blank" rel="nofollow sponsored noopener">{label}</a>
    </div>
    """


# ---------------- الصفحة ----------------
st.markdown(
    f"""<div class="brand"><h1>🛍️ {STORE_NAME_EN}</h1>
    <p>{STORE_NAME_AR} · منتجات مختارة من أمازون ونون</p></div>""",
    unsafe_allow_html=True,
)

df = load_data()

if df is None or df.empty:
    st.warning("جاري تحميل المنتجات… لو الرسالة دي فضلت، اتأكدي إن جدول جوجل متاح لأي حد معاه اللينك.")
    st.stop()

categories = sorted(c for c in df["category"].unique() if c)

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    query = st.text_input("ابحث عن منتج", placeholder="مثلاً: سيروم، بخاخ زيت، جراب…")
with c2:
    selected_category = st.selectbox("القسم", ["كل الأقسام"] + categories)
with c3:
    selected_store = st.selectbox("المتجر", ["الكل", "أمازون", "نون"])

view = df.copy()
view["_store"] = view.apply(store_of, axis=1)
if selected_category != "كل الأقسام":
    view = view[view["category"] == selected_category]
if selected_store == "أمازون":
    view = view[view["_store"] == "amazon"]
elif selected_store == "نون":
    view = view[view["_store"] == "noon"]
if query:
    q = query.strip()
    view = view[
        view["name"].str.contains(q, case=False, regex=False)
        | view["description"].str.contains(q, case=False, regex=False)
        | view["category"].str.contains(q, case=False, regex=False)
    ]

PER_PAGE = 40
total = len(view)
pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
if pages > 1:
    p1, p2 = st.columns([1, 3])
    with p1:
        page = st.number_input("الصفحة", min_value=1, max_value=pages, value=1, step=1)
    with p2:
        st.caption(f"{total} منتج · صفحة {page} من {pages}")
else:
    page = 1
    st.caption(f"{total} منتج")

rows = view.iloc[(page - 1) * PER_PAGE: page * PER_PAGE].to_dict("records")
for start in range(0, len(rows), COLUMNS_PER_ROW):
    cols = st.columns(COLUMNS_PER_ROW)
    for col, row in zip(cols, rows[start:start + COLUMNS_PER_ROW]):
        with col:
            st.markdown(card_html(row), unsafe_allow_html=True)

st.markdown("---")
st.caption(
    f"{STORE_NAME_EN} مشارك في برامج التسويق بالعمولة، وممكن نحصل على عمولة صغيرة "
    "لما تشتري من خلال الروابط، من غير أي زيادة في السعر عليك."
)
