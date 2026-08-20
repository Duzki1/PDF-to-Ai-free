import streamlit as st
import requests
import pypdf
from io import BytesIO
import time

# إعدادات الصفحة
st.set_page_config(page_title="مستعرض ومشارك ملفات PDF", page_icon="📄", layout="wide")

st.title("📄 مستعرض ومشارك ملفات PDF للجميع")
st.write("يمكنك الآن رفع ملف من جهازك، أو وضع رابط مباشر ليتمكن الذكاء الاصطناعي من قراءته!")

# إنشاء قائمة اختيار لطريقة إدخال الملف
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

# إذا تم الحصول على ملف PDF، قم بقراءته وعرض شريط التقدم والنسبة المئوية
if pdf_file is not None:
    try:
        reader = pypdf.PdfReader(pdf_file)
        total_pages = len(reader.pages)
        
        st.success(f"✅ {source_info} | عدد الصفحات الإجمالي: {total_pages}")
        
        # ─── إضافة شريط التقدم والنسبة المئوية ───
        st.subheader("⏳ جاري معالجة وقراءة صفحات الملف:")
        
        # مكان مخصص لعرض النص المتغير (النسبة ورقم الصفحة)
        status_text = st.empty()
        # شريط التقدم المرئي
        progress_bar = st.progress(0)
        
        full_text = ""
        
        # حلقة تكرار تمر على الصفحات وتحسب النسبة المئوية
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            full_text += f"\n--- الصفحة {i+1} ---\n{text}"
            
            # حساب النسبة المئوية الحالية (رقم الصفحة الحالية تقسيم العدد الإجمالي للصفحات)
            current_progress = (i + 1) / total_pages
            percentage = int(current_progress * 100)
            
            # تحديث النسبة المئوية وشريط التقدم بشكل حي على الشاشة
            status_text.text(f"جاري قراءة الصفحة {i+1} من أصل {total_pages} ({percentage}%)")
            progress_bar.progress(current_progress)
            
            # تأخير بسيط جداً بالأجزاء من الثانية لجعل الحركة سلسة ومرئية في الملفات الصغيرة
            time.sleep(0.05)
            
        # عند اكتمال القراءة 100%، نقوم بمسح شريط التقدم وعرض النص كاملاً
        status_text.text("✨ تم استخراج النص بالكامل بنجاح 100%!")
        progress_bar.empty() # إخفاء شريط التقدم بعد الاكتمال
        
        # عرض النص المستخرج للمستخدم
        st.subheader("📝 محتوى الملف النصي:")
        st.text_area(label="النص المستخرج", value=full_text, height=500)
        
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء قراءة الملف.")
