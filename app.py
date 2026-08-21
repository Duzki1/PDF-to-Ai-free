import streamlit as st
import requests
import pypdf
from io import BytesIO

# إعدادات الصفحة
st.set_page_config(page_title="مستعرض ومشارك ملفات PDF", page_icon="📄", layout="wide")

st.title("📄 مستعرض ومشارك ملفات PDF الذكي والسريع")
st.write("تم تطوير هذا الموقع ليتعامل مع الملفات الضخمة جداً بسرعة صاروخية دون أي تعليق!")

option = st.radio("اختر طريقة إدخال ملف الـ PDF:", ("وضع رابط مباشر للمشاركة مع الـ AI", "رفع ملف من جهازك (للقراءة الشخصية)"))

pdf_file = None
source_info = ""

if option == "وضع رابط مباشر للمشاركة مع الـ AI":
    query_params = st.query_params
    default_url = query_params.get("pdf_url", "")
    pdf_url = st.text_input("أدخل رابط ملف الـ PDF المباشر هنا:", value=default_url)
    
    if pdf_url:
        st.query_params["pdf_url"] = pdf_url
        st.info(f"🔗 **رابط المشاركة السريع:** انسخ رابط المتصفح الحالي وأرسله لأي ذكاء اصطناعي!")
        try:
            with st.spinner("جاري تحميل الملف من الرابط..."):
                response = requests.get(pdf_url)
                response.raise_for_status()
                pdf_file = BytesIO(response.content)
                source_info = "تم التحميل من الرابط بنجاح!"
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء تحميل الرابط.")

else:
    uploaded_file = st.file_uploader("اختر ملف PDF من جهازك:", type=["pdf"])
    if uploaded_file is not None:
        pdf_file = BytesIO(uploaded_file.read())
        source_info = f"تم رفع الملف بنجاح! [{uploaded_file.name}]"
        st.warning("⚠️ تنبيه: الملف المرفوع من جهازك لا يمكن مشاركته برابط مع الـ AI.")

# الحل السريع: قراءة وعرض صفحة واحدة فقط يختارها المستخدم لمنع التعليق
if pdf_file is not None:
    try:
        reader = pypdf.PdfReader(pdf_file)
        total_pages = len(reader.pages)
        
        st.success(f"✅ {source_info} | إجمالي عدد الصفحات: {total_pages}")
        
        st.subheader("📖 تصفح محتوى الملف بسرّعة صاروخية:")
        
        # صندوق يختار منه المستخدم رقم الصفحة التي يريد قراءتها
        page_number = st.number_input(f"أدخل رقم الصفحة التي تريد قراءتها (من 1 إلى {total_pages}):", 
                                      min_value=1, 
                                      max_value=total_pages, 
                                      value=1)
        
        # بايثون يقرأ فقط الصفحة المختارة ويستخرج نصها في أجزاء من الثانية!
        with st.spinner(f"جاري قراءة الصفحة {page_number}..."):
            # مصفوفات بايثون تبدأ من الصفر، لذا نطرح 1 من رقم الصفحة
            selected_page = reader.pages[page_number - 1]
            page_text = selected_page.extract_text()
            
        # عرض نص الصفحة المختارة فقط
        st.write(f"### 📝 محتوى الصفحة رقم ({page_number})")
        if page_text.strip():
            st.text_area(label="محتوى الصفحة", value=page_text, height=350)
        else:
            st.info("ℹ️ هذه الصفحة لا تحتوي على نصوص مقروءة (ربما تحتوي على صورة فقط).")
            
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء معالجة الملف.")
