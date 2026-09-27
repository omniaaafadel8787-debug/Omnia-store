import html
import re

import pandas as pd
import streamlit as st

# ---------------- إعدادات عامة ----------------
STORE_NAME_EN = "OmAmin Store"
STORE_NAME_AR = "أم آمن ستور"
SHEET_ID = "1ir7FX_oIRJOx-7JPOmahyYPW7hUPbLpwAxqdRrMNbFQ"
SHEET_URL = "https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/export?format=csv&gid={gid}"
# كل تاب في الشيت: (رقم التاب gid, المتجر)
SHEET_TABS = [("0", "amazon"), ("1225262452", "noon")]
PLACEHOLDER_IMG = (
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'>"
    "<rect width='400' height='400' fill='%23F3EAF3'/>"
    "<circle cx='200' cy='200' r='70' fill='%234A2A55'/>"
    "<text x='200' y='222' font-family='Georgia,serif' font-size='60' fill='%23E9C9A8' "
    "text-anchor='middle'>OA</text></svg>"
)
COLUMNS_PER_ROW = 4
PER_PAGE = 40

# ألوان التصميم (بنفسجي برقوقي وذهبي وردي)
PLUM = "#4A2A55"
PLUM_MID = "#6E4478"
PLUM_DARK = "#3A2143"
GOLD = "#B8875C"
GOLD_LIGHT = "#E9C9A8"
INK = "#2A2230"
MUTED = "#71667A"
BG = "#F5F1F3"

st.set_page_config(page_title=STORE_NAME_EN, page_icon="🛍️", layout="wide")

# ---------------- التصميم ----------------
st.markdown(
    f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Marcellus&family=Jost:wght@500&family=Cairo:wght@600;700;800&family=IBM+Plex+Sans+Arabic:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp {{ direction: rtl; }}
.stApp {{ background: {BG}; color: {INK}; font-family: 'IBM Plex Sans Arabic', Tahoma, sans-serif; }}
.stApp p, .stApp label, .stApp input, .stApp span, .stApp div {{ font-family: 'IBM Plex Sans Arabic', Tahoma, sans-serif; }}
#MainMenu, footer, [data-testid="stHeader"] {{ visibility: hidden; }}
.block-container {{ padding-top: 1.2rem; max-width: 1320px; }}
.om-top {{ display:flex; align-items:center; justify-content:space-between; gap:16px;
  background:#fff; border:1px solid #E6DDE4; border-radius:22px; padding:14px 22px; margin-bottom:18px; }}
.om-logo {{ display:flex; align-items:center; gap:10px; direction:ltr; }}
.om-stamp {{ width:46px; height:46px; border-radius:50%; background:{PLUM}; display:flex; align-items:center;
  justify-content:center; font-family:Marcellus,serif !important; font-size:19px; color:{GOLD_LIGHT};
  box-shadow: inset 0 0 0 3px {PLUM}, inset 0 0 0 4px {GOLD}; }}
.om-name {{ display:flex; flex-direction:column; line-height:1.05; }}
.om-name b {{ font-family:Marcellus,serif !important; font-weight:400; font-size:28px; color:{PLUM}; }}
.om-name small {{ font-family:Jost,sans-serif !important; font-weight:500; font-size:10px; letter-spacing:.4em; color:{GOLD}; }}
.om-top .om-ar {{ color:{MUTED}; font-size:14px; }}
.om-hero {{ position:relative; overflow:hidden; border-radius:28px; background:{PLUM}; color:#FBF6F9;
  padding:44px 48px; margin-bottom:22px; }}
.om-hero .ring {{ position:absolute; left:-80px; top:-80px; width:260px; height:260px; border-radius:50%;
  border:40px solid {PLUM_MID}; }}
.om-hero .dot {{ position:absolute; left:120px; bottom:-50px; width:110px; height:110px; border-radius:50%; background:{GOLD}; }}
.om-hero .kicker {{ position:relative; font-size:14px; font-weight:600; color:{GOLD_LIGHT}; }}
.om-hero h1 {{ position:relative; margin:8px 0 10px; font-family:Cairo,sans-serif !important; font-weight:800;
  font-size:44px; line-height:1.3; color:#FBF6F9; padding:0; }}
.om-hero p {{ position:relative; margin:0; font-size:17px; line-height:1.8; color:#E4D2DF; max-width:520px; }}
.om-stats {{ position:relative; display:flex; gap:12px; margin-top:22px; flex-wrap:wrap; }}
.om-stats span {{ background:rgba(255,255,255,.1); border:1px solid rgba(233,201,168,.35); color:#FBF6F9;
  border-radius:14px; padding:8px 16px; font-size:14px; }}
.om-stats span b {{ font-family:Cairo,sans-serif !important; color:{GOLD_LIGHT}; font-size:18px; margin-left:4px; }}
.om-h2 {{ font-family:Cairo,sans-serif !important; font-weight:700; font-size:26px; color:{INK}; margin:6px 0 2px; }}
.card {{ background:#fff; border-radius:22px; padding:14px; display:flex; flex-direction:column; gap:8px;
  margin-bottom:20px; box-shadow:0 1px 0 #E6DDE4; transition:transform .15s, box-shadow .15s; }}
.card:hover {{ transform:translateY(-3px); box-shadow:0 10px 24px rgba(74,42,85,.10); }}
.card .ph {{ position:relative; border-radius:16px; background:#fff; border:1px solid #F0E8EE; overflow:hidden; }}
.card .ph img {{ width:100%; aspect-ratio:1/1; object-fit:contain; display:block; }}
.card .badge {{ position:absolute; top:10px; right:10px; font-size:12px; font-weight:700; padding:3px 10px;
  border-radius:999px; background:{BG}; color:{INK}; }}
.card .badge.noon {{ background:#FEEE00; color:#1a1a1a; }}
.card .title {{ font-weight:600; font-size:16px; line-height:1.55; color:{INK}; min-height:3.1em;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }}
.card .desc {{ color:{MUTED}; font-size:13px; line-height:1.7; min-height:3.4em;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }}
.card .tag {{ align-self:flex-start; font-size:12px; color:{PLUM_MID}; background:#F3EAF3; border-radius:999px; padding:2px 10px; }}
.card a.buy {{ display:block; text-align:center; text-decoration:none; font-weight:600; font-size:14px;
  background:{PLUM_MID}; color:#fff !important; border-radius:12px; padding:11px; margin-top:4px; }}
.card a.buy:hover {{ background:{PLUM}; }}
.om-foot {{ margin-top:36px; background:{PLUM_DARK}; color:#E4D2DF; border-radius:24px; padding:30px 36px;
  display:flex; justify-content:space-between; align-items:flex-start; gap:30px; flex-wrap:wrap; }}
.om-foot b {{ font-family:Marcellus,serif !important; font-weight:400; font-size:24px; color:#FBF6F9; }}
.om-foot p {{ margin:8px 0 0; font-size:14px; line-height:1.8; max-width:620px; color:#E4D2DF; }}
.stTextInput input, .stNumberInput input {{ border-radius:12px !important; }}
div[data-baseweb="select"] > div {{ border-radius:12px !important; }}
@media (max-width: 700px) {{
  .om-hero {{ padding:30px 24px; }} .om-hero h1 {{ font-size:30px; }}
  .om-top .om-ar {{ display:none; }}
}}
</style>""",
    unsafe_allow_html=True,
)


# ---------------- تحميل البيانات ----------------
def load_tab(gid, default_store):
    try:
        df = pd.read_csv(SHEET_URL.format(gid=gid), dtype=str).fillna("")
    except Exception:
        return None
    df.columns = df.columns.str.strip()
    # نخلي أسماء الأعمدة مش حساسة لحروف كبيرة وصغيرة (image / Image)
    lower = {c.lower(): c for c in df.columns}

    def col(name):
        return df[lower[name]] if name in lower else pd.Series([""] * len(df), index=df.index)

    out = pd.DataFrame({
        "category": col("category").str.strip(),
        "link": col("product_id").str.strip(),
        "name": col("name").str.strip(),
        "description": col("description").str.strip(),
        "image": col("image").str.strip(),
        "store": col("store").str.strip(),
    })
    out.loc[out["store"] == "", "store"] = default_store
    return out[out["link"] != ""]


@st.cache_data(ttl=60)
def load_data():
    parts = [load_tab(gid, store) for gid, store in SHEET_TABS]
    parts = [p for p in parts if p is not None and not p.empty]
    if not parts:
        return None
    return pd.concat(parts, ignore_index=True)


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


STORE_LABEL = {
    "amazon": ("أمازون", "اشتري من أمازون"),
    "noon": ("نون", "اشتري من نون"),
    "other": ("متجر", "عرض المنتج"),
}


def card_html(row):
    title = product_title(row)
    desc = clean(row["description"])
    if desc.startswith(title):
        desc = desc[len(title):].lstrip(" ،,-–|")
    img = row["image"] if row["image"].startswith("http") else PLACEHOLDER_IMG
    store = store_of(row)
    badge, label = STORE_LABEL[store]
    return (
        '<div class="card">'
        '<div class="ph">'
        f'<span class="badge {store}">{badge}</span>'
        f'<img src="{html.escape(img, quote=True)}" loading="lazy" alt="{html.escape(title, quote=True)}" '
        f'onerror="this.onerror=null;this.src=&quot;{PLACEHOLDER_IMG}&quot;">'
        "</div>"
        f'<div class="title">{html.escape(title)}</div>'
        f'<div class="desc">{html.escape(desc)}</div>'
        f'<span class="tag">{html.escape(clean(row["category"]))}</span>'
        f'<a class="buy" href="{html.escape(product_link(row["link"]), quote=True)}" '
        f'target="_blank" rel="nofollow sponsored noopener">{label}</a>'
        "</div>"
    )


# ---------------- الصفحة ----------------
st.markdown(
    '<div class="om-top">'
    '<div class="om-logo"><span class="om-stamp">OA</span>'
    '<span class="om-name"><b>OmAmin</b><small>STORE</small></span></div>'
    f'<span class="om-ar">{STORE_NAME_AR} · منتجات مختارة من أمازون ونون</span>'
    "</div>",
    unsafe_allow_html=True,
)

df = load_data()

if df is None or df.empty:
    st.warning("جاري تحميل المنتجات… لو الرسالة دي فضلت، اتأكدي إن جدول جوجل متاح لأي حد معاه اللينك.")
    st.stop()

categories = sorted(c for c in df["category"].unique() if c)

st.markdown(
    '<div class="om-hero"><div class="ring"></div><div class="dot"></div>'
    '<div class="kicker">اختيارات مجربة من أمازون ونون</div>'
    "<h1>كل اللي بيتك محتاجه،<br>متنقي بعناية</h1>"
    "<p>بندور لك على أحسن المنتجات، وإنتي تشتري بثقة من المتجر الأصلي.</p>"
    '<div class="om-stats">'
    f"<span><b>{len(df)}</b>منتج</span>"
    f"<span><b>{len(categories)}</b>قسم</span>"
    "<span>أمازون ونون</span>"
    "</div></div>",
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    query = st.text_input("ابحثي عن منتج", placeholder="بتدوري على إيه؟ مثلاً: سيروم، بخاخ زيت، شنطة…")
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

heading = selected_category if selected_category != "كل الأقسام" else "كل المنتجات"
st.markdown(f'<div class="om-h2">{html.escape(heading)}</div>', unsafe_allow_html=True)

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

if total == 0:
    st.info("مفيش منتجات بالبحث ده. جربي كلمة تانية أو قسم تاني.")

rows = view.iloc[(page - 1) * PER_PAGE: page * PER_PAGE].to_dict("records")
for start in range(0, len(rows), COLUMNS_PER_ROW):
    cols = st.columns(COLUMNS_PER_ROW)
    for col, row in zip(cols, rows[start:start + COLUMNS_PER_ROW]):
        with col:
            st.markdown(card_html(row), unsafe_allow_html=True)

st.markdown(
    '<div class="om-foot"><div><b>OmAmin Store</b>'
    f"<p>{STORE_NAME_EN} مشارك في برامج التسويق بالعمولة. بعض الروابط في الموقع روابط عمولة، "
    "ولما تشتري من خلالها بناخد نسبة صغيرة من المتجر، من غير أي زيادة في السعر عليكي.</p></div>"
    f'<div class="om-ar" style="color:{GOLD_LIGHT}">{STORE_NAME_AR}</div></div>',
    unsafe_allow_html=True,
)
