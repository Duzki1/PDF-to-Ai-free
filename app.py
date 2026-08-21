import streamlit as st
import requests
import pypdf
from io import BytesIO
import base64

# إعدادات الصفحة
st.set_page_config(page_title="مستعرض ومشارك ملفات PDF", page_icon="📄", layout="wide")

st.title("📄 مستعرض ومشارك ملفات PDF الذكي مع المعاينة")
st.write("تم تطوير هذا الموقع ليتعامل مع الملفات الضخمة جداً بسرعة صاروخية مع ميزة المعاينة!")

option = st.radio("اختر طريقة إدخال ملف الـ PDF:", ("وضع رابط مباشر للمشاركة مع الـ AI", "رفع ملف من جهازك (للقراءة الشخصية)"))

pdf_file = None
source_info = ""
pdf_bytes = None

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
                pdf_bytes = response.content
                pdf_file = BytesIO(pdf_bytes)
                source_info = "تم التحميل من الرابط بنجاح!"
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء تحميل الرابط.")

else:
    uploaded_file = st.file_uploader("اختر ملف PDF من جهازك:", type=["pdf"])
    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        pdf_file = BytesIO(pdf_bytes)
        source_info = f"تم رفع الملف بنجاح! [{uploaded_file.name}]"
        st.warning("⚠️ تنبيه: الملف المرفوع من جهازك لا يمكن مشاركته برابط مع الـ AI.")

# إذا تم تحميل الملف، نعرض نظام الصفحات مع المعاينة والنص معاً
if pdf_file is not None and pdf_bytes is not None:
    try:
        reader = pypdf.PdfReader(pdf_file)
        total_pages = len(reader.pages)
        
        st.success(f"✅ {source_info} | إجمالي عدد الصفحات: {total_pages}")
        
        # صندوق اختيار رقم الصفحة
        page_number = st.number_input(f"أدخل رقم الصفحة للتصفح والمعاينة (من 1 إلى {total_pages}):", 
                                      min_value=1, 
                                      max_value=total_pages, 
                                      value=1)
        
        # قراءة النص للصفحة المختارة
        with st.spinner(f"جاري قراءة وتجهيز الصفحة {page_number}..."):
            selected_page = reader.pages[page_number - 1]
            page_text = selected_page.extract_text()
            
        # تقسيم الشاشة إلى عمودين (عمود للمعاينة وعمود للنص المستخرج) ليكون التصميم احترافياً!
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"### 🔍 معاينة الصفحة رقم ({page_number})")
            
            # كود ذكي لإنشاء رابط معاينة سريع ومباشر للملف (يفتح في المتصفح)
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            # إضافة سطر التمرير لرقم الصفحة المحددة في المعاينة
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={page_number}" width="100%" height="500" type="application/pdf"></iframe>'
            
            # عرض المعاينة داخل الموقع
            st.markdown(pdf_display, unsafe_allow_bytes=True, unsafe_allow_html=True)
            
            # زر إضافي لفتح الملف كاملاً في صفحة جديدة كـ رابط معاينة خارجي
            st.link_button("🌐 فتح رابط معاينة كامل للملف في صفحة جديدة", f"data:application/pdf;base64,{base64_pdf}")

        with col2:
            st.write(f"### 📝 النص المستخرج من الصفحة ({page_number})")
            if page_text.strip():
                st.text_area(label="النص المستخرج للنسخ أو للـ AI", value=page_text, height=500)
            else:
                st.info("ℹ️ هذه الصفحة لا تحتوي على نصوص مقروءة (ربما تحتوي على صورة فقط).")
            
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء معالجة الملف أو إنشاء المعاينة.")
