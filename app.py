import streamlit as st
import requests
import pypdf
from io import BytesIO
import time

# إعدادات الصفحة
st.set_page_config(page_title="مستعرض ومشارك ملفات PDF", page_icon="📄", layout="wide")

st.title("📄 مستعرض ومشارك ملفات PDF للجميع")
st.write("يمكنك الآن رفع ملف من جهازك، أو وضع رابط مباشر ليتمكن الذكاء الاصطناعي من قراءته!")

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
            with st.spinner("جاري الاتصال بالرابط وتحميل الملف..."):
                response = requests.get(pdf_url)
                response.raise_for_status()
                pdf_file = BytesIO(response.content)
                source_info = "تم التحميل من الرابط بنجاح!"
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء تحميل الرابط. تأكد من أنه رابط مباشر ينتهي بـ .pdf")

else:
    uploaded_file = st.file_uploader("اختر ملف PDF من جهازك:", type=["pdf"])
    if uploaded_file is not None:
        pdf_file = BytesIO(uploaded_file.read())
        source_info = f"تم رفع الملف من الجهاز بنجاح! اسم الملف: {uploaded_file.name}"
        st.warning("⚠️ تنبيه: الملف المرفوع من جهازك لا يمكن مشاركته برابط مع الـ AI. للمشاركة، استخدم خيار الرابط المباشر.")

# معالجة وقراءة الملف بذكاء وسرعة
if pdf_file is not None:
    try:
        reader = pypdf.PdfReader(pdf_file)
        total_pages = len(reader.pages)
        
        st.success(f"✅ {source_info} | عدد الصفحات الإجمالي في الملف: {total_pages}")
        
        # 💡 ميزة الذكاء والسرعة: إذا كان الملف ضخماً جداً، نقرأ أول 50 صفحة فقط لكي لا يعلق الموقع
        pages_to_read = total_pages
        if total_pages > 50:
            st.warning("ℹ️ هذا الملف ضخم جداً! لتسريع التصفح، سيقوم الموقع بقراءة أول 50 صفحة فقط.")
            pages_to_read = 50
        
        st.subheader("⏳ جاري معالجة وقراءة الصفحات المحددة:")
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        full_text = ""
        
        # حلقة التكرار تقرأ فقط حتى العدد المحدد (pages_to_read)
        for i in range(pages_to_read):
            page = reader.pages[i]
            text = page.extract_text()
            full_text += f"\n--- الصفحة {i+1} ---\n{text}"
            
            current_progress = (i + 1) / pages_to_read
            percentage = int(current_progress * 100)
            
            status_text.text(f"جاري قراءة الصفحة {i+1} من أصل {pages_to_read} ({percentage}%)")
            progress_bar.progress(current_progress)
            time.sleep(0.02)
            
        status_text.text("✨ تم استخراج النص بنجاح!")
        progress_bar.empty()
        
        st.subheader("📝 محتوى الملف النصي:")
        st.text_area(label="النص المستخرج", value=full_text, height=500)
        
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء قراءة الملف.")
