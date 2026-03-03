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

# --- NAVIGATION STATE LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

def nav_to(page_name):
    st.session_state.page = page_name

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
.subtitle {{
    color: #888;
    text-align: center;
    font-size: 1.2rem;
    margin-bottom: 40px;
}}

/* Neon Cards */
.feature-card {{
    background: #161B22;
    padding: 25px;
    border-radius: 15px;
    margin: 10px 0;
    border: 1px solid #30363D;
    transition: 0.3s;
    cursor: pointer;
    display: flex;
    align-items: center;
}}
.feature-card:hover {{
    border: 1px solid #00D4FF;
    box-shadow: 0 0 20px #00D4FF33;
    transform: translateY(-5px);
}}
.card-icon {{ font-size: 2.5rem; margin-right: 20px; }}
.card-title {{ font-size: 1.3rem; font-weight: 600; color: #00D4FF; }}
.card-desc {{ color: #8B949E; font-size: 0.9rem; }}

/* Tool Sections */
.tool-section {{
    background: #161B22;
    padding: 30px;
    border-radius: 20px;
    border: 1px solid #30363D;
}}

/* Mass Buttons */
div.stButton > button {{
    background: transparent;
    color: #00D4FF;
    border: 1px solid #00D4FF;
    border-radius: 8px;
    font-weight: bold;
    transition: 0.3s;
}}
div.stButton > button:hover {{
    background: #00D4FF;
    color: #000 !important;
    box-shadow: 0 0 15px #00D4FF;
}}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<h2 style="color:#00D4FF; text-align:center;">🚀 VAAYU VEGA</h2>', unsafe_allow_html=True)
    choice = st.radio("Menu", 
                     ["🏠 Dashboard", "📦 Barcode Pro", "📊 PDF→Excel", 
                      "✏️ PDF Editor", "📸 Image OCR", "⚖️ VoluCalc"],
                     key="sidebar_nav", index=["🏠 Dashboard", "📦 Barcode Pro", "📊 PDF→Excel", "✏️ PDF Editor", "📸 Image OCR", "⚖️ VoluCalc"].index(st.session_state.page))
    st.session_state.page = choice

# ===============================================
# 🏠 HOME DASHBOARD
# ===============================================
if st.session_state.page == "🏠 Dashboard":
    st.markdown('<h1 class="main-title">వాయి వేగ PRO 🚀</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Mass Dark Business Suite | Telugu Support</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    tools = [
        {"icon": "📦", "title": "Barcode Pro", "desc": "3-inch professional labels", "id": "📦 Barcode Pro"},
        {"icon": "📊", "title": "PDF to Excel", "desc": "Extract Delhivery/DTDC data", "id": "📊 PDF→Excel"},
        {"icon": "✏️", "title": "PDF Editor", "desc": "Edit Amount & Weight on labels", "id": "✏️ PDF Editor"},
        {"icon": "📸", "title": "Image OCR", "desc": "Extract Telugu/English text", "id": "📸 Image OCR"},
        {"icon": "⚖️", "title": "VoluCalc", "desc": "L×W×H Weight Calculator", "id": "⚖️ VoluCalc"}
    ]

    for i, tool in enumerate(tools):
        with (col1 if i % 2 == 0 else col2):
            if st.button(f"{tool['icon']} {tool['title']}\n{tool['desc']}", key=f"btn_{tool['id']}", use_container_width=True):
                st.session_state.page = tool['id']
                st.rerun()

# ===============================================
# 📦 BARCODE GENERATOR
# ===============================================
elif st.session_state.page == "📦 Barcode Pro":
    st.markdown('<h2 style="color:#00D4FF;">📦 Barcode Generator Pro</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    c1, c2 = st.columns([2,1])
    nums = c1.text_area("📝 Tracking Numbers (Each line one):")
    comp = c2.text_input("🏢 Company Name:", value="VAYI VEGA")
    if st.button("Generate PDF Labels"):
        if nums:
            tracking_list = [n.strip() for n in nums.split('\n') if n.strip()]
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            w, h = A4
            lw, lh = 3 * inch, 1.5 * inch
            mx, my = 0.5 * inch, 0.5 * inch
            cx, cy = mx, h - my - lh
            for num in tracking_list:
                code_class = barcode.get_barcode_class('code128')
                my_barcode = code_class(num, writer=ImageWriter())
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    img_path = my_barcode.save(tmp.name.replace(".png", ""), options={"write_text": True, "font_size": 8})
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(cx + (lw/2), cy + lh - 15, comp.upper())
                c.drawImage(img_path, cx + 10, cy + 10, width=lw-20, height=lh-40)
                cx += lw + 0.2 * inch
                if cx + lw > w: cx = mx; cy -= lh + 0.3 * inch
                if cy < my: c.showPage(); cy = h - my - lh; cx = mx
                os.remove(img_path)
            c.save()
            st.download_button("📥 Download Labels", pdf_buffer.getvalue(), "Labels.pdf")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# 📊 PDF TO EXCEL (FIXED: CLIENT ID & WEIGHT)
# ===============================================
elif st.session_state.page == "📊 PDF→Excel":
    st.markdown('<h2 style="color:#00D4FF;">📊 PDF to Excel Converter</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        use_del = st.checkbox("Delhivery", value=True)
        d_id = st.text_input("Delhivery ID:")
        d_wt = st.text_input("Delhivery Default Weight:")
    with col2:
        use_dtdc = st.checkbox("DTDC", value=True)
        dt_id = st.text_input("DTDC ID:")
        dt_wt = st.text_input("DTDC Default Weight:")
    
    files = st.file_uploader("Upload PDFs", type=['pdf'], accept_multiple_files=True)
    if files and st.button("Convert to Excel"):
        data = []
        for f in files:
            with pdfplumber.open(f) as pdf:
                for pg in pdf.pages:
                    txt = pg.extract_text()
                    if not txt: continue
                    if use_del and "Delhivery" in txt:
                        awb = re.search(r"AWB#\s*(\d+)", txt)
                        pin = re.search(r"PIN\s*[:\-\s]*(\d{6})", txt)
                        data.append({"Client ID": d_id, "AWB": awb.group(1) if awb else "", "Pin": pin.group(1) if pin else "", "Weight": d_wt})
                    elif use_dtdc and "DTDC" in txt:
                        awb = re.search(r"([A-Z][0-9]{10})", txt)
                        pin = re.search(r"(\d{6})", txt)
                        data.append({"Client ID": dt_id, "AWB": awb.group(1) if awb else "", "Pin": pin.group(1) if pin else "", "Weight": dt_wt})
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)
            out = BytesIO(); df.to_excel(out, index=False)
            st.download_button("Download Excel", out.getvalue(), "Output.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# ✏️ PDF EDITOR (FIXED: AMT & WT)
# ===============================================
elif st.session_state.page == "✏️ PDF Editor":
    st.markdown('<h2 style="color:#00D4FF;">✏️ Smart PDF Editor</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    ctype = st.radio("Company:", ["DTDC", "Delhivery"], horizontal=True)
    up = st.file_uploader("Upload Labels", type=['pdf'], accept_multiple_files=True)
    if up:
        for f in up:
            st.write(f"Editing: {f.name}")
            c1, c2 = st.columns(2)
            n_amt = c1.text_input("New Amount (Rs.)", key=f"a_{f.name}")
            n_wt = c2.text_input("New Weight (KG)", key=f"w_{f.name}")
            if st.button(f"Process {f.name}"):
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
                    else:
                        p_hit = page.search_for("Product")
                        if p_hit:
                            sx, ay = p_hit[0].x0+2, p_hit[0].y1+18
                            page.add_redact_annot(fitz.Rect(sx, ay-12, sx+200, ay+30), fill=(1,1,1))
                            page.apply_redactions()
                            page.insert_text((sx, ay), f"Rs. {n_amt}", fontsize=12, color=(0,0,0))
                            page.insert_text((sx, ay+15), f"Weight: {n_wt} KG", fontsize=12, color=(0,0,0))
                res = BytesIO(); doc.save(res)
                st.download_button(f"Download {f.name}", res.getvalue(), f"Fixed_{f.name}")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# 📸 IMAGE OCR (FIXED)
# ===============================================
elif st.session_state.page == "📸 Image OCR":
    st.markdown('<h2 style="color:#00D4FF;">📸 Image to Text</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    img_f = st.file_uploader("Upload Image", type=['png','jpg','jpeg'])
    if img_f:
        img = Image.open(img_f)
        st.image(img, width=400)
        if st.button("Extract Text"):
            with st.spinner("AI Reading..."):
                try:
                    import easyocr
                    reader = easyocr.Reader(['en', 'te'])
                    result = reader.readtext(np.array(img), detail=0)
                    st.text_area("Extracted Text:", "\n".join(result), height=200)
                except: st.error("Please install easyocr: pip install easyocr")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# ⚖️ VOLUMETRIC (FIXED: SAMPLE DOWNLOAD & ACTUAL WT)
# ===============================================
elif st.session_state.page == "⚖️ VoluCalc":
    st.markdown('<h2 style="color:#00D4FF;">⚖️ Volumetric Weight</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    L = c1.number_input("L (cm)")
    W = c2.number_input("W (cm)")
    H = c3.number_input("H (cm)")
    A_WT = st.number_input("Actual Weight (KG)")
    div = st.selectbox("Divisor", [5000, 4500, 6000])
    if L*W*H > 0:
        v_wt = (L*W*H)/div
        st.success(f"Chargeable Weight: {max(v_wt, A_WT):.3f} KG")

    st.divider()
    st.subheader("📁 Bulk Volumetric Calculation")
    
    # Sample File Logic
    sample_df = pd.DataFrame({'Length': [10, 20], 'Width': [10, 15], 'Height': [10, 12], 'Actual_Weight': [0.5, 1.2]})
    sample_out = BytesIO()
    sample_df.to_excel(sample_out, index=False)
    st.download_button("📥 Download Sample Excel", sample_out.getvalue(), "Sample_Volu.xlsx")
    
    bulk = st.file_uploader("Upload Filled Excel", type=['xlsx'])
    if bulk:
        df_b = pd.read_excel(bulk)
        if all(x in df_b.columns for x in ['Length', 'Width', 'Height']):
            df_b['Vol_Weight'] = (df_b['Length'] * df_b['Width'] * df_b['Height']) / div
            st.dataframe(df_b)
            out_b = BytesIO(); df_b.to_excel(out_b, index=False)
            st.download_button("Download Results", out_b.getvalue(), "Results.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p style="text-align:center; color:#555; margin-top:50px;">Vaayi Vega © 2026 | Mass Edition</p>', unsafe_allow_html=True)
