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
st.set_page_config(page_title="🚀 వాయి వేగ Pro", layout="wide", initial_sidebar_state="expanded")

# --- NAVIGATION LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

def go_to_page(name):
    st.session_state.page = name
    # st.rerun() # No need to manual rerun if we handle via state

# --- MASS DARK THEME CSS ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
html, body, [class*="css"]  {{ font-family: 'Poppins', sans-serif !important; }}
.stApp {{ background-color: #0E1117; color: #E0E0E0; }}

/* Mass Neon Titles */
.main-title {{
    font-size: 3.5rem !important;
    color: #00D4FF;
    text-shadow: 0 0 15px #00D4FF55;
    font-weight: 800 !important;
    text-align: center;
    margin-bottom: 5px;
}}

/* Custom Mass Cards */
.card-box {{
    background: #161B22;
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #30363D;
    text-align: center;
    transition: 0.3s ease;
    cursor: pointer;
    margin-bottom: 20px;
    min-height: 150px;
}}
.card-box:hover {{
    border: 1px solid #00D4FF;
    box-shadow: 0 0 20px #00D4FF33;
    transform: scale(1.05);
}}
.card-icon {{ font-size: 3rem; margin-bottom: 10px; }}
.card-title {{ font-size: 1.4rem; font-weight: 600; color: #00D4FF; }}

/* Tool Sections */
.tool-section {{
    background: #161B22;
    padding: 30px;
    border-radius: 20px;
    border: 1px solid #30363D;
}}

/* Side Bar Active Item */
div[data-testid="stSidebarNav"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (MANUAL SYNC) ---
with st.sidebar:
    st.markdown('<h2 style="color:#00D4FF; text-align:center;">🚀 VAAYU VEGA</h2>', unsafe_allow_html=True)
    st.markdown("---")
    choice = st.radio("Choose Tool:", 
                     ["🏠 Dashboard", "📦 Barcode Pro", "📊 PDF→Excel", 
                      "✏️ PDF Editor", "📸 Image OCR", "⚖️ VoluCalc"],
                     key="main_nav", index=["🏠 Dashboard", "📦 Barcode Pro", "📊 PDF→Excel", "✏️ PDF Editor", "📸 Image OCR", "⚖️ VoluCalc"].index(st.session_state.page))
    st.session_state.page = choice

# ===============================================
# 🏠 HOME DASHBOARD
# ===============================================
if st.session_state.page == "🏠 Dashboard":
    st.markdown('<h1 class="main-title">వాయి వేగ PRO 🚀</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#888;">Select a tool to start your work</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📦\nBarcode Pro", use_container_width=True):
            st.session_state.page = "📦 Barcode Pro"
            st.rerun()
        if st.button("✏️\nPDF Editor", use_container_width=True):
            st.session_state.page = "✏️ PDF Editor"
            st.rerun()

    with col2:
        if st.button("📊\nPDF to Excel", use_container_width=True):
            st.session_state.page = "📊 PDF→Excel"
            st.rerun()
        if st.button("📸\nImage OCR", use_container_width=True):
            st.session_state.page = "📸 Image OCR"
            st.rerun()
            
    with col3:
        if st.button("⚖️\nVoluCalc", use_container_width=True):
            st.session_state.page = "⚖️ VoluCalc"
            st.rerun()
        st.markdown("""<div style='background:#161B22; padding:15px; border-radius:10px; border:1px dashed #444; text-align:center;'>
                    <p style='color:#555;'>Ready to serve!</p></div>""", unsafe_allow_html=True)

# ===============================================
# 📊 PDF TO EXCEL (FIXED EXTRACTION)
# ===============================================
elif st.session_state.page == "📊 PDF→Excel":
    st.markdown('<h2 style="color:#00D4FF;">📊 PDF to Excel Converter</h2>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="tool-section">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            u_del = st.checkbox("Delhivery Labels", value=True)
            d_id = st.text_input("Delhivery Client ID", value="1234")
            d_wt = st.text_input("Delhivery Weight", value="0.5")
        with c2:
            u_dtdc = st.checkbox("DTDC Labels", value=True)
            dt_id = st.text_input("DTDC Client ID", value="5678")
            dt_wt = st.text_input("DTDC Weight", value="1.0")

        files = st.file_uploader("Select PDF Files", type=['pdf'], accept_multiple_files=True)
        if files and st.button("🚀 Start Convert"):
            extracted = []
            for f in files:
                with pdfplumber.open(f) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if not text: continue
                        
                        # Delhivery Check
                        if u_del and ("Delhivery" in text or "AWB#" in text):
                            awb = re.search(r"AWB#\s*(\d+)", text)
                            pin = re.search(r"PIN\s*[:\-\s]*(\d{6})", text)
                            extracted.append({"Client": d_id, "AWB": awb.group(1) if awb else "", "Pincode": pin.group(1) if pin else "", "Weight": d_wt})
                        
                        # DTDC Check
                        elif u_dtdc and ("DTDC" in text or "Ship Date" in text):
                            awb = re.search(r"([A-Z][0-9]{10})", text)
                            pin = re.search(r"(\d{6})", text)
                            extracted.append({"Client": dt_id, "AWB": awb.group(1) if awb else "", "Pincode": pin.group(1) if pin else "", "Weight": dt_wt})
            
            if extracted:
                df = pd.DataFrame(extracted)
                st.success(f"Extracted {len(extracted)} items!")
                st.dataframe(df, use_container_width=True)
                out = BytesIO()
                df.to_excel(out, index=False)
                st.download_button("📥 Download Excel", out.getvalue(), "Converted_Data.xlsx")
            else:
                st.error("No data found! Check PDF format.")
        st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# ⚖️ VOLUMETRIC (FIXED: SAMPLE & ACTUAL WEIGHT)
# ===============================================
elif st.session_state.page == "⚖️ VoluCalc":
    st.markdown('<h2 style="color:#00D4FF;">⚖️ Volumetric Calculator</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    col_in, col_res = st.columns([2, 1])
    with col_in:
        c1, c2, c3 = st.columns(3)
        L = c1.number_input("Length (cm)", min_value=0.0)
        W = c2.number_input("Width (cm)", min_value=0.0)
        H = c3.number_input("Height (cm)", min_value=0.0)
        A_WT = st.number_input("Actual Weight (KG)", min_value=0.0)
        div = st.selectbox("Divisor", [5000, 4500, 6000])

    if L*W*H > 0:
        v_wt = (L*W*H)/div
        with col_res:
            st.markdown(f"<div style='background:#00D4FF; color:#000; padding:20px; border-radius:10px; text-align:center;'><h3>{max(v_wt, A_WT):.3f} KG</h3><p>Billable Weight</p></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📁 Bulk Calculation")
    
    # Sample File Logic
    sample_data = pd.DataFrame({'Length': [10.5, 20], 'Width': [10, 15], 'Height': [12, 10], 'Actual_Weight': [0.5, 1.5]})
    sample_io = BytesIO()
    sample_data.to_excel(sample_io, index=False)
    st.download_button("📥 Download Sample Excel", sample_io.getvalue(), "Sample_Format.xlsx")
    
    bulk_f = st.file_uploader("Upload Filled Excel", type=['xlsx'])
    if bulk_f:
        df_bulk = pd.read_excel(bulk_f)
        df_bulk['Volumetric_KG'] = (df_bulk['Length'] * df_bulk['Width'] * df_bulk['Height']) / div
        df_bulk['Final_Weight'] = df_bulk[['Volumetric_KG', 'Actual_Weight']].max(axis=1)
        st.dataframe(df_bulk)
        out_bulk = BytesIO(); df_bulk.to_excel(out_bulk, index=False)
        st.download_button("📥 Download Calculated Results", out_bulk.getvalue(), "Bulk_Results.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)

# 📦 Barcode, ✏️ Editor, 📸 OCR Sections (Same as previous working versions but fixed for dark mode)
elif st.session_state.page == "📦 Barcode Pro":
    st.markdown('<h2 style="color:#00D4FF;">📦 Barcode Generator</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    nums = st.text_area("Enter Tracking Numbers:")
    comp = st.text_input("Company Name", value="VAYI VEGA")
    if st.button("Generate PDF"):
        if nums:
            tracking_list = [n.strip() for n in nums.split('\n') if n.strip()]
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4
            for num in tracking_list:
                code_class = barcode.get_barcode_class('code128')
                my_barcode = code_class(num, writer=ImageWriter())
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    img_path = my_barcode.save(tmp.name.replace(".png", ""))
                c.drawImage(img_path, 50, height-200, width=200, height=100)
                c.showPage()
                os.remove(img_path)
            c.save()
            st.download_button("Download", pdf_buffer.getvalue(), "Labels.pdf")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "✏️ PDF Editor":
    st.markdown('<h2 style="color:#00D4FF;">✏️ Label Editor</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    ctype = st.radio("Courier:", ["DTDC", "Delhivery"], horizontal=True)
    up = st.file_uploader("Upload PDFs", accept_multiple_files=True)
    if up:
        for f in up:
            c1, c2 = st.columns(2)
            amt = c1.text_input("Amount", key=f"am_{f.name}")
            wt = c2.text_input("Weight", key=f"wt_{f.name}")
            if st.button(f"Process {f.name}"):
                doc = fitz.open(stream=f.read(), filetype="pdf")
                for page in doc:
                    if ctype == "DTDC":
                        page.add_redact_annot(fitz.Rect(100, 480, 260, 515), fill=(1,1,1))
                        page.apply_redactions()
                        page.insert_text((75, 505), f"Rs. {amt}", fontsize=20, color=(0,0,0))
                res = BytesIO(); doc.save(res)
                st.download_button(f"Download Fixed_{f.name}", res.getvalue())
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "📸 Image OCR":
    st.markdown('<h2 style="color:#00D4FF;">📸 Image OCR</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    img_up = st.file_uploader("Upload Image")
    if img_up:
        img = Image.open(img_up)
        st.image(img, width=400)
        if st.button("Read Text"):
            try:
                import easyocr
                reader = easyocr.Reader(['en', 'te'])
                res = reader.readtext(np.array(img), detail=0)
                st.text_area("Result:", "\n".join(res), height=200)
            except: st.error("OCR Error. Check easyocr installation.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p style="text-align:center; color:#555; margin-top:50px;">Vaayi Vega © 2026</p>', unsafe_allow_html=True)
