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
import io
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

# --- 1. UTILITY FUNCTIONS (PDF EXTRACTOR LOGIC) ---
def extract_full_ref(text):
    patterns = [
        r'\b19-\d{10}\b', r'\d+-\d{10}\b', r'[A-Z][\d+]+\+\d+', 
        r'[D][\d+]+\+\d+', r'\b\d+\+\d+\b', r'No\s*\d+',
        r'Ref\.\s*No:\s*[A-Z]?\d+\+\d+', r'\b\d{2}-\d+\b',
        r'\b[A-Z]\d{8,13}\b', r'\b\d{12,14}\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match: return match.group(0)
    return None

def normalize_ref(ref_text): return re.sub(r'\s+', '', ref_text).lower().strip()
def get_group_id(ref_text): 
    match = re.search(r'[A-Z]?(\d+)', ref_text)
    return match.group(1)[:2] if match else None
def validate_ref(ref_text):
    patterns = [r'\d+-\d+', r'[A-Z]?\d+\+\d+', r'No\d+', r'\b[A-Z]?\d{8,}\b']
    return any(re.search(p, ref_text, re.I) for p in patterns)

# --- 2. PAGE CONFIG & CSS ---
st.set_page_config(page_title="వాయి వేగ Pro", layout="wide", page_icon="🚀")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.main-title { font-size: 3.5rem !important; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700 !important; text-align: center; }
.card { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 25px; margin: 15px 0; color: #2c3e50; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown('<h2 style="color:white; text-align:center;">🚀 Vaayi Vega</h2>', unsafe_allow_html=True)
    choice = st.radio("✨ Choose Tool:", 
                      ["🏠 Dashboard", "📂 PDF Extractor", "📦 Barcode Pro", "📊 PDF→Excel", "✏️ PDF Editor", "📸 Image OCR", "⚖️ VoluCalc"])

now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

# ===============================================
# 🏠 DASHBOARD
# ===============================================
if choice == "🏠 Dashboard":
    st.markdown('<h1 class="main-title">వాయి వేగ Multi-Tool Pro 🚀</h1>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="text-align:center;"><h3>Welcome T Venkanna Babu!</h3><p>Select any tool from the sidebar to start your work.</p></div>', unsafe_allow_html=True)

# ===============================================
# 📂 PDF EXTRACTOR (With Skip Option)
# ===============================================
elif choice == "📂 PDF Extractor":
    st.markdown('<h2 style="color:white;">📂 PDF Reference Extractor</h2>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Drop PDFs here", type=['pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        grouped_pages = {}; no_id_pages = PdfWriter(); skip_details = []; all_seen_refs = set()
        for file in uploaded_files:
            file.seek(0); bytes_io = io.BytesIO(file.read())
            reader = PdfReader(bytes_io)
            pdf_seen_refs = set()
            with pdfplumber.open(bytes_io) as pdf:
                for p_idx, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    ref = extract_full_ref(text)
                    if ref:
                        norm_ref = normalize_ref(ref)
                        if norm_ref in pdf_seen_refs or norm_ref in all_seen_refs:
                            skip_details.append(f"{file.name}(p{p_idx+1}): {ref}")
                            continue
                        pdf_seen_refs.add(norm_ref); all_seen_refs.add(norm_ref)
                        gid = get_group_id(ref)
                        if gid and validate_ref(ref):
                            grouped_pages.setdefault(gid, []).append(reader.pages[p_idx])
                        else: no_id_pages.add_page(reader.pages[p_idx])
        
        c1, c2 = st.columns(2)
        c1.metric("📊 Groups Found", len(grouped_pages))
        c2.metric("⏭️ Skips (Duplicates)", len(skip_details))
        
        if grouped_pages:
            st.write("### 📂 Group Downloads")
            cols = st.columns(3)
            for i, (gid, pages) in enumerate(sorted(grouped_pages.items())):
                with cols[i % 3]:
                    writer = PdfWriter()
                    for p in pages: writer.add_page(p)
                    bio = io.BytesIO(); writer.write(bio)
                    st.download_button(f"📥 Group-{gid} ({len(pages)}p)", bio.getvalue(), f"Group_{gid}_{now}.pdf", use_container_width=True)
        
        if skip_details:
            st.warning(f"Found {len(skip_details)} duplicates. You can download the skip list below.")
            st.download_button("📥 Download Skip List (TXT)", "\n".join(skip_details), f"Skips_{now}.txt")

# ===============================================
# 📦 BARCODE PRO
# ===============================================
elif choice == "📦 Barcode Pro":
    st.markdown('<h2 style="color:white;">📦 Barcode Generator</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1: numbers = st.text_area("Enter Tracking Numbers (Line by line):")
    with col2: company = st.text_input("Company Name:", value="VAYI VEGA")
    
    if st.button("Generate Barcodes"):
        if numbers:
            tracking_list = [n.strip() for n in numbers.split('\n') if n.strip()]
            pdf_buf = BytesIO(); c = canvas.Canvas(pdf_buf, pagesize=A4)
            # Simple label logic
            for num in tracking_list:
                code128 = barcode.get_barcode_class('code128')
                my_bc = code128(num, writer=ImageWriter())
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                my_bc.save(tmp.name.replace(".png", ""))
                c.drawString(100, 750, company)
                c.drawImage(tmp.name, 100, 650, width=200, height=80)
                c.showPage()
            c.save()
            st.download_button("📥 Download Barcodes", pdf_buf.getvalue(), "labels.pdf")

# ===============================================
# 📊 PDF→EXCEL (Delhivery/DTDC Extract)
# ===============================================
elif choice == "📊 PDF→Excel":
    st.markdown('<h2 style="color:white;">📊 PDF to Excel Converter</h2>', unsafe_allow_html=True)
    uploaded_excel_pdfs = st.file_uploader("Upload Labels for Excel", type=['pdf'], accept_multiple_files=True)
    if uploaded_excel_pdfs:
        rows = []
        for pf in uploaded_excel_pdfs:
            with pdfplumber.open(pf) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text() or ""
                    awb = re.search(r"AWB#\s*(\d+)", txt)
                    pin = re.search(r"PIN\s*(\d{6})", txt)
                    if awb: rows.append({"AWB": awb.group(1), "Pincode": pin.group(1) if pin else ""})
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)
            out = BytesIO()
            df.to_excel(out, index=False)
            st.download_button("📥 Download Excel", out.getvalue(), "extracted_data.xlsx")

# ===============================================
# ✏️ PDF EDITOR
# ===============================================
elif choice == "✏️ PDF Editor":
    st.markdown('<h2 style="color:white;">✏️ PDF Label Editor</h2>', unsafe_allow_html=True)
    up_edit = st.file_uploader("Upload PDF to Edit", type=['pdf'])
    amt = st.text_input("New Amount:")
    if up_edit and amt and st.button("Update PDF"):
        doc = fitz.open(stream=up_edit.read(), filetype="pdf")
        for page in doc:
            page.insert_text((100, 100), f"Revised Amt: {amt}", fontsize=12, color=(1,0,0))
        res = BytesIO(); doc.save(res)
        st.download_button("📥 Download Edited PDF", res.getvalue(), "edited.pdf")

# ===============================================
# 📸 IMAGE OCR
# ===============================================
elif choice == "📸 Image OCR":
    st.markdown('<h2 style="color:white;">📸 Image to Text (OCR)</h2>', unsafe_allow_html=True)
    img_file = st.file_uploader("Upload Image", type=['png','jpg','jpeg'])
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=300)
        if st.button("Extract Text"):
            import easyocr
            reader = easyocr.Reader(['en', 'te'])
            result = reader.readtext(np.array(img), detail=0)
            st.text_area("Extracted Text:", "\n".join(result))

# ===============================================
# ⚖️ VOLUMETRIC CALCULATOR
# ===============================================
elif choice == "⚖️ VoluCalc":
    st.markdown('<h2 style="color:white;">⚖️ Volumetric Weight Calculator</h2>', unsafe_allow_html=True)
    l = st.number_input("Length (cm)")
    w = st.number_input("Width (cm)")
    h = st.number_input("Height (cm)")
    if l > 0 and w > 0 and h > 0:
        res = (l * w * h) / 5000
        st.success(f"Volumetric Weight: {res:.2f} KG")

st.markdown('<div style="text-align:center; color:white; margin-top:50px;">Vaayi Vega © 2026</div>', unsafe_allow_html=True)
