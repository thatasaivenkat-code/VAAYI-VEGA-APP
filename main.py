import streamlit as st
from datetime import datetime
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
import re
import io
import fitz  # PyMuPDF
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import tempfile
import os
from io import BytesIO

# SUPER CUSTOM CSS (Combined)
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
.card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
       border-radius: 15px; padding: 1.5rem; margin: 1rem 0;}
.metric-card {background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
              color: white; text-align: center; border-radius: 12px; padding: 1rem;}
.skip-card {background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
            color: white; text-align: center;}
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
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Vaayi Vega Pro", layout="wide", page_icon="🚛")

# PDF Reference Extractor Functions (FIXED)
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

# SIDEBAR
with st.sidebar:
    st.markdown('<div style="text-align:center; padding:20px; background:rgba(255,255,255,0.1); border-radius:20px; margin-bottom:20px;"><h2 style="color:white; margin:0;">🚀 Vaayi Vega Pro</h2></div>', unsafe_allow_html=True)
    
    choice = st.radio("✨ Choose Tool:", 
                     ["📦 PDF Groups", "📊 PDF→Excel", "🏠 Dashboard"],  # PDF Groups first!
                     index=0,
                     label_visibility="collapsed")

now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

# ===============================================
# 📦 PDF GROUPS EXTRACTOR (Your main tool)
# ===============================================
if choice == "📦 PDF Groups":
    st.markdown('<h1 class="main-title">🚛 PDF Reference Extractor Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">E25+1→25 | D19+1→19 | Duplicates skipped | Auto-group</p>', unsafe_allow_html=True)

    # File upload
    uploaded_files = st.file_uploader("📁 Drop PDFs here", type=['pdf'], accept_multiple_files=True)

    if uploaded_files:
        # SILENT PROCESSING
        grouped_pages = {}
        no_id_pages = PdfWriter()
        skip_details = []
        all_seen_refs = set()
        
        for file in uploaded_files:
            file.seek(0)
            bytes_io = io.BytesIO(file.read())
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
        
        # DASHBOARD METRICS
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
                    bio = io.BytesIO()
                    writer.write(bio)
                    
                    st.markdown(f"""
                    <div class="card metric-card">
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
                bio = io.BytesIO()
                no_id_pages.write(bio)
                st.info(f"No Reference ({len(no_id_pages.pages)} pages)")
                st.download_button("📂 No-Ref", bio.getvalue(), f"NoRef_{now}.pdf")
        
        if skip_details:
            with col2:
                st.markdown(f"""
                <div class="skip-card">
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
            
            bulk_bio = io.BytesIO()
            bulk_writer.write(bulk_bio)
            st.success(f"🎯 Complete: {len(grouped_pages)} Groups / {total_pages} Pages")
            st.download_button("📦 All Groups", bulk_bio.getvalue(), f"AllGroups_{now}.pdf")

# ===============================================
# 📊 PDF→EXCEL CONVERTER (Simplified version)
# ===============================================
elif choice == "📊 PDF→Excel":
    st.markdown('<h2 class="section-title">📊 PDF to Excel Converter</h2>', unsafe_allow_html=True)
    
    pdf_files = st.file_uploader("📄 Select PDF Files", type=['pdf'], accept_multiple_files=True)
    
    if pdf_files and st.button("🔄 Convert to Excel", use_container_width=True):
        all_data = []
        with st.spinner("Processing..."):
            for pdf_file in pdf_files:
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text() or ""
                        ref = extract_full_ref(text)
                        if ref:
                            gid = get_group_id(ref)
                            all_data.append({
                                'Reference': ref,
                                'Group_ID': gid or '',
                                'File': pdf_file.name
                            })
        
        if all_data:
            df = pd.DataFrame(all_data)
            st.success(f"✅ {len(all_data)} references extracted!")
            st.dataframe(df)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='References')
            
            st.download_button("📥 Download Excel", 
                             data=output.getvalue(), 
                             file_name=f"PDF_References_{now}.xlsx")
        else:
            st.warning("⚠️ No references found!")

# ===============================================
# 🏠 DASHBOARD
# ===============================================
elif choice == "🏠 Dashboard":
    st.markdown('<h1 class="main-title">వాయి వేగ Multi-Tool Pro 🚀</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">PDF Groups + Excel + More Tools Coming Soon!</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span style="font-size:3rem;">📦</span>
            <div>
                <div style="font-size:1.4rem; font-weight:600;">PDF Reference Extractor</div>
                <div style="color:#7f8c8d;">E25+1→25 | D19+1→19 | Auto-group</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span style="font-size:3rem;">📊</span>
            <div>
                <div style="font-size:1.4rem; font-weight:600;">PDF to Excel</div>
                <div style="color:#7f8c8d;">Extract references to Excel sheet</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; padding:30px; color:rgba(255,255,255,0.8); font-size:1rem; margin-top:40px;">
    ✨ Vaayi Vega Pro © 2026 | Made for Courier Business 🚀
</div>
""", unsafe_allow_html=True)
