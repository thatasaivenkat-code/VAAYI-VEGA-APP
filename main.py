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
from PyPDF2 import PdfReader, PdfWriter

# ===============================================
# 🧠 SMART SORTER UTILITIES (E25/D19 Logic) - ALL FIXED
# ===============================================
def extract_full_ref(text):
    """Extract ALL reference patterns E25+1, D19+1, 19-XXXX, etc."""
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

def normalize_ref(ref_text): 
    return re.sub(r'\s+', '', ref_text).lower().strip()

def get_group_id(ref_text): 
    """E25+1 → 25, D19+1 → 19 - PRIORITY LOGIC"""
    ref_upper = ref_text.upper()
    
    # E LOGIC FIRST (Highest Priority)
    e_match = re.search(r'E(\d+)', ref_upper)
    if e_match: 
        return e_match.group(1)[:2]
    
    # D LOGIC SECOND
    d_match = re.search(r'D(\d+)', ref_upper)
    if d_match:
        return d_match.group(1)[:2]
    
    # Generic fallback
    match = re.search(r'[A-Z]?(\d+)', ref_text)
    return match.group(1)[:2] if match else None

def validate_ref(ref_text):
    patterns = [r'\d+-\d+', r'[A-Z]?\d+\+\d+', r'No\d+', r'\b[A-Z]?\d{8,}\b']
    return any(re.search(p, ref_text, re.I) for p in patterns)

# --- SUPER CUSTOM CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif !important;
}
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.main-title {
    font-size: 4rem !important;
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
    text-align: center;
    margin-bottom: 20px;
}
.subtitle {
    font-size: 1.3rem !important;
    color: #fff;
    text-align: center;
    background: rgba(255,255,255,0.1);
    padding: 15px 30px;
    border-radius: 50px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    margin-bottom: 40px;
}
.feature-card {
    background: rgba(255,255,255,0.95);
    padding: 30px;
    border-radius: 20px;
    margin: 15px 0;
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    cursor: pointer;
    height: 160px;
    display: flex;
    align-items: center;
}
.feature-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 25px 50px rgba(0,0,0,0.2);
    background: rgba(255,255,255,1);
}
.feature-icon {
    font-size: 3rem !important;
    margin-right: 20px;
}
.card-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 8px;
}
.card-desc {
    color: #7f8c8d;
    font-size: 0.95rem;
}
.tool-section {
    background: rgba(255,255,255,0.95);
    padding: 35px;
    border-radius: 25px;
    margin: 20px 0;
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}
.section-title {
    font-size: 2.2rem !important;
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 25px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# --- PAGE CONFIG ---
st.set_page_config(page_title="🚀 వాయి వేగ Pro", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div style="text-align:center; padding:20px; background:rgba(255,255,255,0.1); border-radius:20px; margin-bottom:20px;"><h2 style="color:white; margin:0;">🚀 Vaayi Vega</h2></div>', unsafe_allow_html=True)
    
    choice = st.radio("✨ Choose Tool:", 
                     ["🏠 Dashboard", "📦 PDF Sorter", "📦 Barcode Pro", "📊 PDF→Excel", 
                      "✏️ PDF Editor", "📸 Image OCR", "⚖️ VoluCalc"],
                     index=0,
                     label_visibility="collapsed")

# ===============================================
# 🏠 HOME DASHBOARD
# ===============================================
if choice == "🏠 Dashboard":
    st.markdown('<h1 class="main-title">వాయి వేగ Multi-Tool Pro 🚀</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">7-in-1 AI Business Tools | Telugu + English | E25/D19 Support</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📦</span>
            <div>
                <div class="card-title">PDF Sorter (NEW)</div>
                <div class="card-desc">E25+1→Group25 | D19+1→Group19</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
                <div class="card-desc">Delhivery + DTDC + E/D refs → Excel.</div>
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
        <div class="feature-card" style="background: linear-gradient(145deg, #FF6B6B, #4ECDC4); color:white;">
            <span class="feature-icon">⚖️</span>
            <div>
                <div class="card-title" style="color:white;">VoluCalc</div>
                <div class="card-desc" style="color:rgba(255,255,255,0.9);">L×W×H → Billing KG</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ===============================================
# 📦 PDF SORTER (COMPLETE FROM 2CODES.DOCX)
# ===============================================
elif choice == "📦 PDF Sorter":
    st.markdown('<h2 class="section-title">📦 Smart PDF Reference Sorter</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    uploaded_files = st.file_uploader("📁 Drop PDFs here", type=['pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        grouped_pages = {}
        no_id_pages = PdfWriter()
        skip_details = []
        all_seen_refs = set()
        
        with st.spinner("🔄 Processing PDFs..."):
            for file in uploaded_files:
                file.seek(0)
                bytes_io = BytesIO(file.read())
                reader = PdfReader(bytes_io)
                pdf_seen_refs = set()
                
                with pdfplumber.open(bytes_io) as pdf:
                    for p_idx, page in enumerate(pdf.pages):
                        text = page.extract_text() or ""
                        ref = extract_full_ref(text)
                        
                        if ref:
                            norm_ref = normalize_ref(ref)
                            
                            if norm_ref in pdf_seen_refs:
                                skip_details.append(f"{file.name}(p{p_idx+1}): {ref} [PDF DUPE]")
                                continue
                            if norm_ref in all_seen_refs:
                                skip_details.append(f"{file.name}(p{p_idx+1}): {ref} [GLOBAL DUPE]")
                                continue
                            
                            pdf_seen_refs.add(norm_ref)
                            all_seen_refs.add(norm_ref)
                            gid = get_group_id(ref)
                            
                            if gid and validate_ref(ref):
                                grouped_pages.setdefault(gid, []).append(reader.pages[p_idx])
                            else:
                                no_id_pages.add_page(reader.pages[p_idx])
        
        # METRICS
        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Groups", len(grouped_pages))
        col2.metric("⏭️ Skips", len(skip_details))
        col3.metric("📄 Files", len(uploaded_files))
        
        st.divider()
        
        # GROUP DOWNLOADS
        if grouped_pages:
            st.markdown("<h3>📂 Group Downloads</h3>", unsafe_allow_html=True)
            cols = st.columns(3)
            
            for i, (gid, pages) in enumerate(sorted(grouped_pages.items())):
                with cols[i % 3]:
                    writer = PdfWriter()
                    for page in pages: writer.add_page(page)
                    bio = BytesIO()
                    writer.write(bio)
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                color: white; text-align: center; border-radius: 12px; padding: 1rem;">
                        <h4>Group {gid}</h4>
                        <p>{len(pages)} pages</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.download_button(
                        label=f"📥 Group-{gid}",
                        data=bio.getvalue(),
                        file_name=f"Group_{gid}_{now}.pdf",
                        use_container_width=True
                    )
        
        # DOWNLOAD SECTION
        col1, col2 = st.columns(2)
        
        if no_id_pages.pages:
            with col1:
                bio = BytesIO()
                no_id_pages.write(bio)
                st.info(f"No Reference ({len(no_id_pages.pages)} pages)")
                st.download_button("📂 No-Ref", bio.getvalue(), f"NoRef_{now}.pdf")
        
        if skip_details:
            with col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
                            color: white; text-align: center; border-radius: 12px; padding: 1rem;">
                    <h4>⚠️ Skipped Items</h4>
                    <p>{len(skip_details)} duplicates found</p>
                </div>
                """, unsafe_allow_html=True)
                
                skip_txt = "SKIPPED REFERENCES:\n\n" + "\n".join(skip_details)
                st.download_button(
                    label=f"📥 Skips ({len(skip_details)})",
                    data=skip_txt,
                    file_name=f"Skips_{now}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        # BULK DOWNLOAD
        if grouped_pages:
            st.markdown("---")
            total_pages = sum(len(pages) for pages in grouped_pages.values())
            bulk_writer = PdfWriter()
            for pages_list in grouped_pages.values():
                for page in pages_list: bulk_writer.add_page(page)
            
            bulk_bio = BytesIO()
            bulk_writer.write(bulk_bio)
            st.success(f"🎯 Complete: {len(grouped_pages)} Groups / {total_pages} Pages")
            st.download_button("📦 All Groups", bulk_bio.getvalue(), f"AllGroups_{now}.pdf")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# 📦 BARCODE GENERATOR
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
    
    if st.button("🖨️ Generate PDF Labels", use_container_width=True):
        if numbers_input.strip() and company_name.strip():
            tracking_list = [n.strip() for n in numbers_input.split('\n') if n.strip()]
            try:
                pdf_buffer = BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=A4)
                width, height = A4
                label_width, label_height = 3 * inch, 1.5 * inch
                margin_x, margin_y = 0.5 * inch, 0.5 * inch
                curr_x, curr_y = margin_x, height - margin_y - label_height
                
                for num in tracking_list:
                    code_class = barcode.get_barcode_class('code128')
                    my_barcode = code_class(num, writer=ImageWriter())
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        img_path = my_barcode.save(tmp.name.replace(".png", ""), 
                                                 options={"write_text": True, "font_size": 8, "text_distance": 3})
                    
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
                    if os.path.exists(img_path): 
                        os.remove(img_path)
                
                c.save()
                st.success(f"✅ {len(tracking_list)} labels generated successfully!")
                st.download_button("📥 Download PDF", pdf_buffer.getvalue(), 
                                 f"{company_name}_Labels.pdf", use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter tracking numbers and company name!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# 📊 PDF TO EXCEL (WITH E/D LOGIC)
# ===============================================
elif choice == "📊 PDF→Excel":
    st.markdown('<h2 class="section-title">📊 PDF to Excel Converter</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    st.subheader("1️⃣ కొరియర్ సెట్టింగ్స్")
    
    col_del, col_dtdc = st.columns(2)
    
    with col_del:
        use_delhivery = st.checkbox("🚚 Delhivery Labels", value=True)
        del_client = st.text_input("Delhivery క్లయింట్ ఐడి:", key="del_c", placeholder="e.g
