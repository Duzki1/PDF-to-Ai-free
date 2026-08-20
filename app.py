import streamlit as st
import pypdf
from io import BytesIO

# إعدادات الصفحة
st.set_page_config(page_title="مستعرض ومشارك ملفات PDF", page_icon="📄", layout="wide")

st.title("📄 مستعرض ومشارك ملفات PDF للجميع")
st.write("قم برفع ملف PDF من جهازك أو جوالك ليتم تحويله إلى نص ويب يمكن لأي شخص أو ذكاء اصطناعي قراءته.")

# خيار رفع الملف من الجهاز مباشرة
uploaded_file = st.file_uploader("اختر ملف PDF من جهازك:", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner("جاري قراءة ملف الـ PDF..."):
            # قراءة ملف الـ PDF المرفوع مباشرة من الذاكرة
            pdf_file = BytesIO(uploaded_file.read())
            reader = pypdf.PdfReader(pdf_file)
            
            st.success(f"✅ تم تحميل الملف بنجاح! اسم الملف: {uploaded_file.name} | عدد الصفحات: {len(reader.pages)}")
            
            # استخراج النص
            st.subheader("📝 محتوى الملف النصي:")
            full_text = ""
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                full_text += f"\n--- الصفحة {i+1} ---\n{text}"
            
            # عرض النص في صندوق ويب متاح للقراءة والكشط الرقمي
            st.text_area(label="النص المستخرج", value=full_text, height=500)
            
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء قراءة الملف. تأكد من أن الملف غير تالف.")
