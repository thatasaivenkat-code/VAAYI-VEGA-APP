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
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="🚀 వాయి వేగ Pro", layout="wide")

# --- NAVIGATION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# --- PERFECT NEON CSS (FROM CODE 1) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Poppins:wght@300;400;600&display=swap');
* {font-family: 'Poppins', sans-serif !important;}
.stApp {background: #0a0a0a; min-height: 100vh;}
.main-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 3.5rem !important;
    background: linear-gradient(45deg, #ff00ff, #00ffff, #00ff9d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin: 20px 0;
    font-weight: 900 !important;
    text-shadow: 0 0 20px rgba(0,255,255,0.4);
}
.subtitle {
    font-size: 1.2rem !important;
    color: #00ffff;
    text-align: center;
    padding: 10px;
    background: rgba(0,255,255,0.05);
    border-radius: 50px;
    border: 1px solid #00ffff;
    margin-bottom: 30px;
}
.feature-card-btn {
    background: rgba(20,20,40,0.9) !important;
    border: 2px solid rgba(0,255,255,0.3) !important;
    border-radius: 20px !important;
    padding: 20px !important;
    transition: all 0.3s ease !important;
    text-align: center;
    width: 100%;
    margin-bottom: 15px;
}
.feature-card-btn:hover {
    border-color: #00ffff !important;
    box-shadow: 0 0 20px rgba(0,255,255,0.4) !important;
    transform: translateY(-5px);
}
.tool-section {
    background: rgba(20,20,40,0.95) !important;
    padding: 30px !important;
    border-radius: 25px !important;
    border: 2px solid rgba(255,0,255,0.4);
    box-shadow: 0 0 30px rgba(255,0,255,0.2);
}
.section-title {
    font-family: 'Orbitron', sans-serif !important;
    color: #00ffff;
    text-align: center;
    font-size: 2rem;
    margin-bottom: 20px;
}
/* Style Buttons */
.stButton > button {
    background: linear-gradient(135deg, #ff00ff, #00ffff) !important;
    color: white !important;
    border-radius: 25px !important;
    font-family: 'Orbitron', sans-serif !important;
    border: none !important;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<h2 style="color:#00ffff; font-family:Orbitron;">🚀 Vaayi Vega</h2>', unsafe_allow_html=True)
    choice = st.sidebar.radio("Navigation", 
                             ["🏠 Dashboard", "📦 Barcode Pro", "📊 PDF→Excel", 
                              "✏️ PDF Editor", "📸 Image OCR", "⚖️ VoluCalc"],
                             index=["🏠 Dashboard", "📦 Barcode Pro", "📊 PDF→Excel", "✏️ PDF Editor", "📸 Image OCR", "⚖️ VoluCalc"].index(st.session_state.page))
    st.session_state.page = choice

# ===============================================
# 🏠 HOME DASHBOARD
# ===============================================
if st.session_state.page == "🏠 Dashboard":
    st.markdown('<h1 class="main-title">వాయి వేగ PRO 🚀</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">5-in-1 AI Business Tools | Mass Neon Edition</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 Barcode Generator Pro\nCreate 3-inch Labels", key="btn_bar"): st.session_state.page = "📦 Barcode Pro"; st.rerun()
        if st.button("📊 PDF to Excel Converter\nExtract Delivery/DTDC Data", key="btn_pdf"): st.session_state.page = "📊 PDF→Excel"; st.rerun()
        if st.button("⚖️ Volumetric Calculator\nCompare Actual vs Vol Weight", key="btn_vol"): st.session_state.page = "⚖️ VoluCalc"; st.rerun()
    with col2:
        if st.button("✏️ Smart PDF Editor\nEdit Amount & Weight on Labels", key="btn_edit"): st.session_state.page = "✏️ PDF Editor"; st.rerun()
        if st.button("📸 Image to Text (OCR)\nEnglish + Telugu Extraction", key="btn_ocr"): st.session_state.page = "📸 Image OCR"; st.rerun()
        st.markdown('<div style="background:rgba(0,255,255,0.1); padding:25px; border-radius:20px; border:1px dashed #00ffff; text-align:center; color:#00ffff;">🚀 All Systems Nominal. Ready to Process!</div>', unsafe_allow_html=True)

# ===============================================
# 📊 PDF TO EXCEL (WORKING FUNCTION)
# ===============================================
elif st.session_state.page == "📊 PDF→Excel":
    st.markdown('<h2 class="section-title">📊 PDF to Excel Converter</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        use_del = st.checkbox("🚚 Delhivery", value=True)
        del_id = st.text_input("Delhivery Client ID:", value="1234")
        del_wt = st.text_input("Delhivery Weight:", value="0.5")
    with c2:
        use_dtdc = st.checkbox("📦 DTDC", value=True)
        dtdc_id = st.text_input("DTDC Client ID:", value="5678")
        dtdc_wt = st.text_input("DTDC Weight:", value="1.0")

    pdf_files = st.file_uploader("📄 Upload PDFs", type=['pdf'], accept_multiple_files=True)
    if pdf_files and st.button("🔄 Start Extracting Data"):
        all_data = []
        for f in pdf_files:
            with pdfplumber.open(f) as pdf:
                for pg in pdf.pages:
                    text = pg.extract_text()
                    if not text: continue
                    if use_del and "Delhivery" in text:
                        awb = re.search(r"AWB#\s*(\d+)", text)
                        pin = re.search(r"PIN\s*[:\-\s]*(\d{6})", text)
                        all_data.append({"Client": del_id, "AWB": awb.group(1) if awb else "", "Pincode": pin.group(1) if pin else "", "Weight": del_wt})
                    elif use_dtdc and "DTDC" in text:
                        awb = re.search(r"([A-Z][0-9]{10})", text)
                        pin = re.search(r"(\d{6})", text)
                        all_data.append({"Client": dtdc_id, "AWB": awb.group(1) if awb else "", "Pincode": pin.group(1) if pin else "", "Weight": dtdc_wt})
        if all_data:
            df = pd.DataFrame(all_data)
            st.dataframe(df, use_container_width=True)
            output = BytesIO(); df.to_excel(output, index=False)
            st.download_button("📥 Download Excel", output.getvalue(), "VayuVega_Data.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# ⚖️ VOLUMETRIC (WITH SAMPLE FILE & ACTUAL WT)
# ===============================================
elif st.session_state.page == "⚖️ VoluCalc":
    st.markdown('<h2 class="section-title">⚖️ Volumetric Calculator</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    l = c1.number_input("Length (cm)")
    w = c2.number_input("Width (cm)")
    h = c3.number_input("Height (cm)")
    act_wt = st.number_input("Actual Weight (KG)")
    div = st.selectbox("Divisor", [5000, 4500, 6000])
    if l*w*h > 0:
        vol_wt = (l*w*h)/div
        st.info(f"Chargeable Weight: {max(vol_wt, act_wt):.3f} KG")
    
    st.divider()
    st.subheader("📁 Bulk Volumetric Calculation")
    # Sample file for user
    sample_df = pd.DataFrame({'Length': [10, 20], 'Width': [10, 15], 'Height': [12, 10], 'Actual_Weight': [0.5, 1.5]})
    sample_out = BytesIO(); sample_df.to_excel(sample_out, index=False)
    st.download_button("📥 Download Sample Format", sample_out.getvalue(), "Sample_Format.xlsx")
    
    bulk = st.file_uploader("Upload Excel", type=['xlsx'])
    if bulk:
        df_b = pd.read_excel(bulk)
        df_b['Vol_Weight'] = (df_b['Length'] * df_b['Width'] * df_b['Height']) / div
        df_b['Final_Weight'] = df_b[['Vol_Weight', 'Actual_Weight']].max(axis=1)
        st.dataframe(df_b)
        out_b = BytesIO(); df_b.to_excel(out_b, index=False)
        st.download_button("Download Results", out_b.getvalue(), "Bulk_Results.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# ✏️ PDF EDITOR (FIXED: AMT + WT)
# ===============================================
elif st.session_state.page == "✏️ PDF Editor":
    st.markdown('<h2 class="section-title">✏️ Smart PDF Label Editor</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    ctype = st.radio("Select Courier:", ["DTDC", "Delhivery"], horizontal=True)
    up_files = st.file_uploader("Upload Labels", type=['pdf'], accept_multiple_files=True)
    if up_files:
        for f in up_files:
            st.write(f"Editing: {f.name}")
            col_a, col_w = st.columns(2)
            n_amt = col_a.text_input("New Amount:", key=f"a_{f.name}")
            n_wt = col_w.text_input("New Weight:", key=f"w_{f.name}")
            if st.button(f"Update & Download {f.name}"):
                doc = fitz.open(stream=f.read(), filetype="pdf")
                for page in doc:
                    if ctype == "DTDC":
                        page.add_redact_annot(fitz.Rect(100, 480, 260, 515), fill=(1,1,1))
                        page.apply_redactions()
                        page.insert_text((75, 505), f"Rs. {n_amt}", fontsize=20, color=(0,0,0))
                        w_hit = page.search_for("Weight")
                        if w_hit:
                            page.add_redact_annot(fitz.Rect(w_hit[0].x1+5, w_hit[0].y0-2, 450, w_hit[0].y1+2), fill=(1,1,1))
                            page.apply_redactions()
                            page.insert_text((w_hit[0].x1+10, w_hit[0].y1-5), f": {n_wt} KG", fontsize=14, color=(0,0,0))
                    else: # Delhivery
                        p_hit = page.search_for("Product")
                        if p_hit:
                            sx, ay = p_hit[0].x0+2, p_hit[0].y1+18
                            page.add_redact_annot(fitz.Rect(sx, ay-12, sx+200, ay+30), fill=(1,1,1))
                            page.apply_redactions()
                            page.insert_text((sx, ay), f"Rs. {n_amt}", fontsize=12, color=(0,0,0))
                            page.insert_text((sx, ay+15), f"Weight: {n_wt} KG", fontsize=12, color=(0,0,0))
                res = BytesIO(); doc.save(res)
                st.download_button(f"📥 Download Fixed_{f.name}", res.getvalue(), f"Fixed_{f.name}")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# 📸 IMAGE OCR (WORKING)
# ===============================================
elif st.session_state.page == "📸 Image OCR":
    st.markdown('<h2 class="section-title">📸 Image to Text (OCR)</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    img_f = st.file_uploader("Upload Image", type=['png','jpg','jpeg'])
    if img_f:
        img = Image.open(img_f)
        st.image(img, width=400)
        if st.button("🔍 Extract Text"):
            with st.spinner("AI is reading..."):
                try:
                    import easyocr
                    reader = easyocr.Reader(['en', 'te'])
                    result = reader.readtext(np.array(img), detail=0)
                    st.text_area("Extracted Text:", "\n".join(result), height=250)
                except: st.error("OCR Error. Check easyocr installation.")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# 📦 BARCODE PRO (WORKING)
# ===============================================
elif st.session_state.page == "📦 Barcode Pro":
    st.markdown('<h2 class="section-title">📦 Barcode Generator</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    nums = st.text_area("📝 Tracking Numbers (one per line):")
    comp = st.text_input("🏢 Company Name", value="VAYI VEGA")
    if st.button("Generate Label PDF"):
        tracking_list = [n.strip() for n in nums.split('\n') if n.strip()]
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        for num in tracking_list:
            code_class = barcode.get_barcode_class('code128')
            my_barcode = code_class(num, writer=ImageWriter())
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                img_path = my_barcode.save(tmp.name.replace(".png", ""))
            c.setFont("Helvetica-Bold", 10); c.drawCentredString(150, 750, comp.upper())
            c.drawImage(img_path, 50, 650, width=200, height=80)
            c.showPage(); os.remove(img_path)
        c.save()
        st.download_button("📥 Download Labels", pdf_buffer.getvalue(), "Labels.pdf")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown('<p style="text-align:center; color:#00ffff; margin-top:50px; font-family:Orbitron;">Vaayi Vega © 2026 | Mass Neon Pro</p>', unsafe_allow_html=True)
