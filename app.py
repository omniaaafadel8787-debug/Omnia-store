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
    "<rect width='400' height='400' fill='%23FFF1E5'/>"
    "<circle cx='200' cy='200' r='70' fill='%23161616'/>"
    "<text x='200' y='222' font-family='Georgia,serif' font-size='60' fill='%23FFB26B' "
    "text-anchor='middle'>OA</text></svg>"
)
COLUMNS_PER_ROW = 4
PER_PAGE = 40

# ألوان التصميم (برتقالي وأبيض وأسود)
PLUM = "#161616"
PLUM_MID = "#F07A1A"
PLUM_DARK = "#111111"
GOLD = "#F07A1A"
GOLD_LIGHT = "#FFB26B"
INK = "#1A1A1A"
MUTED = "#6B6B6B"
BG = "#FAFAFA"

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
  background:#fff; border:1px solid #EBEBEB; border-radius:22px; padding:14px 22px; margin-bottom:18px; }}
.om-logo {{ display:flex; align-items:center; gap:10px; direction:ltr; }}
.om-stamp {{ width:46px; height:46px; border-radius:50%; background:{PLUM}; display:flex; align-items:center;
  justify-content:center; font-family:Marcellus,serif !important; font-size:19px; color:{GOLD_LIGHT};
  box-shadow: inset 0 0 0 3px {PLUM}, inset 0 0 0 4px {GOLD}; }}
.om-name {{ display:flex; flex-direction:column; line-height:1.05; }}
.om-name b {{ font-family:Marcellus,serif !important; font-weight:400; font-size:28px; color:{PLUM}; }}
.om-name small {{ font-family:Jost,sans-serif !important; font-weight:500; font-size:10px; letter-spacing:.4em; color:{GOLD}; }}
.om-top .om-ar {{ color:{MUTED}; font-size:14px; }}
.om-hero {{ position:relative; overflow:hidden; border-radius:28px; background:{PLUM}; color:#FFFFFF;
  padding:44px 48px; margin-bottom:22px; }}
.om-hero .ring {{ position:absolute; left:-80px; top:-80px; width:260px; height:260px; border-radius:50%;
  border:40px solid rgba(240,122,26,.28); }}
.om-hero .dot {{ position:absolute; left:120px; bottom:-50px; width:110px; height:110px; border-radius:50%; background:{GOLD}; }}
.om-hero .kicker {{ position:relative; font-size:14px; font-weight:600; color:{GOLD_LIGHT}; }}
.om-hero h1 {{ position:relative; margin:8px 0 10px; font-family:Cairo,sans-serif !important; font-weight:800;
  font-size:44px; line-height:1.3; color:#FFFFFF; padding:0; }}
.om-hero p {{ position:relative; margin:0; font-size:17px; line-height:1.8; color:#D6D6D6; max-width:520px; }}
.om-stats {{ position:relative; display:flex; gap:12px; margin-top:22px; flex-wrap:wrap; }}
.om-stats span {{ background:rgba(255,255,255,.1); border:1px solid rgba(255,178,107,.45); color:#FFFFFF;
  border-radius:14px; padding:8px 16px; font-size:14px; }}
.om-stats span b {{ font-family:Cairo,sans-serif !important; color:{GOLD_LIGHT}; font-size:18px; margin-left:4px; }}
.om-h2 {{ font-family:Cairo,sans-serif !important; font-weight:700; font-size:26px; color:{INK}; margin:6px 0 2px; }}
.card {{ background:#fff; border-radius:22px; padding:14px; display:flex; flex-direction:column; gap:8px;
  margin-bottom:20px; box-shadow:0 1px 0 #EBEBEB; transition:transform .15s, box-shadow .15s; }}
.card:hover {{ transform:translateY(-3px); box-shadow:0 10px 24px rgba(240,122,26,.18); }}
.card .ph {{ position:relative; border-radius:16px; background:#fff; border:1px solid #EEEEEE; overflow:hidden; }}
.card .ph img {{ width:100%; aspect-ratio:1/1; object-fit:contain; display:block; }}
.card .badge {{ position:absolute; top:10px; right:10px; font-size:12px; font-weight:700; padding:3px 10px;
  border-radius:999px; background:{BG}; color:{INK}; }}
.card .badge.noon {{ background:#FEEE00; color:#1a1a1a; }}
.card .title {{ font-weight:600; font-size:16px; line-height:1.55; color:{INK}; min-height:3.1em;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }}
.card .desc {{ color:{MUTED}; font-size:13px; line-height:1.7; min-height:3.4em;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }}
.card .tag {{ align-self:flex-start; font-size:12px; color:{PLUM_MID}; background:#FFF1E5; border-radius:999px; padding:2px 10px; }}
.card a.buy {{ display:block; text-align:center; text-decoration:none; font-weight:600; font-size:14px;
  background:{PLUM_MID}; color:#fff !important; border-radius:12px; padding:11px; margin-top:4px; }}
.card a.buy:hover {{ background:#D9640A; }}
.om-foot {{ margin-top:36px; background:{PLUM_DARK}; color:#D6D6D6; border-radius:24px; padding:30px 36px;
  display:flex; justify-content:space-between; align-items:flex-start; gap:30px; flex-wrap:wrap; }}
.om-foot b {{ font-family:Marcellus,serif !important; font-weight:400; font-size:24px; color:#FFFFFF; }}
.om-foot p {{ margin:8px 0 0; font-size:14px; line-height:1.8; max-width:620px; color:#D6D6D6; }}
.stTextInput input, .stNumberInput input {{ border-radius:12px !important; }}
div[data-baseweb="select"] > div {{ border-radius:12px !important; }}
.om-bag {{ display:block; filter: drop-shadow(0 2px 3px rgba(0,0,0,.18)); }}
.om-hero {{ display:grid; grid-template-columns: minmax(0,1fr) minmax(0,1.2fr); gap:24px; align-items:center; }}
.om-hero-text {{ position:relative; z-index:1; }}
.om-hero-pics {{ position:relative; z-index:1; height:300px; display:grid; grid-template-columns:1fr 1fr; gap:12px;
  overflow:hidden; border-radius:20px;
  -webkit-mask-image: linear-gradient(to bottom, transparent, #000 14%, #000 86%, transparent);
  mask-image: linear-gradient(to bottom, transparent, #000 14%, #000 86%, transparent); }}
.om-strip {{ overflow:hidden; }}
.om-track {{ display:flex; flex-direction:column; gap:12px; animation: omUp 38s linear infinite; }}
.om-track.rev {{ animation-name: omDown; animation-duration: 44s; }}
.om-hero-pics:hover .om-track {{ animation-play-state: paused; }}
.om-track img {{ width:100%; aspect-ratio:1/1; object-fit:contain; background:#fff; border-radius:16px; padding:8px;
  box-sizing:border-box; box-shadow:0 6px 16px rgba(0,0,0,.18); }}
@keyframes omUp {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-50%); }} }}
@keyframes omDown {{ from {{ transform: translateY(-50%); }} to {{ transform: translateY(0); }} }}
@media (prefers-reduced-motion: reduce) {{ .om-track {{ animation: none; }} }}
/* أزرار المتجر وأرقام الصفحات */
[data-testid="stButtonGroup"] button {{
  border-radius:12px !important; border:1px solid #EBEBEB !important; background:#fff !important; color:{INK} !important;
  font-weight:600 !important; min-height:42px; padding:0 18px !important; }}
[data-testid="stButtonGroup"] button[aria-checked="true"] {{
  border-radius:12px !important; background:{PLUM_MID} !important; border-color:{PLUM_MID} !important;
  color:#fff !important; font-weight:700 !important; min-height:42px; padding:0 18px !important; }}
[data-testid="stButtonGroup"] button[data-variant="pills"] {{ min-width:44px; padding:0 12px !important; }}
@media (max-width: 700px) {{
  .om-hero {{ padding:30px 24px; }} .om-hero h1 {{ font-size:30px; }}
  .om-top .om-ar {{ display:none; }}
  .om-hero {{ grid-template-columns: 1fr; }}
  .om-hero-pics {{ height:190px; }}
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
# لوجو: شنطة تسوق وجواها قلب (تسوق باهتمام أم)
LOGO_SVG = (
    '<svg class="om-bag" width="44" height="50" viewBox="0 0 92 104" aria-hidden="true">'
    '<path d="M30 32V24a16 16 0 0 1 32 0v8" stroke="#F07A1A" stroke-width="7" stroke-linecap="round" fill="none"/>'
    '<rect x="8" y="30" width="76" height="68" rx="18" fill="#161616"/>'
    '<path d="M46 84c-10-7-17-12.5-17-20.5a9 9 0 0 1 17-4.2 9 9 0 0 1 17 4.2c0 8-7 13.5-17 20.5z" fill="#F07A1A"/>'
    '<circle cx="31" cy="44" r="3.2" fill="#FFB26B"/><circle cx="61" cy="44" r="3.2" fill="#FFB26B"/>'
    "</svg>"
)

st.markdown(
    '<div class="om-top">'
    f'<div class="om-logo">{LOGO_SVG}'
    '<span class="om-name"><b>OmAmin</b><small>STORE</small></span></div>'
    f'<span class="om-ar">{STORE_NAME_AR} · منتجات مختارة بحب من أمازون ونون</span>'
    "</div>",
    unsafe_allow_html=True,
)

df = load_data()

if df is None or df.empty:
    st.warning("جاري تحميل المنتجات… لو الرسالة دي فضلت، اتأكدي إن جدول جوجل متاح لأي حد معاه اللينك.")
    st.stop()

categories = sorted(c for c in df["category"].unique() if c)


def hero_strip(frame, n=10, seed=0):
    """شريط صور منتجات بيتحرك لوحده جوه البانر"""
    pics = frame[frame["image"].str.startswith("http")]
    if pics.empty:
        return ""
    pics = pics.sample(min(n, len(pics)), random_state=seed)
    imgs = "".join(
        f'<img src="{html.escape(u, quote=True)}" alt="">' for u in pics["image"]
    )
    # بنكرر الصور مرتين عشان الحركة تبان متصلة من غير قطع
    return f'<div class="om-strip"><div class="om-track">{imgs}{imgs}</div></div>'


day_seed = pd.Timestamp.now().dayofyear
strips = hero_strip(df, 10, day_seed) + hero_strip(df, 10, day_seed + 7).replace(
    'class="om-track"', 'class="om-track rev"'
)

st.markdown(
    '<div class="om-hero"><div class="ring"></div><div class="dot"></div>'
    f'<div class="om-hero-pics">{strips}</div>'
    '<div class="om-hero-text">'
    '<div class="kicker">اختيارات مجربة من أمازون ونون</div>'
    "<h1>كل اللي بيتك محتاجه،<br>متنقي بعناية</h1>"
    "<p>بندور لك على أحسن المنتجات، وإنتي تشتري بثقة من المتجر الأصلي.</p>"
    '<div class="om-stats">'
    f"<span><b>{len(df)}</b>منتج</span>"
    f"<span><b>{len(categories)}</b>قسم</span>"
    "<span>أمازون ونون</span>"
    "</div></div>"
    "</div>",
    unsafe_allow_html=True,
)

# ---------------- البحث والفلاتر ----------------
STORE_OPTIONS = ["كل المتاجر", "أمازون", "نون"]
if "page" not in st.session_state:
    st.session_state.page = 1


def reset_page():
    st.session_state.page = 1


c1, c2 = st.columns([2, 1])
with c1:
    query = st.text_input(
        "ابحثي عن منتج", placeholder="بتدوري على إيه؟ مثلاً: سيروم، بخاخ زيت، شنطة…",
        on_change=reset_page,
    )
with c2:
    selected_category = st.selectbox("القسم", ["كل الأقسام"] + categories, on_change=reset_page)

# أزرار المتجر: كل المتاجر / أمازون / نون
if hasattr(st, "segmented_control"):
    selected_store = st.segmented_control(
        "المتجر", STORE_OPTIONS, default="كل المتاجر", key="store_btn", on_change=reset_page
    ) or "كل المتاجر"
else:
    selected_store = st.radio("المتجر", STORE_OPTIONS, horizontal=True, on_change=reset_page)

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

total = len(view)
pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
st.session_state.page = min(max(1, st.session_state.page), pages)


def page_window(cur, last):
    """أرقام الصفحات اللي بتظهر: الأولى والأخيرة وحوالين الصفحة الحالية"""
    nums = {1, last} | set(range(max(1, cur - 2), min(last, cur + 2) + 1))
    return sorted(nums)


def go_to_page(key):
    val = st.session_state.get(key)
    if val:
        st.session_state.page = int(val)


def pager(key):
    if pages <= 1:
        return
    cur = st.session_state.page
    options = [str(n) for n in page_window(cur, pages)]
    st.session_state[key] = str(cur)
    if hasattr(st, "pills"):
        st.pills(
            "الصفحات", options, key=key, on_change=go_to_page, args=(key,),
            label_visibility="collapsed",
        )
    else:
        st.number_input("الصفحة", 1, pages, key="pg_num_" + key,
                        value=cur, on_change=lambda: st.session_state.update(page=st.session_state["pg_num_" + key]))


heading = selected_category if selected_category != "كل الأقسام" else "كل المنتجات"
st.markdown(f'<div class="om-h2">{html.escape(heading)}</div>', unsafe_allow_html=True)
page = st.session_state.page
st.caption(f"{total} منتج · صفحة {page} من {pages}" if pages > 1 else f"{total} منتج")
pager("pg_top")

if total == 0:
    st.info("مفيش منتجات بالبحث ده. جربي كلمة تانية أو قسم تاني.")

rows = view.iloc[(page - 1) * PER_PAGE: page * PER_PAGE].to_dict("records")
for start in range(0, len(rows), COLUMNS_PER_ROW):
    cols = st.columns(COLUMNS_PER_ROW)
    for col, row in zip(cols, rows[start:start + COLUMNS_PER_ROW]):
        with col:
            st.markdown(card_html(row), unsafe_allow_html=True)

if pages > 1:
    st.caption(f"صفحة {page} من {pages}")
    pager("pg_bottom")

st.markdown(
    '<div class="om-foot"><div><b>OmAmin Store</b>'
    f"<p>{STORE_NAME_EN} مشارك في برامج التسويق بالعمولة. بعض الروابط في الموقع روابط عمولة، "
    "ولما تشتري من خلالها بناخد نسبة صغيرة من المتجر، من غير أي زيادة في السعر عليكي.</p></div>"
    f'<div class="om-ar" style="color:{GOLD_LIGHT}">{STORE_NAME_AR} · بحب ❤</div></div>',
    unsafe_allow_html=True,
)
