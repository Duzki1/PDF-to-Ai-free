import streamlit as st
import requests
import pypdf
from io import BytesIO
import base64

# إعدادات الصفحة
st.set_page_config(page_title="مستعرض ومشارك ملفات PDF", page_icon="📄", layout="wide")

st.title("📄 مستعرض ومشارك ملفات PDF الذكي")
st.write("تم تطوير الموقع! يمكنك الآن رفع ملف من جهازك وتحويله إلى رابط مباشر لمشاركته مع الـ AI.")

option = st.radio("اختر طريقة إدخال ملف الـ PDF:", ("رفع ملف من جهازك وصنع رابط له", "وضع رابط مباشر جاهز"))

pdf_file = None
source_info = ""
pdf_bytes = None
generated_url = ""

if option == "رفع ملف من جهازك وصنع رابط له":
    uploaded_file = st.file_uploader("اختر ملف PDF من جهازك:", type=["pdf"])
    
    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        pdf_file = BytesIO(pdf_bytes)
        source_info = f"تم رفع الملف بنجاح! [{uploaded_file.name}]"
        
        # زر مخصص لإنشاء الرابط لمنع الرفع التلقائي المتكرر
        if st.button("🔗 اضغط هنا لتحويل الملف إلى رابط مباشر للـ AI"):
            with st.spinner("جاري رفع الملف وإنشاء الرابط المباشر..."):
                try:
                    # نستخدم خدمة tmpfiles.org المجانية لرفع الملف والحصول على رابط مباشر
                    files = {'file': (uploaded_file.name, pdf_bytes, 'application/pdf')}
                    # نطلب الرفع إلى السيرفر
                    response = requests.post('https://tmpfiles.org', files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        # الرابط الافتراضي يكون للمعاينة، نقوم بتعديله برمجياً ليصبح رابط تحميل مباشر
                        raw_url = data['data']['url']
                        generated_url = raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                        
                        # تحديث رابط المتصفح (Query Params) لتسهيل المشاركة
                        st.query_params["pdf_url"] = generated_url
                    else:
                        st.error("❌ فشل السيرفر في إنشاء الرابط، حاول مجدداً بعد قليل.")
                except Exception as e:
                    st.error("❌ حدث خطأ أثناء الاتصال بسيرفر رفع الملفات.")
        
        # إذا تم توليد الرابط بنجاح، نعرضه للمستخدم
        # نتحقق أيضاً لو كان الرابط موجوداً مسبقاً في المتصفح
        current_url = generated_url if generated_url else st.query_params.get("pdf_url", "")
        
        if current_url:
            st.success("🎉 تم إنشاء الرابط المباشر بنجاح!")
            st.text_input("رابط الـ PDF المباشر (جاهز للنسخ وإرساله للـ AI):", value=current_url)
            st.info("🔗 **نصيحة:** يمكنك أيضاً نسخ رابط المتصفح الحالي بالكامل وإرساله للـ AI وسيفتح له موقعك ومعه الملف جاهزاً!")

else:
    query_params = st.query_params
    default_url = query_params.get("pdf_url", "")
    pdf_url = st.text_input("أدخل رابط ملف الـ PDF المباشر هنا:", value=default_url)
    
    if pdf_url:
        st.query_params["pdf_url"] = pdf_url
        st.info(f"🔗 **رابط المشاركة السريع:** انسخ رابط المتصفح الحالي وأرسله لأي ذكاء اصطناعي!")
        try:
            with st.spinner("جاري تحميل الملف من الرابط..."):
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(pdf_url, headers=headers, timeout=15)
                response.raise_for_status()
                pdf_bytes = response.content
                pdf_file = BytesIO(pdf_bytes)
                source_info = "تم التحميل من الرابط بنجاح!"
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء تحميل الرابط. تأكد من أن الرابط مباشر وينتهي بـ .pdf")

# عرض نظام الصفحات والمعاينة بعد المعالجة
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
            
        # تقسيم الشاشة إلى عمودين
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"### 🔍 معاينة الصفحة رقم ({page_number})")
            
            # تشفير الملف وعرض المعاينة بشكل آمن
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={page_number}" width="100%" height="500" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
        with col2:
            st.write(f"### 📝 النص المستخرج من الصفحة ({page_number})")
            if page_text and page_text.strip():
                st.text_area(label="النص المستخرج للنسخ أو للـ AI", value=page_text, height=450)
            else:
                st.info("ℹ️ هذه الصفحة لا تحتوي على نصوص مقروءة بوضوح (قد تكون صورة أو ممسوحة ضوئيًا).")
            
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء معالجة الملف. تأكد من أن الملف غير مشفر بكلمة سر.")
