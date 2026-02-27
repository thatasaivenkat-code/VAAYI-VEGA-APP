import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import pdfplumber
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from io import BytesIO
import tempfile
import os

# Page Config
st.set_page_config(page_title="VAYI VEGA - All in One Tool", layout="wide")

# Sidebar Menu
st.sidebar.title("🚀 VAYI VEGA TOOLS")
choice = st.sidebar.radio("ఒక ఆప్షన్ ఎంచుకోండి:", 
    ["PDF to Excel Converter", "Smart PDF Editor (Text Removal)", "Barcode Generator"])

# --- 📂 1. PDF TO EXCEL CONVERTER ---
if choice == "PDF to Excel Converter":
    st.title("📄 PDF to Excel Converter")
    uploaded_file = st.file_uploader("PDF ఫైల్‌ను అప్‌లోడ్ చేయండి", type=['pdf'])
    
    if uploaded_file is not None:
        if st.button("Convert to Excel"):
            all_data = []
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        df = pd.DataFrame(table)
                        all_data.append(df)
            
            if all_data:
                final_df = pd.concat(all_data, ignore_index=True)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    final_df.to_excel(writer, index=False, header=False)
                
                st.success("Excel ఫైల్ సిద్ధమైంది!")
                st.download_button("Download Excel File", data=output.getvalue(), file_name="converted_data.xlsx")
            else:
                st.error("ఈ PDF లో ఎటువంటి టేబుల్స్ దొరకలేదు.")

# --- ✏️ 2. SMART PDF EDITOR (Text Removal) ---
elif choice == "Smart PDF Editor (Text Removal)":
    st.title("✂️ Smart PDF Editor")
    st.info("ఈ టూల్ ద్వారా PDF లో మీకు వద్దనుకున్న టెక్స్ట్‌ను (ఉదా: పాత అడ్రస్ లేదా నంబర్లు) తీసేయవచ్చు.")
    
    uploaded_file = st.file_uploader("PDF ఫైల్‌ను అప్‌లోడ్ చేయండి", type=['pdf'])
    text_to_remove = st.text_input("తీసేయాల్సిన టెక్స్ట్ ఇవ్వండి (ఉదా: 9988776655):")
    
    if uploaded_file and text_to_remove:
        if st.button("Remove Text & Save"):
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            found = False
            for page in doc:
                text_instances = page.search_for(text_to_remove)
                for inst in text_instances:
                    found = True
                    page.add_redact_annot(inst, fill=(1, 1, 1)) # వైట్ కలర్‌తో కవర్ చేస్తుంది
                    page.apply_redactions()
            
            if found:
                output_pdf = BytesIO()
                doc.save(output_pdf)
                st.success(f"'{text_to_remove}' సక్సెస్‌ఫుల్‌గా తీసేయబడింది!")
                st.download_button("Download Edited PDF", data=output_pdf.getvalue(), file_name="edited_document.pdf")
            else:
                st.warning("మీరు ఇచ్చిన టెక్స్ట్ ఈ PDF లో ఎక్కడా దొరకలేదు.")

# --- 📦 3. BARCODE GENERATOR (With Logo Support) ---
elif choice == "Barcode Generator":
    st.title("📦 DTDC Style Barcode Labels")
    numbers_input = st.text_area("ట్రాకింగ్ నంబర్లను ఇక్కడ పేస్ట్ చేయండి (లైన్ కి ఒకటి):", height=150)
    company_name = st.text_input("కంపెనీ పేరు ఇవ్వండి (ఉదా: VAYI VEGA):")
    
    LOGO_FILENAME = 'logo.png' 
    
    if st.button("Generate Labels"):
        if numbers_input.strip() and company_name.strip():
            tracking_list = [n.strip() for n in numbers_input.split('\n') if n.strip()]
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4
            
            # Label Settings
            label_width, label_height = 2.8 * inch, 1.4 * inch
            margin_x, margin_y = 0.4 * inch, 0.4 * inch
            curr_x, curr_y = margin_x, height - margin_y - label_height
            
            has_logo = os.path.exists(LOGO_FILENAME)
            
            for num in tracking_list:
                try:
                    # బార్‌కోడ్ క్రియేషన్
                    code_class = barcode.get_barcode_class('code128')
                    my_barcode = code_class(num, writer=ImageWriter())
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        img_path = my_barcode.save(tmp.name.replace(".png", ""), 
                                                 options={"write_text": True, "font_size": 10, "text_distance": 4})
                    
                    # బాక్స్ గీయడం (Label Border)
                    c.rect(curr_x, curr_y, label_width, label_height)
                    
                    # 1. లోగో (ఉంటే)
                    if has_logo:
                        c.drawImage(LOGO_FILENAME, curr_x + 5, curr_y + label_height - 35, width=50, height=25, preserveAspectRatio=True)
                    
                    # 2. కంపెనీ పేరు
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(curr_x + 60, curr_y + label_height - 20, company_name.upper())
                    
                    # 3. బార్‌కోడ్ ఇమేజ్
                    c.drawImage(img_path, curr_x + 5, curr_y + 5, width=label_width - 10, height=label_height - 50)
                    
                    # పొజిషన్ అప్‌డేట్
                    curr_x += label_width + 0.2 * inch
                    if curr_x + label_width > width - margin_x:
                        curr_x = margin_x
                        curr_y -= label_height + 0.2 * inch
                        
                    if curr_y < margin_y:
                        c.showPage()
                        curr_y = height - margin_y - label_height
                        curr_x = margin_x
                        
                    if os.path.exists(img_path): os.remove(img_path)
                    
                except Exception as e:
                    st.error(f"Error: {e}")
            
            c.save()
            st.success("అన్ని లేబుల్స్ తయారయ్యాయి!")
            st.download_button("Download PDF", data=pdf_buffer.getvalue(), file_name="labels.pdf")
        else:
            st.warning("దయచేసి నంబర్లు మరియు కంపెనీ పేరు ఎంటర్ చేయండి.")
