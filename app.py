import streamlit as st
import pandas as pd

# إعدادات صفحة المتجر الاسم والعنوان
st.set_page_config(page_title="Omnia store", page_icon="🛍️", layout="wide")

# عنوان المتجر الرئيسي
st.title("🛍️ Omnia store")
st.write("أهلاً بكِ في متجرك الإلكتروني المحدث أوتوماتيكياً من جدول جوجل!")

# رابط جدول جوجل المباشر للـ CSV
sheet_id = "1ir7FX_oIRJOx-7JPOmahyYPW7hUPbLpwAxqdRrMNbFQ"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

# دالة لتحميل المنتجات من جدول جوجل مع التخزين المؤقت لتسريع الموقع
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(sheet_url)
        # التأكد من إزالة أي مسافات زائدة في أسماء الأعمدة
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return None

# جلب البيانات
df = load_data()

if df is not None and not df.empty:
    # التأكد من وجود الأعمدة المطلوبة
    required_cols = ["Category", "Product_ID", "Name"]
    if all(col in df.columns for col in required_cols):
        
        # تصفية حسب الأقسام
        categories = df["Category"].dropna().unique().tolist()
        selected_category = st.sidebar.selectbox("اختر القسم:", ["الكل"] + categories)
        
        if selected_category != "الكل":
            filtered_df = df[df["Category"] == selected_category]
        else:
            filtered_df = df
            
        st.subheader(f"المنتجات المتوفرة ({len(filtered_df)})")
        
        # عرض المنتجات بشكل منظم
        for index, row in filtered_df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{row['Name']}**")
                st.caption(f"الكود: {row['Product_ID']}")
            with col2:
                # زرار يفتح رابط أمازون مباشرة باستخدام الكود
                product_link = f"https://www.amazon.com/dp/{row['Product_ID']}"
                st.markdown(f"[عرض المنتج على أمازون]({product_link})", unsafe_allow_html=True)
            st.divider()
    else:
        st.error("خطأ: أسماء الأعمدة في جدول جوجل غير مطابقة (يجب أن تكون: Category, Product_ID, Name)")
else:
    st.warning("جاري تحميل البيانات أو أن جدول جوجل فارغ حالياً. تأكد من إتاحة الرابط للعامة.")
