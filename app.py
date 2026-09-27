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
    "<rect width='400' height='400' fill='%23FFF5EC'/>"
    "<circle cx='200' cy='200' r='70' fill='%23EE8433'/>"
    "<text x='200' y='222' font-family='Georgia,serif' font-size='60' fill='%23FFFFFF' "
    "text-anchor='middle'>OA</text></svg>"
)
COLUMNS_PER_ROW = 4
PER_PAGE = 40

# ألوان التصميم (برتقالي وأبيض ولمسة أسود)
ORANGE = "#EE8433"
ORANGE_DARK = "#D46F22"
ORANGE_SOFT = "#FFF5EC"
INK = "#1A1A1A"
MUTED = "#6B6B6B"
BG = "#FFFFFF"
LINE = "#EFE7E0"
EDGE = "#3A3A3A"  # لون التحديد: رمادي غامق

st.set_page_config(page_title=STORE_NAME_EN, page_icon="🛍️", layout="wide")

# ---------------- اللغات ----------------
LANGS = {"عربي": "ar", "English": "en", "Italiano": "it"}
T = {
    "ar": {
        "tagline": "منتجات مختارة بحب من أمازون ونون",
        "kicker": "اختيارات مجربة من أمازون ونون",
        "hero": "كل اللي بيتك محتاجه،<br>متنقي بعناية",
        "hero_p": "بندور لك على أحسن المنتجات، وإنتي تشتري بثقة من المتجر الأصلي.",
        "products": "منتج", "cats": "قسم", "both": "أمازون ونون",
        "search": "ابحثي عن منتج", "search_ph": "بتدوري على إيه؟ مثلاً: سيروم، بخاخ زيت، شنطة…",
        "category": "القسم", "all_cats": "كل الأقسام", "store": "المتجر",
        "all_stores": "كل المتاجر", "amazon": "أمازون", "noon": "نون", "other": "متجر",
        "all_products": "كل المنتجات", "page": "صفحة", "of": "من",
        "buy_amazon": "اشتري من أمازون", "buy_noon": "اشتري من نون", "buy_other": "عرض المنتج",
        "none": "مفيش منتجات بالبحث ده. جربي كلمة تانية أو قسم تاني.",
        "loading": "جاري تحميل المنتجات… لو الرسالة دي فضلت، اتأكدي إن جدول جوجل متاح لأي حد معاه اللينك.",
        "footer": f"{STORE_NAME_EN} مشارك في برامج التسويق بالعمولة. بعض الروابط في الموقع روابط عمولة، "
                  "ولما تشتري من خلالها بناخد نسبة صغيرة من المتجر، من غير أي زيادة في السعر عليكي.",
        "love": "بحب ❤",
        "sec_amazon": "منتجات أمازون", "sec_noon": "منتجات نون", "sec_other": "منتجات أخرى",
    },
    "en": {
        "tagline": "Products picked with love from Amazon & Noon",
        "kicker": "Tried-and-loved picks from Amazon & Noon",
        "hero": "Everything your home needs,<br>carefully chosen",
        "hero_p": "We search for the best products for you, so you can buy with confidence from the original store.",
        "products": "products", "cats": "categories", "both": "Amazon & Noon",
        "search": "Search for a product", "search_ph": "What are you looking for? e.g. serum, oil sprayer, bag…",
        "category": "Category", "all_cats": "All categories", "store": "Store",
        "all_stores": "All stores", "amazon": "Amazon", "noon": "Noon", "other": "Store",
        "all_products": "All products", "page": "Page", "of": "of",
        "buy_amazon": "Buy on Amazon", "buy_noon": "Buy on Noon", "buy_other": "View product",
        "none": "No products match your search. Try another word or category.",
        "loading": "Loading products…",
        "footer": f"{STORE_NAME_EN} participates in affiliate programs. Some links on this site are affiliate links: "
                  "when you buy through them we earn a small commission, at no extra cost to you.",
        "love": "with love ❤",
        "sec_amazon": "Amazon products", "sec_noon": "Noon products", "sec_other": "Other products",
    },
    "it": {
        "tagline": "Prodotti scelti con amore da Amazon e Noon",
        "kicker": "Scelte provate e amate da Amazon e Noon",
        "hero": "Tutto ciò che serve alla tua casa,<br>scelto con cura",
        "hero_p": "Cerchiamo per te i prodotti migliori, così puoi acquistare con fiducia dal negozio originale.",
        "products": "prodotti", "cats": "categorie", "both": "Amazon e Noon",
        "search": "Cerca un prodotto", "search_ph": "Cosa stai cercando? es. siero, spruzzino olio, borsa…",
        "category": "Categoria", "all_cats": "Tutte le categorie", "store": "Negozio",
        "all_stores": "Tutti i negozi", "amazon": "Amazon", "noon": "Noon", "other": "Negozio",
        "all_products": "Tutti i prodotti", "page": "Pagina", "of": "di",
        "buy_amazon": "Acquista su Amazon", "buy_noon": "Acquista su Noon", "buy_other": "Vedi prodotto",
        "none": "Nessun prodotto trovato. Prova un'altra parola o categoria.",
        "loading": "Caricamento dei prodotti…",
        "footer": f"{STORE_NAME_EN} partecipa a programmi di affiliazione. Alcuni link del sito sono link di affiliazione: "
                  "se acquisti tramite essi riceviamo una piccola commissione, senza costi aggiuntivi per te.",
        "love": "con amore ❤",
        "sec_amazon": "Prodotti Amazon", "sec_noon": "Prodotti Noon", "sec_other": "Altri prodotti",
    },
}

# ترجمة أسماء الأقسام (عربي: [إنجليزي, إيطالي])
CAT_TR = {
    "مستلزمات مطبخ": ["Kitchen essentials", "Accessori da cucina"],
    "مستلزمات الحمام": ["Bathroom essentials", "Accessori per il bagno"],
    "ادوات منزليه مساحات وفرش وغيره": ["Cleaning tools", "Attrezzi per la pulizia"],
    "مستلزمات منزليه وشخصيه لتسهيل الحياه اليوميه": ["Home & everyday helpers", "Casa e vita quotidiana"],
    "العنايه بالبشره": ["Skin care", "Cura della pelle"],
    "اكسسوار تليفون": ["Phone accessories", "Accessori per telefono"],
    "اكسسوار حريمي": ["Women's accessories", "Accessori donna"],
    "لانجيري": ["Lingerie", "Lingerie"],
    "تراننج حريمي ورجالي": ["Tracksuits", "Tute sportive"],
    "اسكرفات": ["Scarves", "Sciarpe"],
    "اجهزه الكترونيه": ["Electronics", "Elettronica"],
    "اثاث": ["Furniture", "Mobili"],
    "أمان": ["Safety & security", "Sicurezza"],
    "ادوات مكتبيه": ["Stationery", "Cancelleria"],
    "مفروشات": ["Bedding", "Biancheria per la casa"],
    "سفر": ["Travel", "Viaggio"],
    "مستلزمات حريمي": ["Women's essentials", "Essenziali donna"],
    "شنط حريمي": ["Women's bags", "Borse donna"],
    "مستلزمات اطفال": ["Baby & kids", "Neonati e bambini"],
    "مكياج": ["Makeup", "Trucco"],
    "العنايه بالشعر": ["Hair care", "Cura dei capelli"],
    "سماعات": ["Headphones", "Cuffie"],
    "العنايه بالاحذيه والشنط": ["Shoe & bag care", "Cura di scarpe e borse"],
    "ديكور المنزل": ["Home decor", "Decorazioni per la casa"],
    "اجهزه منزليه": ["Home appliances", "Elettrodomestici"],
    "عطور": ["Fragrances", "Profumi"],
    "العنايه بالجسم": ["Body care", "Cura del corpo"],
    "ساعات ذكيه": ["Smartwatches", "Smartwatch"],
    "ملابس حريمي": ["Women's clothing", "Abbigliamento donna"],
    "العاب اطفال": ["Kids' toys", "Giocattoli"],
    "رياضه": ["Sports", "Sport"],
    "كتب تلوين وأنشطة": ["Coloring & activity books", "Libri da colorare e attività"],
    "قصص اطفال": ["Children's stories", "Storie per bambini"],
    "العاب تعليمية": ["Educational toys", "Giochi educativi"],
    "رسم وأشغال يدوية": ["Arts & crafts", "Arte e bricolage"],
    "مستلزمات الحيوانات الأليفة": ["Pet supplies", "Articoli per animali"],
    "منظفات ومناديل": ["Cleaning & tissues", "Detersivi e fazzoletti"],
    "اكسسوارات السيارات": ["Car accessories", "Accessori auto"],
    "ادوات وتحسين المنزل": ["Home improvement", "Fai da te"],
    "حديقه": ["Garden", "Giardino"],
    "موبايلات": ["Mobile phones", "Cellulari"],
    "ملابس رجالي": ["Men's clothing", "Abbigliamento uomo"],
    "مفروشات وحمام": ["Bed & bath", "Letto e bagno"],
    "عنايه شخصيه": ["Personal care", "Cura personale"],
    "ساعات حريمي": ["Women's watches", "Orologi donna"],
    "ملابس اطفال": ["Kids' clothing", "Abbigliamento bambini"],
}

if "lang" not in st.session_state:
    st.session_state.lang = "ar"
lang_choice = st.segmented_control(
    "Language", list(LANGS), default="عربي", key="lang_btn", label_visibility="collapsed"
) if hasattr(st, "segmented_control") else st.radio("Language", list(LANGS), horizontal=True)
LANG = LANGS.get(lang_choice or "عربي", "ar")
TX = T[LANG]
DIR = "rtl" if LANG == "ar" else "ltr"


def cat_name(cat):
    if LANG == "ar":
        return cat
    tr = CAT_TR.get(cat)
    return tr[0 if LANG == "en" else 1] if tr else cat


# ---------------- التصميم ----------------
st.markdown(
    f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Marcellus&family=Jost:wght@500&family=Cairo:wght@600;700;800&family=IBM+Plex+Sans+Arabic:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp {{ direction: {DIR}; }}
.stApp {{ background: {BG}; color: {INK}; font-family: 'IBM Plex Sans Arabic', Tahoma, sans-serif; }}
.stApp p, .stApp label, .stApp input, .stApp span, .stApp div {{ font-family: 'IBM Plex Sans Arabic', Tahoma, sans-serif; }}
#MainMenu, footer, [data-testid="stHeader"] {{ visibility: hidden; }}
.block-container {{ padding-top: 1.2rem; max-width: 1320px; }}
[data-testid="stMainBlockContainer"], .block-container {{ border:2px solid {EDGE}; border-radius:28px; margin-top:14px; margin-bottom:14px; }}
.om-top {{ display:flex; align-items:center; justify-content:space-between; gap:16px;
  background:#fff; border:1.5px solid {EDGE}; border-radius:22px; padding:14px 22px; margin-bottom:18px;
  box-shadow:0 2px 10px rgba(238,132,51,.08); }}
.om-logo {{ display:flex; align-items:center; gap:10px; direction:ltr; }}
.om-bag {{ display:block; filter: drop-shadow(0 3px 5px rgba(238,132,51,.30)); }}
.om-name {{ position:relative; display:flex; flex-direction:column; line-height:1.05; padding:0 6px; }}
.om-name b, .om-name small {{ position:relative; z-index:1; }}
.om-mom {{ position:absolute; z-index:0; left:50%; top:50%; transform:translate(-50%,-50%); width:60px; height:60px; opacity:.13; pointer-events:none; }}
.om-name b {{ font-family:Marcellus,serif !important; font-weight:400; font-size:28px; color:{INK}; }}
.om-name small {{ font-family:Jost,sans-serif !important; font-weight:500; font-size:10px; letter-spacing:.4em; color:{ORANGE}; }}
.om-top .om-ar {{ color:{MUTED}; font-size:14px; }}
.om-hero {{ position:relative; overflow:hidden; border-radius:28px; color:#fff; padding:40px 44px; margin-bottom:22px; border:2px solid {EDGE};
  background: linear-gradient(135deg, #F7B06E 0%, #F29A50 45%, {ORANGE} 100%);
  display:grid; grid-template-columns: minmax(0,1fr) minmax(0,1.2fr); gap:24px; align-items:center; }}
.om-hero .ring {{ position:absolute; inset-inline-end:-80px; top:-80px; width:260px; height:260px; border-radius:50%;
  border:40px solid rgba(255,255,255,.16); }}
.om-hero .dot {{ position:absolute; inset-inline-end:120px; bottom:-50px; width:110px; height:110px; border-radius:50%; background:{INK}; opacity:.9; }}
.om-hero-text {{ position:relative; z-index:1; }}
.om-hero .kicker {{ font-size:14px; font-weight:600; color:#FFF3E6; }}
.om-hero h1 {{ margin:8px 0 10px; font-family:Cairo,sans-serif !important; font-weight:800;
  font-size:44px; line-height:1.3; color:#fff; padding:0; text-shadow:0 2px 12px rgba(0,0,0,.12); }}
.om-hero p {{ margin:0; font-size:17px; line-height:1.8; color:#FFF6EE; max-width:520px; }}
.om-stats {{ display:flex; gap:12px; margin-top:22px; flex-wrap:wrap; }}
.om-stats span {{ background:rgba(255,255,255,.22); border:1px solid rgba(255,255,255,.5); color:#fff;
  border-radius:14px; padding:8px 16px; font-size:14px; }}
.om-stats span b {{ font-family:Cairo,sans-serif !important; color:{INK}; font-size:18px; margin:0 4px; }}
.om-hero-pics {{ position:relative; z-index:1; height:300px; display:grid; grid-template-columns:1fr 1fr; gap:12px;
  overflow:hidden; border-radius:20px;
  -webkit-mask-image: linear-gradient(to bottom, transparent, #000 14%, #000 86%, transparent);
  mask-image: linear-gradient(to bottom, transparent, #000 14%, #000 86%, transparent); }}
.om-strip {{ overflow:hidden; }}
.om-track {{ display:flex; flex-direction:column; gap:12px; animation: omUp 38s linear infinite; }}
.om-track.rev {{ animation-name: omDown; animation-duration: 44s; }}
.om-hero-pics:hover .om-track {{ animation-play-state: paused; }}
.om-track img {{ width:100%; aspect-ratio:1/1; object-fit:contain; background:#fff; border-radius:16px; padding:8px; border:1.5px solid {EDGE};
  box-sizing:border-box; box-shadow:0 6px 16px rgba(0,0,0,.15); }}
@keyframes omUp {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-50%); }} }}
@keyframes omDown {{ from {{ transform: translateY(-50%); }} to {{ transform: translateY(0); }} }}
@media (prefers-reduced-motion: reduce) {{ .om-track {{ animation: none; }} }}
.om-sec {{ display:table; margin:6px 0 14px; padding:6px 16px; border-radius:999px; font-weight:700; font-size:15px;
  background:{ORANGE_SOFT}; color:{ORANGE_DARK}; border:1.5px solid {EDGE}; }}
.om-h2 {{ font-family:Cairo,sans-serif !important; font-weight:700; font-size:26px; color:{INK}; margin:6px 0 2px; }}
.card {{ background:#fff; border:1.5px solid {EDGE}; border-radius:22px; padding:14px; display:flex; flex-direction:column; gap:8px;
  margin-bottom:20px; transition:transform .15s, box-shadow .15s; }}
.card:hover {{ transform:translateY(-3px); box-shadow:0 10px 24px rgba(238,132,51,.16); }}
.card .ph {{ position:relative; border-radius:16px; background:#fff; border:1px solid #C9C9C9; overflow:hidden; }}
.card .ph img {{ width:100%; aspect-ratio:1/1; object-fit:contain; display:block; }}
.card .badge {{ position:absolute; top:10px; inset-inline-end:10px; font-size:12px; font-weight:700; padding:3px 10px;
  border-radius:999px; background:{INK}; color:#fff; }}
.card .badge.noon {{ background:#FEEE00; color:{INK}; }}
.card .title {{ font-weight:600; font-size:16px; line-height:1.55; color:{INK}; min-height:3.1em;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }}
.card .desc {{ color:{MUTED}; font-size:13px; line-height:1.7; min-height:3.4em;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }}
.card .tag {{ align-self:flex-start; font-size:12px; color:{ORANGE_DARK}; background:{ORANGE_SOFT}; border-radius:999px; padding:2px 10px; }}
.card a.buy {{ display:block; text-align:center; text-decoration:none; font-weight:600; font-size:14px;
  background:{ORANGE}; color:#fff !important; border-radius:12px; padding:11px; margin-top:4px; }}
.card a.buy:hover {{ background:{ORANGE_DARK}; }}
.om-foot {{ margin-top:36px; background:{ORANGE_SOFT}; color:{INK}; border-radius:24px; padding:30px 36px;
  border:1.5px solid {EDGE}; border-top:4px solid {ORANGE};
  display:flex; justify-content:space-between; align-items:flex-start; gap:30px; flex-wrap:wrap; }}
.om-foot b {{ font-family:Marcellus,serif !important; font-weight:400; font-size:24px; color:{INK}; }}
.om-foot p {{ margin:8px 0 0; font-size:14px; line-height:1.8; max-width:620px; color:{MUTED}; }}
.stTextInput input, .stNumberInput input {{ border-radius:12px !important; }}
div[data-baseweb="select"] > div {{ border-radius:12px !important; border:1.5px solid {EDGE} !important; }}
.stTextInput [data-baseweb="input"] {{ border-radius:12px !important; border:1.5px solid {EDGE} !important; }}
/* أزرار اللغة والمتجر وأرقام الصفحات */
[data-testid="stButtonGroup"] button {{
  border-radius:12px !important; border:1.5px solid {EDGE} !important; background:#fff !important; color:{INK} !important;
  font-weight:600 !important; min-height:42px; padding:0 18px !important; }}
[data-testid="stButtonGroup"] button[aria-checked="true"] {{
  background:{ORANGE} !important; border-color:{EDGE} !important; color:#fff !important; font-weight:700 !important; }}
[data-testid="stButtonGroup"] button[data-variant="pills"] {{ min-width:44px; padding:0 12px !important; }}
@media (max-width: 700px) {{
  .om-hero {{ padding:28px 22px; grid-template-columns: 1fr; }} .om-hero h1 {{ font-size:30px; }}
  .om-top .om-ar {{ display:none; }}
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
        "name_en": col("name_en").str.strip(),
        "name_it": col("name_it").str.strip(),
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


def good_tr(text):
    text = clean(text)
    return text if text and not text.startswith("#") and not text.lower().startswith("loading") else ""


def product_title(row):
    if LANG != "ar":
        tr = good_tr(row.get("name_" + LANG, ""))
        if tr:
            return tr
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


def card_html(row):
    title = product_title(row)
    desc = clean(row["description"]) if LANG == "ar" else ""
    if desc.startswith(title):
        desc = desc[len(title):].lstrip(" ،,-–|")
    img = row["image"] if row["image"].startswith("http") else PLACEHOLDER_IMG
    store = store_of(row)
    badge, label = TX[store], TX["buy_" + store]
    return (
        '<div class="card">'
        '<div class="ph">'
        f'<span class="badge {store}">{badge}</span>'
        f'<img src="{html.escape(img, quote=True)}" loading="lazy" alt="{html.escape(title, quote=True)}" '
        f'onerror="this.onerror=null;this.src=&quot;{PLACEHOLDER_IMG}&quot;">'
        "</div>"
        f'<div class="title">{html.escape(title)}</div>'
        f'<div class="desc">{html.escape(desc)}</div>'
        f'<span class="tag">{html.escape(cat_name(clean(row["category"])))}</span>'
        f'<a class="buy" href="{html.escape(product_link(row["link"]), quote=True)}" '
        f'target="_blank" rel="nofollow sponsored noopener">{label}</a>'
        "</div>"
    )


# ---------------- الصفحة ----------------
# ظل بسيط لأم شايلة طفلها ورا الاسم (من غير ملامح)
MOM_SVG = (
    '<svg class="om-mom" viewBox="28 0 64 64" aria-hidden="true">'
    '<g fill="#1A1A1A">'
    '<circle cx="62" cy="10" r="7.5"/>'
    '<circle cx="68" cy="6" r="3.6"/>'
    '<path d="M55 20c-6 4-9 16-11 44h38c-1-20-5-36-12-43-4-3-10-4-15-1z"/>'
    '<circle cx="47" cy="29" r="5.6"/>'
    '<ellipse cx="56" cy="38" rx="12" ry="6.2" transform="rotate(-18 56 38)"/>'
    '</g></svg>'
)

# لوجو: شنطة تسوق برتقالي وجواها قلب (تسوق باهتمام أم)
LOGO_SVG = (
    '<svg class="om-bag" width="44" height="50" viewBox="0 0 92 104" aria-hidden="true">'
    '<path d="M30 32V24a16 16 0 0 1 32 0v8" stroke="#1A1A1A" stroke-width="7" stroke-linecap="round" fill="none"/>'
    '<rect x="8" y="30" width="76" height="68" rx="18" fill="#EE8433"/>'
    '<path d="M46 84c-10-7-17-12.5-17-20.5a9 9 0 0 1 17-4.2 9 9 0 0 1 17 4.2c0 8-7 13.5-17 20.5z" fill="#FFFFFF"/>'
    '<circle cx="31" cy="44" r="3.2" fill="#1A1A1A"/><circle cx="61" cy="44" r="3.2" fill="#1A1A1A"/>'
    "</svg>"
)

st.markdown(
    '<div class="om-top">'
    f'<div class="om-logo">{LOGO_SVG}'
    f'<span class="om-name">{MOM_SVG}<b>OmAmin</b><small>STORE</small></span></div>'
    f'<span class="om-ar">{STORE_NAME_AR} · {TX["tagline"]}</span>'
    "</div>",
    unsafe_allow_html=True,
)

df = load_data()

if df is None or df.empty:
    st.warning(TX["loading"])
    st.stop()

categories = sorted(c for c in df["category"].unique() if c)


def hero_strip(frame, n=10, seed=0):
    """شريط صور منتجات بيتحرك لوحده جوه البانر"""
    pics = frame[frame["image"].str.startswith("http")]
    if pics.empty:
        return ""
    pics = pics.sample(min(n, len(pics)), random_state=seed)
    imgs = "".join(f'<img src="{html.escape(u, quote=True)}" alt="">' for u in pics["image"])
    # بنكرر الصور مرتين عشان الحركة تبان متصلة من غير قطع
    return f'<div class="om-strip"><div class="om-track">{imgs}{imgs}</div></div>'


day_seed = pd.Timestamp.now().dayofyear
strips = hero_strip(df, 10, day_seed) + hero_strip(df, 10, day_seed + 7).replace(
    'class="om-track"', 'class="om-track rev"'
)

# الصور على اليمين والكلام على الشمال (في العربي)
pics_html = f'<div class="om-hero-pics">{strips}</div>'
text_html = (
    '<div class="om-hero-text">'
    f'<div class="kicker">{TX["kicker"]}</div>'
    f'<h1>{TX["hero"]}</h1>'
    f'<p>{TX["hero_p"]}</p>'
    '<div class="om-stats">'
    f'<span><b>{len(df)}</b>{TX["products"]}</span>'
    f'<span><b>{len(categories)}</b>{TX["cats"]}</span>'
    f'<span>{TX["both"]}</span>'
    "</div></div>"
)
st.markdown(
    '<div class="om-hero"><div class="ring"></div><div class="dot"></div>'
    + (pics_html + text_html if LANG == "ar" else text_html + pics_html)
    + "</div>",
    unsafe_allow_html=True,
)

# ---------------- البحث والفلاتر ----------------
if "page" not in st.session_state:
    st.session_state.page = 1


def reset_page():
    st.session_state.page = 1


c1, c2 = st.columns([2, 1])
with c1:
    query = st.text_input(TX["search"], placeholder=TX["search_ph"], on_change=reset_page)
with c2:
    cat_options = ["__all__"] + categories
    selected_category = st.selectbox(
        TX["category"], cat_options, on_change=reset_page,
        format_func=lambda c: TX["all_cats"] if c == "__all__" else cat_name(c),
    )

# أزرار المتجر: كل المتاجر / أمازون / نون
store_keys = ["all", "amazon", "noon"]
store_labels = {"all": TX["all_stores"], "amazon": TX["amazon"], "noon": TX["noon"]}
if hasattr(st, "segmented_control"):
    selected_store = st.segmented_control(
        TX["store"], store_keys, default="all", key="store_btn", on_change=reset_page,
        format_func=lambda k: store_labels[k],
    ) or "all"
else:
    selected_store = st.radio(TX["store"], store_keys, horizontal=True, on_change=reset_page,
                              format_func=lambda k: store_labels[k])

view = df.copy()
view["_store"] = view.apply(store_of, axis=1)
if selected_category != "__all__":
    view = view[view["category"] == selected_category]
if selected_store in ("amazon", "noon"):
    view = view[view["_store"] == selected_store]
if query:
    q = query.strip()
    view = view[
        view["name"].str.contains(q, case=False, regex=False)
        | view["description"].str.contains(q, case=False, regex=False)
        | view["category"].str.contains(q, case=False, regex=False)
        | view["name_en"].str.contains(q, case=False, regex=False)
        | view["name_it"].str.contains(q, case=False, regex=False)
    ]

total = len(view)
# كل صفحة فيها منتجات متجر واحد بس: صفحات أمازون الأول وبعدها صفحات نون (من غير خلط)
chunks = []
for store_key in ("amazon", "noon", "other"):
    part = view[view["_store"] == store_key]
    for i in range(0, len(part), PER_PAGE):
        chunks.append((store_key, part.iloc[i:i + PER_PAGE]))
pages = max(1, len(chunks))
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
            TX["page"], options, key=key, on_change=go_to_page, args=(key,),
            label_visibility="collapsed",
        )


heading = cat_name(selected_category) if selected_category != "__all__" else TX["all_products"]
st.markdown(f'<div class="om-h2">{html.escape(heading)}</div>', unsafe_allow_html=True)
page = st.session_state.page
st.caption(
    f"{total} {TX['products']} · {TX['page']} {page} {TX['of']} {pages}" if pages > 1
    else f"{total} {TX['products']}"
)
pager("pg_top")

if total == 0:
    st.info(TX["none"])

page_store, page_rows = chunks[page - 1] if chunks else ("", view.iloc[0:0])
if page_store and selected_store == "all":
    st.markdown(f'<div class="om-sec">{TX["sec_" + page_store]}</div>', unsafe_allow_html=True)
rows = page_rows.to_dict("records")
for start in range(0, len(rows), COLUMNS_PER_ROW):
    cols = st.columns(COLUMNS_PER_ROW)
    for col, row in zip(cols, rows[start:start + COLUMNS_PER_ROW]):
        with col:
            st.markdown(card_html(row), unsafe_allow_html=True)

if pages > 1:
    st.caption(f"{TX['page']} {page} {TX['of']} {pages}")
    pager("pg_bottom")

st.markdown(
    '<div class="om-foot"><div><b>OmAmin Store</b>'
    f'<p>{TX["footer"]}</p></div>'
    f'<div class="om-ar" style="color:{ORANGE}">{STORE_NAME_AR} · {TX["love"]}</div></div>',
    unsafe_allow_html=True,
)
