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

# --- PAGE CONFIG ---
st.set_page_config(page_title="వాయి వేగ Multi-Tool", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("వాయి వేగ Navigation")
choice = st.sidebar.radio("ఏం చేయాలనుకుంటున్నారు?", 
                         ["Home", "Barcode Generator", "PDF to Excel Converter", "Smart PDF Label Editor"])

LOGO_PATH = 'logo.png' 

# --- 🏠 0. HOME PAGE ---
if choice == "Home":
    st.title("Welcome to వాయి వేగ 🚀")
    st.write("---")
    st.info("పక్కన ఉన్న మెనూ నుండి మీకు కావాల్సిన టూల్ సెలెక్ట్ చేసుకోండి.")
    st.markdown("""
    - **Barcode Generator:** కంపెనీ పేరు మరియు లోగోతో 3-ఇంచ్ లేబుల్స్.
    - **PDF to Excel:** ఢిల్లీవరీ పిడిఎఫ్ నుండి డేటా తీసి ఎక్సెల్ చేయడం (Custom Columns & PIN Fix).
    - **Smart PDF Editor:** పాత పిడిఎఫ్ లేబుల్స్ లో అమౌంట్ మరియు వెయిట్ ఫిక్స్ చేయడం.
    """)

# --- 📦 1. BARCODE GENERATOR (With Centered Logo) ---
elif choice == "Barcode Generator":
    st.title("📦 Standard 3-Inch Barcode Labels")
    numbers_input = st.text_area("ట్రాకింగ్ నంబర్లను ఇక్కడ పేస్ట్ చేయండి:", height=150)
    company_name = st.text_input("కంపెనీ పేరు ఇవ్వండి:")
    
    if st.button("Generate Standard PDF"):
        if numbers_input.strip() and company_name.strip():
            tracking_list = [n.strip() for n in numbers_input.split('\n') if n.strip()]
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4
            
            # Label Size settings (3 inch x 1.5 inch)
            label_width, label_height = 3 * inch, 1.5 * inch
            margin_x, margin_y = 0.5 * inch, 0.5 * inch
            curr_x, curr_y = margin_x, height - margin_y - label_height
            
            # --- లోగో ఉందో లేదో చెక్ చేయడం ---
            has_logo = os.path.exists(LOGO_PATH)
            
            for num in tracking_list:
                try:
                    # బార్‌కోడ్ క్రియేషన్
                    code_class = barcode.get_barcode_class('code128')
                    my_barcode = code_class(num, writer=ImageWriter())
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        img_path = my_barcode.save(tmp.name.replace(".png", ""), options={"write_text": True, "font_size": 8, "text_distance": 3})
                    
                    # --- బాక్స్ చుట్టూ బార్డర్ (Label Border) ---
                    c.rect(curr_x, curr_y, label_width, label_height)
                    
                    # 1. కంపెనీ పేరు (పైన సెంటర్ లో)
                    c.setFont("Helvetica-Bold", 10)
                    c.drawCentredString(curr_x + (label_width/2), curr_y + label_height - 15, company_name.upper())
                    
                    # 2. లోగో (సెంటర్ లో - కంపెనీ పేరుకి కొంచెం కింద)
                    if has_logo:
                        logo_w, logo_h = 60, 25 # లోగో సైజు (Adjustable)
                        logo_y = curr_y + label_height - 45
                        # సెంటర్ చేయడానికి లెక్క: (Label Width / 2) - (Logo Width / 2)
                        logo_x_centered = curr_x + (label_width/2) - (logo_w/2)
                        c.drawImage(LOGO_PATH, logo_x_centered, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True)
                    
                    # 3. బార్‌కోడ్ ఇమేజ్ (నంబర్‌తో సహా - కింద సెంటర్ లో)
                    barcode_w = label_width - 20
                    barcode_h = label_height - 55
                    barcode_x_centered = curr_x + 10
                    barcode_y = curr_y + 10
                    c.drawImage(img_path, barcode_x_centered, barcode_y, width=barcode_w, height=barcode_h)
                    
                    # తదుపరి లేబుల్ స్థానం అప్‌డేట్
                    curr_x += label_width + 0.2 * inch
                    if curr_x + label_width > width - margin_x:
                        curr_x = margin_x
                        curr_y -= label_height + 0.3 * inch
                        
                    # పేజీ నిండిపోతే కొత్త పేజీ
                    if curr_y < margin_y:
                        c.showPage()
                        curr_y = height - margin_y - label_height
                        curr_x = margin_x
                        
                    if os.path.exists(img_path): os.remove(img_path)
                    
                except Exception as e:
                    st.error(f"Error for {num}: {e}")
            
            c.save()
            st.success("లేబుల్స్ తయారయ్యాయి!")
            st.download_button("Download Labels PDF", data=pdf_buffer.getvalue(), file_name=f"{company_name}_Standard.pdf")
        else:
            st.warning("దయచేసి నంబర్లు మరియు కంపెనీ పేరు ఎంటర్ చేయండి.")

# --- 📊 2. PDF TO EXCEL CONVERTER ---
elif choice == "PDF to Excel Converter":
    st.title("📊 వాయి వేగ PDF to Excel")
    
    col_b, col_h = st.columns(2)
    with col_b:
        client_name = st.text_input("క్లయింట్ నేమ్ / ఐడి ఎంటర్ చేయండి (Column B):")
    with col_h:
        weight_val = st.text_input("వెయిట్ (Weight) ఎంటర్ చేయండి (Column H):")

    pdf_files = st.file_uploader("PDF ఫైల్స్ అప్‌లోడ్ చేయండి", type=['pdf'], accept_multiple_files=True)

    if pdf_files:
        all_extracted_data = []
        for pdf_file in pdf_files:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # తేదీ ఫార్మాట్: 26-02-2026
                        date_match = re.search(r"(\d{2}-[a-zA-Z]{3}-\d{4})", text)
                        final_date = ""
                        if date_match:
                            try:
                                d_obj = datetime.strptime(date_match.group(1), '%d-%b-%Y')
                                final_date = d_obj.strftime('%d-%m-%Y')
                            except: final_date = ""

                        awb = re.search(r"AWB#\s*(\d+)", text)
                        name = re.search(r"Ship to\s*-\s*([^\n]+)", text)
                        
                        # --- PIN CODE FIX ---
                        pin = re.search(r"PIN\s*[:\-\s]*(\d{6})", text)

                        if awb or name:
                            all_extracted_data.append({
                                "A": "", 
                                "B": client_name, 
                                "C": final_date,
                                "D": awb.group(1) if awb else "",
                                "E": name.group(1).strip() if name else "",
                                "F": pin.group(1) if pin else "",
                                "G": "", 
                                "H": weight_val
                            })

        if all_extracted_data:
            df = pd.DataFrame(all_extracted_data)
            st.dataframe(df)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
                workbook = writer.book
                worksheet = writer.sheets['Data']

                # ఫార్మాటింగ్: Center, Middle, Wrap Off
                cell_format = workbook.add_format({
                    'align': 'center', 
                    'valign': 'vcenter', 
                    'text_wrap': False
                })

                # ఆటో కాలమ్ విడ్త్
                for i, col in enumerate(df.columns):
                    worksheet.set_column(i, i, 20, cell_format)

            st.download_button("Download Excel File", data=output.getvalue(), file_name="Vaayi_Vega_Data.xlsx")

# --- 📄 3. SMART PDF LABEL EDITOR ---
elif choice == "Smart PDF Label Editor":
    st.title("📄 Smart PDF Label Editor")
    up_files = st.file_uploader("PDF ఫైల్స్ సెలెక్ట్ చేయండి", type=["pdf"], accept_multiple_files=True)
    if up_files:
        for u_file in up_files:
            st.markdown("---")
            st.subheader(f"Editing: {u_file.name}")
            c1, c2 = st.columns(2)
            with c1: n_amt = st.text_input(f"అమౌంట్ Rs.", key=f"a_{u_file.name}")
            with c2: n_wt = st.text_input(f"వెయిట్ KG", key=f"w_{u_file.name}")
            if st.button(f"Process {u_file.name}"):
                if n_amt and n_wt:
                    doc = fitz.open(stream=u_file.read(), filetype="pdf")
                    page = doc[0]
                    # అమౌంట్ బాక్స్ క్లీన్ చేసి కొత్త అమౌంట్ వేయడం
                    page.add_redact_annot(fitz.Rect(100, 480, 260, 515), fill=(1,1,1))
                    page.apply_redactions()
                    page.insert_text((75, 505), f"Rs. {n_amt}", fontsize=20)
                    # వెయిట్ ఎడిట్
                    w_hit = page.search_for("Weight")
                    if w_hit:
                        page.add_redact_annot(fitz.Rect(w_hit[0].x1 + 2, w_hit[0].y0 - 2, 450, w_hit[0].y1 + 2), fill=(1,1,1))
                        page.apply_redactions()
                        page.insert_text((w_hit[0].x1 + 5, w_hit[0].y1 - 2), f": {n_wt} KG", fontsize=14)
                    res = BytesIO()
                    doc.save(res)
                    st.download_button(f"Download {u_file.name}", data=res.getvalue(), file_name=f"Fixed_{u_file.name}")
