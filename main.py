# --- NEON THEME CSS (FIXED VERSION) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

/* Global Styles */
* {
    font-family: 'Rajdhani', sans-serif !important;
}

/* Background - FIXED */
.stApp {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 50%, #16213e 100%);
    background-attachment: fixed;
    min-height: 100vh;
    position: relative;
}

/* Neon Background Overlay - FIXED */
.stApp > div:first-child::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: 
        radial-gradient(circle at 20% 30%, rgba(255, 0, 255, 0.2) 0%, transparent 40%),
        radial-gradient(circle at 80% 70%, rgba(0, 255, 255, 0.2) 0%, transparent 40%),
        radial-gradient(circle at 50% 20%, rgba(0, 255, 157, 0.15) 0%, transparent 50%);
    animation: neonPulse 6s ease-in-out infinite;
    pointer-events: none;
    z-index: -1;
}

@keyframes neonPulse {
    0%, 100% { opacity: 0.7; }
    50% { opacity: 1; }
}

/* Main Title - FIXED */
.main-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 3.8rem !important;
    background: linear-gradient(45deg, #ff00ff, #00ffff, #00ff9d, #ff0080, #ff00ff);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 900;
    text-align: center;
    margin: 20px 0 30px 0;
    padding: 20px;
    animation: neonGradient 3s ease infinite, glowPulse 2s ease-in-out infinite alternate;
    text-shadow: 
        0 0 10px #ff00ff,
        0 0 20px #00ffff,
        0 0 30px rgba(0, 255, 157, 0.5);
    letter-spacing: 2px;
}

@keyframes neonGradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes glowPulse {
    from { filter: drop-shadow(0 0 10px #ff00ff); }
    to { filter: drop-shadow(0 0 20px #00ffff); }
}

/* Subtitle - FIXED */
.subtitle {
    font-size: 1.4rem !important;
    background: linear-gradient(90deg, #00ffff, #00ff9d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    padding: 15px 40px;
    margin-bottom: 40px;
    border: 2px solid transparent;
    border-radius: 50px;
    background-clip: text;
    font-weight: 600;
    position: relative;
    display: inline-block;
}

.subtitle::before {
    content: '';
    position: absolute;
    top: -4px;
    left: -4px;
    right: -4px;
    bottom: -4px;
    background: linear-gradient(45deg, #ff00ff, #00ffff, #00ff9d, #ff00ff);
    border-radius: 55px;
    z-index: -1;
    animation: borderRotate 3s linear infinite;
}

@keyframes borderRotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Feature Cards - FIXED */
.feature-card {
    background: rgba(15, 15, 25, 0.9) !important;
    backdrop-filter: blur(20px);
    padding: 30px !important;
    border-radius: 20px !important;
    margin: 15px 0 !important;
    border: 2px solid rgba(0, 255, 255, 0.3);
    box-shadow: 
        0 10px 30px rgba(0, 0, 0, 0.5),
        0 0 20px rgba(0, 255, 255, 0.2),
        inset 0 0 20px rgba(0, 255, 255, 0.05);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    height: 160px !important;
    display: flex !important;
    align-items: center !important;
    position: relative !important;
    overflow: hidden;
}

.feature-card:hover {
    transform: translateY(-12px) scale(1.02) !important;
    border-color: #00ffff !important;
    box-shadow: 
        0 20px 40px rgba(0, 0, 0, 0.6),
        0 0 40px rgba(0, 255, 255, 0.6),
        0 0 60px rgba(255, 0, 255, 0.3),
        inset 0 0 30px rgba(0, 255, 255, 0.1) !important;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.2), transparent);
    transition: left 0.6s;
}

.feature-card:hover::before {
    left: 100%;
}

.feature-icon {
    font-size: 3.2rem !important;
    margin-right: 20px;
    filter: drop-shadow(0 0 15px currentColor);
    animation: iconFloat 3s ease-in-out infinite;
}

@keyframes iconFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

.card-title {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    background: linear-gradient(45deg, #00ffff, #00ff9d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px !important;
    text-shadow: none;
    font-family: 'Orbitron', monospace;
}

.card-desc {
    color: #a0a0ff !important;
    font-size: 1rem !important;
    font-weight: 400;
    text-shadow: 0 0 8px rgba(160, 160, 255, 0.5);
}

/* Tool Section - FIXED */
.tool-section {
    background: rgba(15, 15, 25, 0.95) !important;
    backdrop-filter: blur(25px);
    padding: 40px !important;
    border-radius: 25px !important;
    margin: 25px 0 !important;
    border: 2px solid rgba(255, 0, 255, 0.4);
    box-shadow: 
        0 20px 50px rgba(0, 0, 0, 0.6),
        0 0 30px rgba(255, 0, 255, 0.3),
        inset 0 0 30px rgba(255, 0, 255, 0.05);
    position: relative;
    z-index: 1;
}

.section-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 2.6rem !important;
    background: linear-gradient(90deg, #ff00ff, #00ffff, #00ff9d);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 30px !important;
    font-weight: 800 !important;
    animation: neonGradient 2.5s ease infinite;
    text-shadow: 
        0 0 15px rgba(255, 0, 255, 0.6),
        0 0 25px rgba(0, 255, 255, 0.4);
    letter-spacing: 1.5px;
}

/* Sidebar - FIXED */
section[data-testid="stSidebar"] {
    background: rgba(10, 10, 20, 0.95) !important;
    backdrop-filter: blur(20px);
    border-right: 3px solid rgba(0, 255, 255, 0.5) !important;
    box-shadow: 5px 0 30px rgba(0, 255, 255, 0.3) !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding-top: 20px !important;
}

section[data-testid="stSidebar"] .stRadio > div > label {
    color: #00ffff !important;
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    padding: 15px 20px !important;
    border-radius: 15px !important;
    border: 2px solid rgba(0, 255, 255, 0.2) !important;
    margin: 5px 0 !important;
    transition: all 0.3s ease !important;
}

section[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(0, 255, 255, 0.15) !important;
    border-color: #00ffff !important;
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.4) !important;
    transform: scale(1.02) !important;
}

/* Buttons - FIXED */
.stButton > button {
    background: linear-gradient(135deg, #ff00ff20, #00ffff30, #00ff9d20) !important;
    backdrop-filter: blur(15px);
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 14px 35px !important;
    border: 2px solid transparent !important;
    border-radius: 50px !important;
    box-shadow: 
        0 8px 25px rgba(0, 255, 255, 0.3),
        0 0 30px rgba(255, 0, 255, 0.2),
        inset 0 0 20px rgba(255, 255, 255, 0.1) !important;
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 1px !important;
    position: relative;
    overflow: hidden;
    transition: all 0.4s ease !important;
}

.stButton > button:hover {
    border-color: #00ffff !important;
    box-shadow: 
        0 12px 35px rgba(0, 255, 255, 0.5),
        0 0 40px rgba(255, 0, 255, 0.4),
        inset 0 0 30px rgba(255, 255, 255, 0.2) !important;
    transform: translateY(-3px) scale(1.05) !important;
}

/* Fix all other elements visibility */
h1, h2, h3, h4, h5, h6, p, div, span, label {
    color: #e0e0ff !important;
    text-shadow: 0 0 5px rgba(224, 224, 255, 0.3) !important;
    z-index: 10 !important;
    position: relative !important;
}

/* Download buttons */
.stDownloadButton > button {
    background: linear-gradient(135deg, #00ff9d20, #00ffff40) !important;
    border-color: #00ff9d !important;
    color: #000 !important;
}

/* Success/Error - FIXED */
.stSuccess, .stError, .stWarning, .stInfo {
    backdrop-filter: blur(15px) !important;
    border-radius: 15px !important;
    border: 2px solid !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    margin: 15px 0 !important;
}

/* Dataframe fix */
[data-testid="stDataFrame"] {
    border-radius: 15px !important;
    border: 2px solid rgba(0, 255, 255, 0.3) !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
}

/* Footer fix */
div[style*="text-align:center"] {
    background: rgba(10, 10, 20, 0.8) !important;
    backdrop-filter: blur(20px);
    border: 2px solid rgba(0, 255, 255, 0.3) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    margin-top: 40px !important;
}
</style>
""", unsafe_allow_html=True)
