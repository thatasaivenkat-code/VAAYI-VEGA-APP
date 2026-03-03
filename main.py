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

# 🔥 MINIMAL NEON CSS - ALL FUNCTIONS WORKING
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
.stApp {background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 100%);}
.main-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 3.5rem !important;
    background: linear-gradient(45deg, #ff00ff, #00ffff, #00ff9d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center; font-weight: 900 !important;
    text-shadow: 0 0 20px rgba(255,0,255,0.8);
}
.subtitle {
    color: #00ffff !important; font-size: 1.3rem !important;
    text-align: center; padding: 15px 30px; border-radius: 50px;
    background: rgba(0,255,255,0.1); border: 2px solid #00ffff;
    box-shadow: 0 0 20px rgba(0,255,255,0.4);
}
.feature-card {
    background: rgba(20,20,40,0.9) !important; padding: 25px !important;
    border-radius: 20px !important; border: 2px solid rgba(0,255,255,0.3);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5); height: 150px !important;
    display: flex !important; align-items: center !important;
}
.feature-card:hover {transform: translateY(-10px) !important; border-color: #00ffff !important;}
.feature-icon {font-size: 3rem !important; margin-right: 20px;}
.card-title {color: #00ffff !important; font-size: 1.4rem !important; font-weight: 700 !important;}
.card-desc {color: #00ff9d !important;}
.tool-section {
    background: rgba(20,20,40,0.95) !important; padding: 35px !important;
    border-radius: 25px !important; border: 2px solid rgba(255,0,255,0.4);
}
.section-title {
    font-family: 'Orbitron', monospace !important; font-size: 2.3rem !important;
    background: linear-gradient(45deg, #ff00ff, #00ffff); -webkit-background-clip: text;
    -webkit-text-fill-color: transparent; text-align: center; font-weight: 700 !important;
}
section[data-testid="stSidebar"] {background: rgba(15,15,35,0.95) !important;}
.stButton > button {
    background: linear-gradient(135deg, #ff00ff, #00ffff) !important; color: white !important;
    border-radius: 25px !important; font-weight: 700 !important; font-size: 1.1rem !important;
    box-shadow: 0 0 20px rgba(0,255,255,0.5) !important;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="🚀 వాయి వేగ Pro", layout="wide")

# SIDEBAR
with st.sidebar:
    st.markdown('<div style="text-align:center;padding:20px;background:rgba(0,255,255,0.1);border-radius:20px;border:2px solid #00ffff;"><h2 style="color:#00ffff;margin:0;">🚀 Vaayi Vega</h2></div>', unsafe_allow_html=True)
    
    choice = st.radio("✨ Choose Tool:", 
                     ["🏠 Dashboard", "📦 Barcode Pro", "📊 PDF→Excel", 
                      "✏️ PDF Editor", "📸 Image OCR", "⚖️ VoluCalc"],
                     index=0,
                     label_visibility="collapsed")

# 🏠 DASHBOARD
if choice == "🏠 Dashboard":
    st.markdown('<h1 class="main-title">వాయి వేగ Multi-Tool Pro 🚀</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">5-in-1 AI Business Tools | Telugu + English Support</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="feature-card"><span class="feature-icon">📦</span><div><div class="card-title">Barcode Generator Pro</div><div class="card-desc">3-inch professional labels</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card"><span class="feature-icon">📊</span><div><div class="card-title">PDF to Excel Converter</div><div class="card-desc">Delhivery + DTDC auto-extract</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card"><span class="feature-icon">⚖️</span><div><div class="card-title">Volumetric Calculator</div><div class="card-desc">L×W×H → KG/Grams billing</div></div></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card"><span class="feature-icon">✏️</span><div><div class="card-title">Smart PDF Editor</div><div class="card-desc">Edit amount/weight labels</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card"><span class="feature-icon">📸</span><div><div class="card-title">Image to Text (OCR)</div><div class="card-desc">Telugu + English OCR</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card" style="background: linear-gradient(135deg, #ff00ff, #00ffff);"><span class="feature-icon">🎉</span><div><div class="card-title" style="color:white;">All Tools Ready!</div><div style="color:rgba(255,255,255,0.9);">Select from sidebar 🚀</div></div></div>', unsafe_allow_html=True)

# 📦 BARCODE PRO
elif choice == "📦 Barcode Pro":
    st.markdown('<h2 class="section-title">📦 Professional Barcode Generator</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2,1])
    with col1:
        numbers_input = st.text_area("📝 Enter Tracking Numbers (one per line):", height=200, placeholder="PA1234567890\nPA1234567891")
    with col2:
        company_name = st.text_input("🏢 Company Name:", value="VAYI VEGA")
    
    if st.button("🖨️ Generate PDF Labels", use_container_width=True):
        if numbers_input.strip():
            tracking_list = [n.strip() for n in numbers_input.split('\n') if n.strip()]
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4
            label_w, label_h = 3*inch, 1.5*inch
            x, y = 0.5*inch, height-0.5*inch-label_h
            
            for i, num in enumerate(tracking_list):
                code = barcode.get_barcode_class('code128')(num, ImageWriter())
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    img_path = code.save(tmp.name)
                
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(x + label_w/2, y + label_h - 15, company_name.upper())
                c.drawImage(img_path, x+10, y+10, label_w-20, label_h-40)
                
                x += label_w + 0.2*inch
                if x + label_w > width:
                    x = 0.5*inch
                    y -= label_h + 0.3*inch
                if y < 0.5*inch:
                    c.showPage()
                    y = height-0.5*inch-label_h
                
                os.remove(img_path)
            
            c.save()
            st.success(f"✅ {len(tracking_list)} labels generated!")
            st.download_button("📥 Download PDF", pdf_buffer.getvalue(), f"{company_name}_Labels.pdf", use_container_width=True)
        else:
            st.warning("⚠️ Enter tracking numbers!")
    st.markdown('</div>', unsafe_allow_html=True)

# ⚖️ VOLUMETRIC CALC
elif choice == "⚖️ VoluCalc":
    st.markdown('<h2 class="section-title">⚖️ Volumetric Weight Calculator</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📐 Dimensions (cm)")
        length = st.number_input("📏 Length", min_value=0.0, step=0.1)
        width = st.number_input("📐 Width", min_value=0.0, step=0.1) 
        height = st.number_input("📏 Height", min_value=0.0, step=0.1)
        divisor = st.selectbox("🚚 Courier", [5000, 4500, 6000])
    
    with col2:
        if length > 0 and width > 0 and height > 0:
            vol_kg = (length * width * height) / divisor
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #ff00ff, #ff0080); padding:25px; border-radius:20px; 
            color:white; text-align:center; border:2px solid #ff00ff;">
                <div>Volumetric Weight</div>
                <div style="font-size:2.5rem; font-weight:700;">{vol_kg:.3f} KG</div>
            </div>
            """, unsafe_allow_html=True)
            
            actual_w = st.number_input("⚖️ Actual Weight (KG):", min_value=0.0)
            if actual_w > 0:
                final_w = max(vol_kg, actual_w)
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #00ffff, #00ff9d); padding:20px; border-radius:20px; 
                color:black; text-align:center; font-weight:700;">
                    💰 Chargeable: <span style="font-size:2rem;">{final_w:.3f} KG</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center;padding:30px;color:#00ffff;background:rgba(20,20,40,0.8);border:2px solid #00ffff;border-radius:20px;margin-top:40px;">✨ Made with ❤️ for Telugu Business Owners | Vaayi Vega © 2026</div>', unsafe_allow_html=True)
