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
import pytesseract

# 🔥 CLEAN NEON CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
.stApp {background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 100%);}
.main-title {
    font-family: 'Orbitron', monospace; font-size: 3rem;
    background: linear-gradient(45deg, #ff00ff, #00ffff, #00ff9d);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; font-weight: 900;
}
.tool-section {
    background: rgba(20,20,40,0.95); padding: 30px;
    border-radius: 25px; border: 2px solid rgba(255,0,255,0.4);
    margin: 20px 0;
}
.stButton > button {
    background: linear-gradient(135deg, #ff00ff, #00ffff) !important;
    color: white !important; border-radius: 25px !important;
    font-weight: 700 !important; padding: 0.5rem 2rem !important;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="🚀 వాయి వేగ Pro", layout="wide")

# SIDEBAR
with st.sidebar:
    st.markdown("### 🚀 Vaayi Vega Tools")
    choice = st.radio("Choose:", 
                     ["🏠 Home", "📦 Barcode", "📊 PDF→Excel", 
                      "✏️ PDF Edit", "📸 OCR", "⚖️ VoluCalc"],
                     index=0)

# 🏠 HOME
if choice == "🏠 Home":
    st.markdown('<h1 class="main-title">వాయి వేగ Multi-Tool 🚀</h1>', unsafe_allow_html=True)
    st.info("👈 Select tool from sidebar")

# 📦 BARCODE GENERATOR
elif choice == "📦 Barcode":
    st.markdown("## 📦 Barcode Generator (3-inch Label)")
    
    col1, col2 = st.columns([2,1])
    with col1:
        awb = st.text_input("Enter AWB Number:", placeholder="12345678")
    with col2:
        format_choice = st.selectbox("Barcode Type:", ["Code128", "Code39"])
    
    if st.button("🎯 Generate Barcode") and awb:
        try:
            barcode_class = barcode.get_barcode_class(format_choice.lower())
            barcode_instance = barcode_class(awb, writer=ImageWriter())
            
            buffer = BytesIO()
            barcode_instance.write(buffer)
            buffer.seek(0)
            
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=(3*inch, 1*inch))
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(buffer.getvalue())
                tmp_path = tmp.name
            
            c.drawImage(tmp_path, 0.1*inch, 0.1*inch, width=2.8*inch, height=0.8*inch)
            c.save()
            os.unlink(tmp_path)
            
            pdf_buffer.seek(0)
            st.success("✅ Barcode Created!")
            st.download_button("📥 Download PDF", pdf_buffer, f"barcode_{awb}.pdf", "application/pdf")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# 📊 PDF TO EXCEL
elif choice == "📊 PDF→Excel":
    st.markdown("## 📊 PDF to Excel Converter")
    st.markdown("**Supports:** Delhivery, DTDC, Standard Tables")
    
    uploaded_pdf = st.file_uploader("Upload PDF", type=['pdf'])
    
    if uploaded_pdf and st.button("🔄 Convert to Excel"):
        try:
            with pdfplumber.open(uploaded_pdf) as pdf:
                all_data = []
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            all_data.extend(table)
                
                if all_data:
                    df = pd.DataFrame(all_data[1:], columns=all_data[0])
                    
                    # Clean data
                    df = df.dropna(how='all').reset_index(drop=True)
                    
                    st.success(f"✅ Extracted {len(df)} rows!")
                    st.dataframe(df, use_container_width=True)
                    
                    # Download
                    excel_buffer = BytesIO()
                    df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        "📥 Download Excel",
                        excel_buffer,
                        f"converted_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("⚠️ No tables found in PDF")
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ✏️ PDF EDITOR
elif choice == "✏️ PDF Edit":
    st.markdown("## ✏️ Smart PDF Text Editor")
    
    uploaded_pdf = st.file_uploader("Upload PDF to Edit", type=['pdf'])
    
    if uploaded_pdf:
        pdf_bytes = uploaded_pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        st.info(f"📄 PDF has {len(doc)} pages")
        
        page_num = st.number_input("Select Page:", 1, len(doc), 1) - 1
        page = doc[page_num]
        
        # Show current text
        text_instances = page.get_text("dict")
        st.markdown("### 📝 Current Text on Page:")
        
        page_text = page.get_text()
        st.text_area("Page Content:", page_text, height=200)
        
        # Edit section
        st.markdown("### ✏️ Edit Text:")
        col1, col2 = st.columns(2)
        
        with col1:
            old_text = st.text_input("Find Text:", placeholder="Type text to replace")
        with col2:
            new_text = st.text_input("Replace With:", placeholder="New text")
        
        if st.button("🔄 Replace Text") and old_text:
            try:
                text_instances = page.search_for(old_text)
                
                if text_instances:
                    for inst in text_instances:
                        page.add_redact_annot(inst, fill=(1, 1, 1))
                    page.apply_redactions()
                    
                    # Add new text
                    first_inst = text_instances[0]
                    page.insert_text(
                        (first_inst.x0, first_inst.y0 + 10),
                        new_text,
                        fontsize=11,
                        color=(0, 0, 0)
                    )
                    
                    # Save
                    output_buffer = BytesIO()
                    doc.save(output_buffer)
                    output_buffer.seek(0)
                    
                    st.success(f"✅ Replaced '{old_text}' with '{new_text}'")
                    st.download_button(
                        "📥 Download Edited PDF",
                        output_buffer,
                        f"edited_{uploaded_pdf.name}",
                        "application/pdf"
                    )
                else:
                    st.warning("⚠️ Text not found on this page")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

# 📸 IMAGE OCR
elif choice == "📸 OCR":
    st.markdown("## 📸 Image to Text (OCR)")
    st.markdown("**Languages:** Telugu + English")
    
    uploaded_image = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    
    lang_choice = st.radio("Select Language:", ["English", "Telugu", "Both"], horizontal=True)
    
    if uploaded_image and st.button("🔍 Extract Text"):
        try:
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Image", width=400)
            
            # OCR language mapping
            lang_map = {
                "English": "eng",
                "Telugu": "tel",
                "Both": "eng+tel"
            }
            
            with st.spinner("🔄 Processing..."):
                extracted_text = pytesseract.image_to_string(
                    image, 
                    lang=lang_map[lang_choice]
                )
                
                if extracted_text.strip():
                    st.success("✅ Text Extracted!")
                    st.text_area("📝 Extracted Text:", extracted_text, height=300)
                    
                    # Download option
                    st.download_button(
                        "📥 Download Text",
                        extracted_text,
                        f"ocr_output_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        "text/plain"
                    )
                else:
                    st.warning("⚠️ No text detected. Try:")
                    st.info("• Better image quality\n• Clear text visibility\n• Different language setting")
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")
            if "pytesseract" in str(e):
                st.info("💡 Install: sudo apt-get install tesseract-ocr tesseract-ocr-tel")

# ⚖️ VOLUMETRIC CALCULATOR
elif choice == "⚖️ VoluCalc":
    st.markdown("## ⚖️ Volumetric Weight Calculator")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        length = st.number_input("Length (cm):", min_value=0.0, step=0.1)
    with col2:
        width = st.number_input("Width (cm):", min_value=0.0, step=0.1)
    with col3:
        height = st.number_input("Height (cm):", min_value=0.0, step=0.1)
    
    actual_weight = st.number_input("Actual Weight (kg):", min_value=0.0, step=0.1)
    
    if st.button("⚖️ Calculate Chargeable Weight"):
        if length > 0 and width > 0 and height > 0:
            volumetric_weight = (length * width * height) / 5000
            chargeable = max(volumetric_weight, actual_weight)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📦 Volumetric Weight", f"{volumetric_weight:.2f} kg")
            with col2:
                st.metric("⚖️ Actual Weight", f"{actual_weight:.2f} kg")
            with col3:
                st.metric("💰 Chargeable Weight", f"{chargeable:.2f} kg", 
                         delta=f"+{chargeable-actual_weight:.2f} kg" if chargeable > actual_weight else "Actual")
            
            st.success(f"✅ Billing Weight: **{chargeable:.2f} kg** ({chargeable*1000:.0f} grams)")
        else:
            st.warning("⚠️ Enter all dimensions!")
