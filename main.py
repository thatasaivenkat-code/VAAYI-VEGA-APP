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
import base64
from PIL import Image

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
        <div class="feature-card" style="background: linear-gradient(145deg, #FF6B6B, #4ECDC4); color:white;">
            <span class="feature-icon">🎉</span>
            <div>
                <div class="card-title" style="color:white;">All Tools Ready!</div>
                <div class="card-desc" style="color:rgba(255,255,255,0.9);">Select from sidebar to start 🚀</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
# 📊 PDF TO EXCEL CONVERTER
# ===============================================
elif choice == "📊 PDF→Excel":
    st.markdown('<h2 class="section-title">📊 PDF to Excel Converter</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    st.subheader("1️⃣ కొరియర్ సెట్టింగ్స్")
    
    col_del, col_dtdc = st.columns(2)
    
    with col_del:
        use_delhivery = st.checkbox("🚚 Delhivery Labels", value=True)
        del_client = st.text_input("Delhivery క్లయింట్ ఐడి:", key="del_c", placeholder="e.g., 1234")
        del_weight = st.text_input("Delhivery వెయిట్:", key="del_w", placeholder="e.g., 0.5")
        
    with col_dtdc:
        use_dtdc = st.checkbox("📦 DTDC Labels", value=True)
        dtdc_client = st.text_input("DTDC క్లయింట్ ఐడి:", key="dtdc_c", placeholder="e.g., 5678")
        dtdc_weight = st.text_input("DTDC వెయిట్:", key="dtdc_w", placeholder="e.g., 1.0")

    st.divider()
    
    st.subheader("2️⃣ PDF ఫైల్స్ అప్‌లోడ్ చేయండి")
    pdf_files = st.file_uploader("📄 Select PDF Files", type=['pdf'], accept_multiple_files=True)

    if pdf_files and st.button("🔄 Convert to Excel", use_container_width=True):
        all_extracted_data = []
        
        with st.spinner("📊 Processing PDFs..."):
            for pdf_file in pdf_files:
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if not text: 
                            continue
                        
                        final_date, awb, dest_name, dest_pin = "", "", "", ""
                        row_client, row_weight = "", ""

                        # --- Delhivery Logic ---
                        if use_delhivery and ("AWB#" in text or "Delhivery" in text):
                            row_client = del_client
                            row_weight = del_weight
                            d_match = re.search(r"(\d{2}-[a-zA-Z]{3}-\d{4})", text)
                            if d_match:
                                try:
                                    d_obj = datetime.strptime(d_match.group(1), '%d-%b-%Y')
                                    final_date = d_obj.strftime('%d-%m-%Y')
                                except: 
                                    pass
                            awb_m = re.search(r"AWB#\s*(\d+)", text)
                            awb = awb_m.group(1) if awb_m else ""
                            n_match = re.search(r"Ship to\s*-\s*([^\n]+)", text)
                            dest_name = n_match.group(1).strip() if n_match else ""
                            p_match = re.search(r"PIN\s*[:\-\s]*(\d{6})", text)
                            dest_pin = p_match.group(1) if p_match else ""

                        # --- DTDC Logic ---
                        elif use_dtdc and ("Ship Date" in text or "DTDC" in text or "TO:" in text):
                            row_client = dtdc_client
                            row_weight = dtdc_weight
                            date_match = re.search(r"Ship Date\s*:\s*(\d{2}-\d{2}-\d{4})", text)
                            final_date = date_match.group(1) if date_match else ""
                            awb_m = re.search(r"([A-Z][0-9]{10})", text)
                            awb = awb_m.group(1) if awb_m else ""
                            n_match = re.search(r"TO:\s*\n?([^\n,]+)", text)
                            dest_name = n_match.group(1).strip() if n_match else ""
                            p_match = re.search(r"Pin[:\-\s]*(\d{6})|PIN[:\-\s]*(\d{6})|(\d{6})", text)
                            if p_match:
                                dest_pin = next((g for g in p_match.groups() if g and len(g) == 6), "")
                            
                            if not row_client:
                                f_match = re.search(r"FROM:\s*\n?([a-zA-Z]+)(\d+)", text)
                                row_client = f_match.group(2) if f_match else ""

                        if awb or dest_name:
                            all_extracted_data.append({
                                "Reference No (A)": "",
                                "Client/Phone (B)": row_client,
                                "Date (C)": final_date,
                                "AWB/Tracking (D)": awb,
                                "Customer Name (E)": dest_name,
                                "Pincode (F)": dest_pin,
                                " (G)": "",
                                "Weight (H)": row_weight
                            })

        if all_extracted_data:
            df = pd.DataFrame(all_extracted_data).fillna("")
            st.success(f"✅ మొత్తం {len(all_extracted_data)} లేబుల్స్ extracted!")
            st.dataframe(df, use_container_width=True, height=400)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            
            st.download_button("📥 Download Excel File", 
                             data=output.getvalue(), 
                             file_name="Vaayi_Vega_Final.xlsx",
                             mime="application/vnd.ms-excel",
                             use_container_width=True)
        else:
            st.warning("⚠️ No data extracted. Check PDF format or settings!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# ✏️ SMART PDF LABEL EDITOR
# ===============================================
elif choice == "✏️ PDF Editor":
    st.markdown('<h2 class="section-title">✏️ Smart PDF Label Editor</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    company_type = st.radio("ఏ కంపెనీ లేబుల్?", ["DTDC", "Delhivery"], horizontal=True)
    page_option = st.selectbox("ఏ పేజీలను ఎడిట్ చేయాలి?", ["All Pages", "Custom Page Number"])
    custom_pg = 1
    if page_option == "Custom Page Number":
        custom_pg = st.number_input("Page Number:", min_value=1, step=1)
    
    up_files = st.file_uploader(f"📄 {company_type} PDF Upload", type=["pdf"], accept_multiple_files=True)
    
    if up_files:
        for u_file in up_files:
            st.markdown("---")
            st.write(f"**File:** {u_file.name}")
            c1, c2 = st.columns(2)
            with c1: 
                n_amt = st.text_input(f"💰 Amount Rs.", key=f"a_{u_file.name}")
            with c2: 
                n_wt = st.text_input(f"⚖️ Weight KG", key=f"w_{u_file.name}")
            
            if st.button(f"Process {u_file.name}", use_container_width=True):
                if n_amt and n_wt:
                    try:
                        doc = fitz.open(stream=u_file.read(), filetype="pdf")
                        pages_to_edit = range(len(doc)) if page_option == "All Pages" else [custom_pg - 1]
                        
                        for p_idx in pages_to_edit:
                            if 0 <= p_idx < len(doc):
                                page = doc[p_idx]
                                
                                if company_type == "DTDC":
                                    page.add_redact_annot(fitz.Rect(100, 480, 260, 515), fill=(1,1,1))
                                    page.apply_redactions()
                                    page.insert_text((75, 505), f"Rs. {n_amt}", fontsize=20, fontname="hebo")
                                    w_hit = page.search_for("Weight")
                                    if w_hit:
                                        page.add_redact_annot(fitz.Rect(w_hit[0].x1 + 2, w_hit[0].y0 - 2, 450, w_hit[0].y1 + 2), fill=(1,1,1))
                                        page.apply_redactions()
                                        page.insert_text((w_hit[0].x1 + 5, w_hit[0].y1 - 5.2), f": {n_wt} KG", fontsize=14, fontname="hebo")
                                else:
                                    p_hit = page.search_for("Product")
                                    if p_hit:
                                        sx, ay = p_hit[0].x0+2, p_hit[0].y1+18
                                        wy = ay+16
                                        page.add_redact_annot(fitz.Rect(sx, ay-12, sx+200, wy+5), fill=(1,1,1))
                                        page.apply_redactions()
                                        page.insert_text((sx, ay), f"Rs. {n_amt}", fontsize=12, color=(0,0,0))
                                        page.insert_text((sx, wy), f"Weight: {n_wt} KG", fontsize=12, color=(0,0,0))
                        
                        res = BytesIO()
                        doc.save(res)
                        st.success("✅ Processing completed!")
                        st.download_button(f"📥 Download {u_file.name}", 
                                         data=res.getvalue(), 
                                         file_name=f"Fixed_{u_file.name}",
                                         use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Enter both Amount and Weight!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# 📸 IMAGE TO TEXT (OCR)
# ===============================================
elif choice == "📸 Image OCR":
    st.markdown('<h2 class="section-title">📸 Image to Text Converter (OCR)</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    st.info("📌 Upload an image or take a photo to extract text (English + Telugu support)")
    
    tab1, tab2 = st.tabs(["📤 Upload Image", "📸 Camera"])
    
    img_file = None
    
    with tab1:
        up_img = st.file_uploader("📁 Choose Image", type=['png', 'jpg', 'jpeg'], key="upload_ocr")
        if up_img:
            img_file = up_img
            
    with tab2:
        cam_img = st.camera_input("📷 Take Photo", key="camera_ocr")
        if cam_img:
            img_file = cam_img

    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Selected Image", width=400)
        
        if st.button("🔍 Extract Text", use_container_width=True):
            with st.spinner("🤖 AI is reading the image..."):
                try:
                    # Try to import easyocr
                    try:
                        import easyocr
                        img_array = np.array(image.convert('L'))
                        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                        enhanced_img = clahe.apply(img_array)
                        
                        reader = easyocr.Reader(['en', 'te'])
                        result = reader.readtext(enhanced_img, detail=0, paragraph=True)
                        
                        if result:
                            full_text = "\n".join(result)
                            st.success("✅ Text extracted successfully!")
                            st.text_area("📝 Extracted Text:", full_text, height=250)
                            st.download_button("📥 Download Text", full_text, 
                                             file_name="extracted.txt", use_container_width=True)
                        else:
                            st.warning("⚠️ No text found in image. Try a clearer image.")
                    except ImportError:
                        st.error("❌ EasyOCR not installed. Install with: pip install easyocr")
                        st.info("💡 Using basic OCR (English only)...")
                        
                        # Fallback to pytesseract if available
                        try:
                            import pytesseract
                            text = pytesseract.image_to_string(image)
                            if text.strip():
                                st.success("✅ Text extracted!")
                                st.text_area("📝 Extracted Text:", text, height=250)
                                st.download_button("📥 Download Text", text, 
                                                 file_name="extracted.txt", use_container_width=True)
                            else:
                                st.warning("⚠️ No text detected")
                        except:
                            st.error("❌ No OCR library available. Install easyocr or pytesseract.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# ⚖️ VOLUMETRIC CALCULATOR
# ===============================================
elif choice == "⚖️ VoluCalc":
    st.markdown('<h2 class="section-title">⚖️ Volumetric Weight Calculator</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    
    st.info("📦 Enter box dimensions to calculate volumetric weight")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📐 Dimensions (cm)")
        length = st.number_input("📏 Length", min_value=0.0, step=0.1, key="v_l")
        width = st.number_input("📐 Width", min_value=0.0, step=0.1, key="v_w")
        height = st.number_input("📏 Height", min_value=0.0, step=0.1, key="v_h")
        
        divisor = st.selectbox("🚚 Courier Divisor:", [5000, 4500, 6000], index=0)
        st.caption("💡 Common: DTDC/Delhivery = 5000")

    with col2:
        st.subheader("📊 Results")
        if length > 0 and width > 0 and height > 0:
            vol_kg = (length * width * height) / divisor
            vol_grams = vol_kg * 1000
            
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #FF6B6B, #FF8E8E); 
                        padding:25px; border-radius:20px; color:white; text-align:center;">
                <div style="font-size:1.1rem; opacity:0.9; margin-bottom:10px;">Volumetric Weight</div>
                <div style="font-size:3rem; font-weight:700; margin:10px 0;">{vol_kg:.3f} KG</div>
                <div style="font-size:1.5rem; opacity:0.8;">({vol_grams:,.0f} Grams)</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            actual_w = st.number_input("⚖️ Actual Weight (KG):", min_value=0.0, step=0.01)
            if actual_w > 0:
                final_w = max(vol_kg, actual_w)
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #4ECDC4, #44A08D); 
                            padding:20px; border-radius:20px; color:white; text-align:center; margin-top:15px;">
                    <div style="font-size:1rem; opacity:0.9;">💰 Chargeable Weight</div>
                    <div style="font-size:2.5rem; font-weight:700; margin-top:5px;">{final_w:.3f} KG</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Enter L, W, H values")

    st.markdown("---")
    st.subheader("📁 Bulk Calculate (Excel)")
    up_vol_file = st.file_uploader("📊 Upload Excel with L, W, H columns", type=['xlsx'], key="bulk_vol")
    
    if up_vol_file:
        try:
            df_v = pd.read_excel(up_vol_file)
            if all(c in df_v.columns for c in ['Length', 'Width', 'Height']):
                df_v['Vol_Weight_KG'] = (df_v['Length'] * df_v['Width'] * df_v['Height']) / divisor
                df_v['Vol_Weight_Grams'] = df_v['Vol_Weight_KG'] * 1000
                st.success(f"✅ Processed {len(df_v)} rows")
                st.dataframe(df_v, use_container_width=True, height=300)
                
                output_v = BytesIO()
                df_v.to_excel(output_v, index=False, engine='xlsxwriter')
                st.download_button("📥 Download Results", 
                                 data=output_v.getvalue(), 
                                 file_name="Volumetric_Report.xlsx",
                                 use_container_width=True)
            else:
                st.error("❌ Excel must have 'Length', 'Width', 'Height' columns!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# FOOTER
# ===============================================
st.markdown("""
<div style="text-align:center; padding:30px; color:rgba(255,255,255,0.8); font-size:1rem; margin-top:40px;">
    ✨ Made with ❤️ for Telugu Business Owners | Vaayi Vega © 2026
</div>
""", unsafe_allow_html=True)

