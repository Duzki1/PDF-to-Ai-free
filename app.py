import streamlit as str
import requests
import pypdf
from io import BytesIO

# إعدادات الصفحة
str.set_page_config(page_title="قارئ ومشارك ملفات PDF", page_icon="📄", layout="wide")

str.title("📄 مستعرض ومشارك ملفات PDF للجميع")
str.write("ضع رابط ملف الـ PDF في الأسفل ليتم تحويله إلى صفحة ويب يمكن لأي شخص أو ذكاء اصطناعي قراءتها.")

# الحصول على الرابط من عنوان URL للموقع (لتسهيل المشاركة)
query_params = str.query_params
default_url = query_params.get("pdf_url", "")

# خانة إدخال الرابط
pdf_url = str.text_input("أدخل رابط ملف الـ PDF المباشر هنا:", value=default_url)

if pdf_url:
    # تحديث رابط المتصفح ليتضمن رابط الملف لسهولة مشاركته
    str.query_params["pdf_url"] = pdf_url
    
    # زر مشاركة الرابط السريع
    current_page_url = f"https://streamlit.io..." # سيتم استبداله برابط موقعك بعد الرفع
    str.info(f"🔗 **رابط المشاركة السريع:** اضغط على الرابط في شريط المتصفح فوق وأرسله لأي شخص!")

    try:
        with str.spinner("جاري تحميل وقراءة ملف الـ PDF..."):
            # تحميل الملف من الرابط
            response = requests.get(pdf_url)
            response.raise_for_status()
            
            # قراءة ملف الـ PDF
            pdf_file = BytesIO(response.content)
            reader = pypdf.PdfReader(pdf_file)
            
            str.success(f"✅ تم تحميل الملف بنجاح! عدد الصفحات: {len(reader.pages)}")
            
            # عرض المحتوى كـ نص (سهل جداً للذكاء الاصطناعي قراءته)
            str.subheader("📝 محتوى الملف النصي:")
            full_text = ""
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                full_text += f"\n--- الصفحة {i+1} ---\n{text}"
            
            # عرض النص في صندوق ويب متاح للقراءة والكشط الرقمي
            str.text_area(label="النص المستخرج", value=full_text, height=500)
            
    except Exception as e:
        str.error(f"❌ حدث خطأ أثناء تحميل أو قراءة الملف. تأكد من أن الرابط مباشر وينتهي بـ .pdf")
