import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import pdfplumber
import re
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from datetime import datetime
from io import BytesIO
import tempfile
import os
import cv2
import numpy as np
import base64
import time
from PIL import Image
import easyocr

# --- PAGE CONFIG ---
st.set_page_config(page_title="వాయి వేగ Multi-Tool", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("వాయి వేగ Navigation")
choice = st.sidebar.radio("ఏం చేయాలనుకుంటున్నారు?", 
                         ["Home", "Barcode Generator", "PDF to Excel Converter", "Smart PDF Label Editor", "Image Upscaler (4K)", "Image to Text (OCR)"])

# --- 🏠 0. HOME PAGE (COLORFUL DESIGN) ---
if choice == "Home":
    st.markdown("""
        <style>
        .main-title { font-size: 50px; color: #FF4B4B; font-weight: bold; text-align: center; margin-bottom: 10px; }
        .sub-title { font-size: 20px; color: #ffffff; text-align: center; margin-bottom: 30px; background: linear-gradient(90deg, #FF4B4B, #4B8BFF); padding: 10px; border-radius: 10px; }
        .feature-card { background-color: #262730; padding: 20px; border-radius: 15px; border-left: 5px solid #FF4B4B; margin-bottom: 15px; transition: transform 0.3s; }
        .feature-card:hover { transform: scale(1.02); border-left: 5px solid #4B8BFF; }
        .feature-icon { font-size: 25px; margin-right: 10px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="main-title">వాయి వేగ Multi-Tool 🚀</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">మీ బిజినెస్ పనులను సులభతరం చేసే స్మార్ట్ AI టూల్స్</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="feature-card"><span class="feature-icon">📦</span><b style="color:#FF4B4B;">Barcode Generator</b><br>ప్రొఫెషనల్ 3-ఇంచ్ లేబుల్స్ తయారు చేయండి.</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card"><span class="feature-icon">📊</span><b style="color:#4B8BFF;">PDF to Excel</b><br>ఢిల్లీవరీ PDFల నుండి డేటాను ఎక్సెల్ లోకి మార్చండి.</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><span class="feature-icon">📄</span><b style="color:#00FFCC;">Smart PDF Editor</b><br>లేబుల్స్ లో అమౌంట్ మరియు వెయిట్ ఎడిట్ చేయండి.</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card"><span class="feature-icon">📝</span><b style="color:#FF66B2;">Image to Text</b><br>ఫోటోలలోని అక్షరాలను (English/Telugu) టెక్స్ట్ గా మార్చండి.</div>', unsafe_allow_html=True)

# --- 📦 1. BARCODE GENERATOR ---
elif choice == "Barcode Generator":
    st.title("📦 Standard 3-Inch Barcode Labels")
    numbers_input = st.text_area("ట్రాకింగ్ నంబర్లను ఇక్కడ పేస్ట్ చేయండి:", height=150)
    company_name = st.text_input("కంపెనీ పేరు ఇవ్వండి:")
    if st.button("Generate Standard PDF"):
        if numbers_input.strip() and company_name.strip():
            tracking_list = [n.strip() for n in numbers_input.split('\n') if n.strip()]
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4
            label_width, label_height = 3 * inch, 1.5 * inch
            margin_x, margin_y = 0.5 * inch, 0.5 * inch
            curr_x, curr_y = margin_x, height - margin_y - label_height
            for num in tracking_list:
                try:
                    code_class = barcode.get_barcode_class('code128')
                    my_barcode = code_class(num, writer=ImageWriter())
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        img_path = my_barcode.save(tmp.name.replace(".png", ""), options={"write_text": True, "font_size": 8, "text_distance": 3})
                    c.setFont("Helvetica-Bold", 10)
                    c.drawCentredString(curr_x + (label_width/2), curr_y + label_height - 15, company_name.upper())
                    c.drawImage(img_path, curr_x + 10, curr_y + 10, width=label_width-20, height=label_height-40)
                    curr_x += label_width + 0.2 * inch
                    if curr_x + label_width > width:
                        curr_x = margin_x
                        curr_y -= label_height + 0.3 * inch
                    if curr_y < margin_y:
                        c.showPage()
                        curr_y = height - margin_y - label_height
                        curr_x = margin_x
                    if os.path.exists(img_path): os.remove(img_path)
                except Exception as e: st.error(f"Error: {e}")
            c.save()
            st.success("లేబుల్స్ తయారయ్యాయి!")
            st.download_button("Download Labels PDF", data=pdf_buffer.getvalue(), file_name=f"{company_name}_Standard.pdf")

# --- 📊 2. PDF TO EXCEL CONVERTER ---
elif choice == "PDF to Excel Converter":
    st.title("📊 వాయి వేగ PDF to Excel")
    col_b, col_h = st.columns(2)
    with col_b: client_name = st.text_input("క్ลయింట్ నేమ్ / ఐడి ఎంటర్ చేయండి (Column B):")
    with col_h: weight_val = st.text_input("వెయిట్ (Weight) ఎంటర్ చేయండి (Column H):")
    pdf_files = st.file_uploader("PDF ఫైల్స్ అప్‌లోడ్ చేయండి", type=['pdf'], accept_multiple_files=True)
    if pdf_files:
        all_extracted_data = []
        for pdf_file in pdf_files:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        date_match = re.search(r"(\d{2}-[a-zA-Z]{3}-\d{4})", text)
                        final_date = ""
                        if date_match:
                            try:
                                d_obj = datetime.strptime(date_match.group(1), '%d-%b-%Y')
                                final_date = d_obj.strftime('%d-%m-%Y')
                            except: final_date = ""
                        awb = re.search(r"AWB#\s*(\d+)", text)
                        name = re.search(r"Ship to\s*-\s*([^\n]+)", text)
                        pin = re.search(r"PIN\s*[:\-\s]*(\d{6})", text)
                        if awb or name:
                            all_extracted_data.append({
                                "A": "", "B": client_name, "C": final_date,
                                "D": awb.group(1) if awb else "",
                                "E": name.group(1).strip() if name else "",
                                "F": pin.group(1) if pin else "",
                                "G": "", "H": weight_val
                            })
        if all_extracted_data:
            df = pd.DataFrame(all_extracted_data)
            st.dataframe(df)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            st.download_button("Download Excel File", data=output.getvalue(), file_name="Vaayi_Vega_Data.xlsx")

# --- 📄 3. SMART PDF LABEL EDITOR ---
elif choice == "Smart PDF Label Editor":
    st.title("📄 Smart PDF Label Editor")
    company_type = st.radio("ఏ కంపెనీ లేబుల్?", ["DTDC", "Delhivery"], horizontal=True)
    page_option = st.selectbox("ఏ పేజీలను ఎడిట్ చేయాలి?", ["All Pages", "Custom Page Number"])
    custom_pg = 1
    if page_option == "Custom Page Number":
        custom_pg = st.number_input("ఏ పేజీ నంబర్ ఎడిట్ చేయాలి?", min_value=1, step=1)
    up_files = st.file_uploader(f"{company_type} PDF ఫైల్స్", type=["pdf"], accept_multiple_files=True)
    if up_files:
        for u_file in up_files:
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1: n_amt = st.text_input(f"అమౌంట్ Rs.", key=f"a_{u_file.name}")
            with c2: n_wt = st.text_input(f"వెయిట్ KG", key=f"w_{u_file.name}")
            if st.button(f"Process {u_file.name}"):
                if n_amt and n_wt:
                    doc = fitz.open(stream=u_file.read(), filetype="pdf")
                    pages_to_edit = range(len(doc)) if page_option == "All Pages" else [custom_pg - 1]
                    for p_idx in pages_to_edit:
                        if 0 <= p_idx < len(doc):
                            page = doc[p_idx]
                            if company_type == "DTDC":
                                page.add_redact_annot(fitz.Rect(100, 480, 260, 515), fill=(1,1,1))
                                page.apply_redactions()
                                page.insert_text((75, 505), f"Rs. {n_amt}", fontsize=20, fontname="hebo")
                                w_hit = page.search_for("Weight")
                                if w_hit:
                                    page.add_redact_annot(fitz.Rect(w_hit[0].x1 + 2, w_hit[0].y0 - 2, 450, w_hit[0].y1 + 2), fill=(1,1,1))
                                    page.apply_redactions()
                                    page.insert_text((w_hit[0].x1 + 5, w_hit[0].y1 - 5.2), f": {n_wt} KG", fontsize=14, fontname="hebo")
                            else:
                                p_hit = page.search_for("Product")
                                if p_hit:
                                    sx, ay = p_hit[0].x0+2, p_hit[0].y1+18
                                    wy = ay+16
                                    page.add_redact_annot(fitz.Rect(sx, ay-12, sx+200, wy+5), fill=(1,1,1))
                                    page.apply_redactions()
                                    page.insert_text((sx, ay), f"Rs. {n_amt}", fontsize=12, color=(0,0,0))
                                    page.insert_text((sx, wy), f"Weight: {n_wt} KG", fontsize=12, color=(0,0,0))
                    res = BytesIO()
                    doc.save(res)
                    st.success("ప్రాసెస్ పూర్తయింది!")
                    st.download_button(f"Download {u_file.name}", data=res.getvalue(), file_name=f"Fixed_{u_file.name}")

# --- 🖼️ 4. IMAGE UPSCALER (4K QUALITY) ---
elif choice == "Image Upscaler (4K)":
    st.title("🖼️ AI Image Upscaler (4K Quality)")
    model_path = "EDSR_x4.pb"
    up_img = st.file_uploader("ఒక ఫోటోను అప్‌లోడ్ చేయండి", type=['png', 'jpg', 'jpeg'])
    if up_img:
        st.image(up_img, caption="Original Image", use_container_width=True)
        if st.button("Convert to 4K & Auto Download"):
            if os.path.exists(model_path):
                try:
                    file_bytes = np.asarray(bytearray(up_img.read()), dtype=np.uint8)
                    img = cv2.imdecode(file_bytes, 1)
                    sr = cv2.dnn_superres.DnnSuperResImpl_create()
                    sr.readModel(model_path); sr.setModel("edsr", 4)
                    with st.spinner("AI పని చేస్తోంది..."):
                        result = sr.upsample(img)
                        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                        st.image(result_rgb, caption="Upscaled 4K Image", use_container_width=True)
                        _, buffer = cv2.imencode('.png', result)
                        b64 = base64.b64encode(buffer).decode()
                        st.markdown(f'<a id="dl" href="data:image/png;base64,{b64}" download="4K_Result.png"></a><script>document.getElementById("dl").click();</script>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Error: {e}")
            else: st.error("Model file not found!")

# --- 📝 5. IMAGE TO TEXT (OCR) ---
elif choice == "Image to Text (OCR)":
    st.title("📝 Image to Text Converter")
    st.write("ఫోటోను అప్‌లోడ్ చేయండి, AI అందులోని టెక్స్ట్‌ని (English/Telugu) చదివి మీకు ఇస్తుంది.")
    up_img_ocr = st.file_uploader("ఇమేజ్ సెలెక్ట్ చేయండి", type=['png', 'jpg', 'jpeg'], key="ocr_uploader")
    if up_img_ocr:
        image = Image.open(up_img_ocr)
        st.image(image, caption="Uploaded Image", width=400)
        if st.button("Extract Text (టెక్స్ట్ తీయి)"):
            with st.spinner("AI చదువుతోంది, ఒక్క నిమిషం..."):
                reader = easyocr.Reader(['en', 'te'])
                img_array = np.array(image)
                result = reader.readtext(img_array, detail=0)
                if result:
                    full_text = "\n".join(result)
                    st.success("టెక్స్ట్ లభించింది!")
                    st.text_area("బయటకు తీసిన టెక్స్ట్:", full_text, height=300)
                    st.download_button("Download as TXT", full_text, file_name="extracted_text.txt")
                else:
                    st.warning("ఈ ఫోటోలో టెక్స్ట్ ఏమీ దొరకలేదు.")
