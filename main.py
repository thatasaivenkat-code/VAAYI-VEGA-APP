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

# --- UTILITY FUNCTIONS FOR REFERENCE EXTRACTOR ---
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

# --- PAGE CONFIG ---
st.set_page_config(page_title="వాయి వేగ Pro", layout="wide", page_icon="🚀")

# --- CUSTOM CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.main-title { font-size: 3.5rem !important; background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700 !important; text-align: center; }
.card { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 25px; margin: 15px 0; box-shadow: 0 15px 35px rgba(0,0,0,0.1); color: #2c3e50; }
.metric-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; text-align: center; border-radius: 12px; padding: 1rem; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR MENU ---
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
    st.markdown('<div class="card" style="text-align:center;"><h3>Welcome to All-in-One Logistics Suite</h3><p>Select a tool from the sidebar to begin.</p></div>', unsafe_allow_html=True)

# ===============================================
# 📂 PDF EXTRACTOR (NEW LOGIC)
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
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Groups", len(grouped_pages))
        c2.metric("Skips", len(skip_details))
        
        if grouped_pages:
            cols = st.columns(3)
            for i, (gid, pages) in enumerate(sorted(grouped_pages.items())):
                with cols[i % 3]:
                    writer = PdfWriter()
                    for p in pages: writer.add_page(p)
                    bio = io.BytesIO(); writer.write(bio)
                    st.download_button(f"📥 Group-{gid} ({len(pages)}p)", bio.getvalue(), f"Group_{gid}_{now}.pdf", use_container_width=True)

# ===============================================
# 📊 PDF TO EXCEL
# ===============================================
elif choice == "📊 PDF→Excel":
    st.markdown('<h2 style="color:white;">📊 PDF to Excel Converter</h2>', unsafe_allow_html=True)
    # ... [Excel Extract Logic here as in your previous code] ...
    st.info("Upload Delhivery/DTDC labels to extract data to Excel.")
    # (Rest of Excel logic from your main code)

# ===============================================
# 📦 BARCODE GENERATOR
# ===============================================
elif choice == "📦 Barcode Pro":
    st.markdown('<h2 style="color:white;">📦 Barcode Generator</h2>', unsafe_allow_html=True)
    # ... [Barcode Logic from your first code] ...

# ===============================================
# ✏️ PDF EDITOR
# ===============================================
elif choice == "✏️ PDF Editor":
    st.markdown('<h2 style="color:white;">✏️ Smart PDF Label Editor</h2>', unsafe_allow_html=True)
    # ... [PDF Edit Logic from your first code] ...

# ===============================================
# 📸 IMAGE OCR
# ===============================================
elif choice == "📸 Image OCR":
    st.markdown('<h2 style="color:white;">📸 Image to Text (OCR)</h2>', unsafe_allow_html=True)
    # ... [OCR Logic with easyocr from your first code] ...

# ===============================================
# ⚖️ VOLUMETRIC CALCULATOR
# ===============================================
elif choice == "⚖️ VoluCalc":
    st.markdown('<h2 style="color:white;">⚖️ Volumetric Weight Calculator</h2>', unsafe_allow_html=True)
    # ... [VoluCalc Logic from your first code] ...

st.markdown('<div style="text-align:center; color:white; margin-top:50px;">Vaayi Vega © 2026</div>', unsafe_allow_html=True)
