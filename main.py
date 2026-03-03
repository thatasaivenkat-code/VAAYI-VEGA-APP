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

# 🔥 PERFECT NEON CSS - NO ERRORS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Poppins:wght@300;400;600&display=swap');
* {font-family: 'Poppins', sans-serif !important;}
.stApp {background: #0a0a0a; min-height: 100vh;}
.main-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 3.5rem !important;
    background: linear-gradient(45deg, #ff00ff, #00ffff, #00ff9d);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin: 20px 0;
    animation: neonGlow 2s ease-in-out infinite alternate;
    text-shadow: 0 0 20px rgba(255,0,255,0.8), 0 0 40px rgba(0,255,255,0.6);
    font-weight: 900 !important;
    letter-spacing: 2px;
}
@keyframes neonGlow {
    from {filter: drop-shadow(0 0 10px #ff00ff);}
    to {filter: drop-shadow(0 0 20px #00ffff);}
}
.subtitle {
    font-size: 1.3rem !important;
    color: #00ffff;
    text-align: center;
    padding: 15px 30px;
    border-radius: 50px;
    background: rgba(0,255,255,0.1);
    border: 2px solid #00ffff;
    box-shadow: 0 0 20px rgba(0,255,255,0.4);
    margin: 30px 0;
    font-weight: 600;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% {box-shadow: 0 0 20px rgba(0,255,255,0.4);}
    50% {box-shadow: 0 0 30px rgba(255,0,255,0.6);}
}
.feature-card {
    background: rgba(20,20,40,0.9) !important;
    padding: 25px !important;
    border-radius: 20px !important;
    margin: 15px 0 !important;
    border: 2px solid rgba(0,255,255,0.3);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(0,255,255,0.2);
    transition: all 0.4s ease !important;
    height: 150px !important;
    display: flex !important;
    align-items: center !important;
}
.feature-card:hover {
    transform: translateY(-10px) !important;
    border-color: #00ffff !important;
    box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 40px rgba(0,255,255,0.6) !important;
}
.feature-icon {font-size: 3rem !important; margin-right: 20px; filter: drop-shadow(0 0 10px #00ffff);}
.card-title {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #00ffff !important;
    margin-bottom: 8px !important;
}
.card-desc {color: #00ff9d !important; font-size: 1rem !important;}
.tool-section {
    background: rgba(20,20,40,0.95) !important;
    padding: 35px !important;
    border-radius: 25px !important;
    margin: 20px 0 !important;
    border: 2px solid rgba(255,0,255,0.4);
    box-shadow: 0 20px 50px rgba(0,0,0,0.6), 0 0 30px rgba(255,0,255,0.3);
}
.section-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 2.3rem !important;
    background: linear-gradient(45deg, #ff00ff, #00ffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 25px !important;
    font-weight: 700 !important;
    text-shadow: 0 0 20px rgba(255,0,255,0.6);
}
section[data-testid="stSidebar"] {
    background: rgba(15,15,35,0.95) !important;
    border-right: 2px solid #00ffff !important;
    box-shadow: 5px 0 30px rgba(0,255,255,0.3) !important;
}
section[data-testid="stSidebar"] div > label {
    color: #00ffff !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #ff00ff, #00ffff) !important;
    color: white !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 12px 30px !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    box-shadow: 0 0 20px rgba(0,255,255,0.5) !important;
    font-family: 'Orbitron', monospace !important;
}
.stButton > button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 0 30px rgba(0,255,255,0.8) !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(20,20,40,0.8) !important;
    color: #00ffff !important;
    border: 2px solid rgba(0,255,255,0.3) !important;
    border-radius: 10px !important;
}
.stTextInput > label, .stNumberInput > label {
    color: #00ff9d !important;
    font-weight: 600 !important;
}
.stSuccess {border: 2px solid #00ff9d !important; background: rgba(0,255,157,0.1) !important;}
.stError {border: 2px solid #ff0066 !important; background: rgba(255,0,102,0.1) !important;}
.stWarning {border: 2px solid #ffc800 !important; background: rgba(255,200,0,0.1) !important;}
</style>
""", unsafe_allow_html=True)

# --- PAGE CONFIG ---
st.set_page_config(page_title="🚀 వాయి వేగ Pro", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div style="text-align:center;padding:20px;background:rgba(0,255,255,0.1);border-radius:20px;border:2px solid #00ffff;box-shadow:0 0 20px rgba(0,255,255,0.4);"><h2 style="color:#00ffff;margin:0;font-family:Orbitron,sans-serif;font-size:1.5rem;">🚀 Vaayi Vega</h2></div>', unsafe_allow_html=True)
    
    choice = st.radio("✨ Choose Tool:", 
                     ["🏠 Dashboard", "📦 Barcode Pro", "📊 PDF→Excel", 
                      "✏️ PDF Editor", "📸 Image OCR", "⚖️ VoluCalc"],
                     index=0,
                     label_visibility="collapsed")

# ===============================================
# 🏠 HOME DASHBOARD
# ===============================================
if choice == "🏠 Dashboard":
    st.markdown('<h1 class="main-title">వాయి వేగ Multi-Tool Pro 🚀</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">5-in-1 AI Business Tools | Telugu + English Support</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📦</span>
            <div>
                <div class="card-title">Barcode Generator Pro</div>
                <div class="card-desc">3-inch professional labels with company branding.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div>
                <div class="card-title">PDF to Excel Converter</div>
                <div class="card-desc">Delhivery + DTDC PDFs → Excel auto-extract.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">⚖️</span>
            <div>
                <div class="card-title">Volumetric Calculator</div>
                <div class="card-desc">L×W×H → KG/Grams with billing weight.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">✏️</span>
            <div>
                <div class="card-title">Smart PDF Editor</div>
                <div class="card-desc">Edit amount/weight on existing labels.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📸</span>
            <div>
                <div class="card-title">Image to Text (OCR)</div>
                <div class="card-desc">Telugu + English. Camera + Upload support.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card" style="background: linear-gradient(135deg, #ff00ff, #00ffff) !important; color:white !important;">
            <span class="feature-icon">🎉</span>
            <div>
                <div class="card-title" style="color:white !important;">All Tools Ready!</div>
                <div class="card-desc" style="color:rgba(255,255,255,0.9) !important;">Select from sidebar to start 🚀</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ===============================================
# REST OF YOUR CODE (Same as before - no changes needed)
# ===============================================
elif choice == "📦 Barcode Pro":
    st.markdown('<h2 class="section-title">📦 Professional Barcode Generator</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2,1])
    with col1:
        numbers_input = st.text_area("📝 Enter Tracking Numbers (one per line):", 
                                   height=200, 
                                   placeholder="PA1234567890\nPA1234567891\nPA1234567892")
    with col2:
        company_name = st.text_input("🏢 Company Name:", value="VAYI VEGA")
    
    # ... rest of barcode code (same as before)

# Add all other sections exactly as they were before...
# (PDF→Excel, PDF Editor, OCR, VoluCalc - NO CHANGES NEEDED)

st.markdown("""
<div style="text-align:center;padding:30px;color:#00ffff;font-size:1.1rem;margin-top:40px;
            background:rgba(20,20,40,0.8);border:2px solid #00ffff;border-radius:20px;
            box-shadow:0 0 30px rgba(0,255,255,0.3);">
    ✨ Made with ❤️ for Telugu Business Owners | Vaayi Vega © 2026
</div>
""", unsafe_allow_html=True)
