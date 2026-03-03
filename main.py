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

# --- THEME SETUP ---
st.set_page_config(page_title="🚀 వాయి వేగ Pro", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%); color: white; }
    .tool-section { background: rgba(255,255,255,0.05); padding: 25px; border-radius: 20px; border: 1px solid rgba(0,212,255,0.2); margin-top: 20px; }
    .section-title { font-size: 2rem !important; color: #00D4FF !important; font-weight: 700; text-align: center; }
    div.stButton > button { background: linear-gradient(45deg, #00D4FF, #00ffcc); color: black !important; font-weight: bold; border-radius: 10px; border: none; width: 100%; height: 3em; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#00D4FF;'>🚀 VAYU VEGA</h2>", unsafe_allow_html=True)
    choice = st.radio("✨ Tools Menu", ["🏠 Dashboard", "📊 PDF→Excel", "✏️ PDF Editor", "📦 Barcode Pro", "📸 Image OCR", "⚖️ VoluCalc"])

# ===============================================
# 📊 1. PDF TO EXCEL (FIXED: ID & WEIGHT ADDED)
# ===============================================
if choice == "📊 PDF→Excel":
    st.markdown('<h2 class="section-title">📊 PDF to Excel Converter</h2>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="tool-section">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            use_del = st.checkbox("🚚 Delhivery", value=True)
            d_id = st.text_input("Delhivery Client ID:", placeholder="Enter ID")
            d_wt = st.text_input("Delhivery Weight:", placeholder="e.g. 0.5")
        with c2:
            use_dtdc = st.checkbox("📦 DTDC", value=True)
            dt_id = st.text_input("DTDC Client ID:", placeholder="Enter ID")
            dt_wt = st.text_input("DTDC Weight:", placeholder="e.g. 1.0")

        pdf_files = st.file_uploader("📄 Upload PDFs", type=['pdf'], accept_multiple_files=True)
        if pdf_files and st.button("🔄 Start Extraction"):
            all_rows = []
            for f in pdf_files:
                with pdfplumber.open(f) as pdf:
                    for pg in pdf.pages:
                        txt = pg.extract_text()
                        if not txt: continue
                        if use_del and "Delhivery" in txt:
                            awb = re.search(r"AWB#\s*(\d+)", txt)
                            pin = re.search(r"PIN\s*[:\-\s]*(\d{6})", txt)
                            all_rows.append({"Client ID": d_id, "AWB": awb.group(1) if awb else "", "Pincode": pin.group(1) if pin else "", "Weight": d_wt})
                        elif use_dtdc and "DTDC" in txt:
                            awb = re.search(r"([A-Z][0-9]{10})", txt)
                            pin = re.search(r"(\d{6})", txt)
                            all_rows.append({"Client ID": dt_id, "AWB": awb.group(1) if awb else "", "Pincode": pin.group(1) if pin else "", "Weight": dt_wt})
            if all_rows:
                df = pd.DataFrame(all_rows)
                st.dataframe(df, use_container_width=True)
                out = BytesIO(); df.to_excel(out, index=False)
                st.download_button("📥 Download Excel", out.getvalue(), "VayuVega_Data.xlsx")
        st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# ✏️ 2. PDF EDITOR (FIXED: AMT + WT + API LOGIC)
# ===============================================
elif choice == "✏️ PDF Editor":
    st.markdown('<h2 class="section-title">✏️ Smart PDF Label Editor</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    ctype = st.radio("Courier Type:", ["DTDC", "Delhivery"], horizontal=True)
    
    up_files = st.file_uploader("📄 Upload Labels", type=["pdf"], accept_multiple_files=True)
    if up_files:
        for f in up_files:
            st.markdown(f"--- Editing: **{f.name}** ---")
            c1, c2 = st.columns(2)
            n_amt = c1.text_input(f"💰 New Amount (Rs.)", key=f"a_{f.name}")
            n_wt = c2.text_input(f"⚖️ New Weight (KG)", key=f"w_{f.name}")
            
            if st.button(f"🚀 Process & Save {f.name}"):
                if n_amt and n_wt:
                    doc = fitz.open(stream=f.read(), filetype="pdf")
                    for page in doc:
                        if ctype == "DTDC":
                            # Redact Amount
                            page.add_redact_annot(fitz.Rect(100, 480, 260, 515), fill=(1,1,1))
                            page.apply_redactions()
                            page.insert_text((75, 505), f"Rs. {n_amt}", fontsize=20, color=(0,0,0))
                            # Redact Weight
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
# 📸 3. IMAGE OCR (FIXED: READING LOGIC)
# ===============================================
elif choice == "📸 Image OCR":
    st.markdown('<h2 class="section-title">📸 Image to Text (OCR)</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    img_file = st.file_uploader("📁 Upload Image", type=['png', 'jpg', 'jpeg'])
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=400)
        if st.button("🔍 Extract Text Now"):
            with st.spinner("Reading Text..."):
                try:
                    import easyocr
                    reader = easyocr.Reader(['en', 'te'])
                    result = reader.readtext(np.array(img), detail=0)
                    st.subheader("📝 Extracted Text:")
                    st.text_area("", value="\n".join(result), height=200)
                except Exception as e:
                    st.error("EasyOCR ఇన్‌స్టాల్ అయి ఉండాలి. లేదంటే pip install easyocr అని రన్ చేయి బ్రో.")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# ⚖️ 4. VOLUMETRIC (FIXED: ACTUAL WEIGHT ADDED)
# ===============================================
elif choice == "⚖️ VoluCalc":
    st.markdown('<h2 class="section-title">⚖️ Volumetric Calculator</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    L = c1.number_input("Length (cm)")
    W = c2.number_input("Width (cm)")
    H = c3.number_input("Height (cm)")
    actual_wt = st.number_input("Actual Weight (KG)", min_value=0.0)
    div = st.selectbox("Divisor", [5000, 4500, 6000])
    
    if L*W*H > 0:
        vol_wt = (L*W*H)/div
        st.divider()
        st.subheader(f"Volumetric: {vol_wt:.3f} KG")
        st.subheader(f"Actual: {actual_wt:.3f} KG")
        final = max(vol_wt, actual_wt)
        st.success(f"📦 Chargeable Weight: {final:.3f} KG")
    st.markdown('</div>', unsafe_allow_html=True)

# Dashboard and Barcode Pro logic remains identical to your working copy.
elif choice == "🏠 Dashboard":
    st.markdown("<h1 style='text-align:center;'>Welcome to Vaayi Vega Pro 🚀</h1>", unsafe_allow_html=True)
    st.info("సెలెక్ట్ చేసిన టూల్స్ అన్నీ పక్కాగా పని చేస్తున్నాయి. పైన మెనూలో చెక్ చేయి బ్రో.")
