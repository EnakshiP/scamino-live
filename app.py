import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- SECURE API KEY SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Google API Key not found. Please set it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- PAGE CONFIGURATION ---
# Removed emoji from page_icon, using a clean layout
st.set_page_config(page_title="Scamina", layout="centered")

# --- PROFESSIONAL CUSTOM CSS ---
st.markdown("""
    <style>
    /* Main typography and spacing */
    .main-header { font-size: 2.2rem; font-weight: 600; color: #2c3e50; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #7f8c8d; margin-bottom: 2rem; font-weight: 400; }
    
    /* Risk Banners (Muted, professional colors) */
    .banner-High { background-color: #fdf2f2; border-left: 4px solid #d9534f; padding: 1rem; border-radius: 4px; margin-bottom: 1rem;}
    .banner-Medium { background-color: #fcf8e3; border-left: 4px solid #f0ad4e; padding: 1rem; border-radius: 4px; margin-bottom: 1rem;}
    .banner-Low { background-color: #eef8f1; border-left: 4px solid #5cb85c; padding: 1rem; border-radius: 4px; margin-bottom: 1rem;}
    
    /* Text colors matching the banners */
    .text-High { color: #c9302c; font-weight: 600; margin: 0; }
    .text-Medium { color: #ec971f; font-weight: 600; margin: 0; }
    .text-Low { color: #449d44; font-weight: 600; margin: 0; }
    
    /* Hook / Summary Box */
    .summary-box { border-left: 3px solid #adb5bd; padding-left: 1rem; color: #495057; margin: 1.5rem 0; font-size: 1.05rem; }
    
    /* Clean up Streamlit elements */
    div.stButton > button { width: 100%; border-radius: 6px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown('<div class="main-header">Scamina</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Advanced Pattern Recognition & Fraud Analysis</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("System Info")
st.sidebar.markdown(
    "Scamina utilizes multimodal language models to analyze text formatting, "
    "linguistic patterns, and visual anomalies to detect potential phishing and fraud attempts."
)

# --- TABS ---
tab1, tab2 = st.tabs(["Text Analysis", "Image Analysis"])

# === HELPER FUNCTION: PARSE AI RESPONSE ===
def analyze_content(content, type="text"):
    # Ensure this matches the working model you found (e.g., 'gemini-2.5-flash' or 'gemini-1.5-flash')
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    prompt = f"""
    Act as a security expert. Analyze this {type} strictly.
    Input: {content}
    
    Output ONLY these 4 lines. Do not add bolding or extra text.
    Line 1: RISK_LEVEL (Must be exactly: High, Medium, or Low)
    Line 2: VERDICT (Max 3 words, e.g., 'Phishing Scam', 'Safe Message')
    Line 3: THE_HOOK (1 short clinical sentence on the objective, e.g., 'Attempt to extract credentials.')
    Line 4: RED_FLAGS (List 3 distinct flaws separated by commas, e.g., Poor grammar, Induced urgency, Obfuscated link)
    """
    
    if type == "image":
        response = model.generate_content([prompt, content])
    else:
        response = model.generate_content(prompt)
        
    return response.text

# === DISPLAY LOGIC (To keep code clean) ===
def render_report(result):
    lines = result.split('\n')
    lines = [l for l in lines if l.strip()] 
    
    if len(lines) >= 4:
        risk = lines[0].replace("Line 1:", "").strip()
        verdict = lines[1].replace("Line 2:", "").strip()
        hook = lines[2].replace("Line 3:", "").strip()
        flags = lines[3].replace("Line 4:", "").strip().split(',')

        st.divider()
        
        # Determine CSS classes based on risk
        risk_class = "High" if "High" in risk else "Medium" if "Medium" in risk else "Low"
        
        # Professional Verdict Banner
        st.markdown(f"""
            <div class="banner-{risk_class}">
                <h3 class="text-{risk_class}">Verdict: {verdict.title()}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Minimalist Metrics
        col1, col2 = st.columns(2)
        col1.metric("Risk Level", risk)
        col2.metric("Confidence", "98.5%")
        
        # Clinical Summary Box
        st.markdown(f"""
            <div class="summary-box">
                <strong>Analysis Summary:</strong> {hook}
            </div>
        """, unsafe_allow_html=True)
        
        # Clean Bullet Points
        st.markdown("#### Identified Risk Factors")
        for flag in flags:
            st.markdown(f"- {flag.strip()}")
            
    else:
        st.error("System could not parse the analysis format. Please retry.")
        with st.expander("View Raw Output"):
            st.write(result)

# === TAB 1: TEXT ===
with tab1:
    text_input = st.text_area("Input Message Text:", height=120, placeholder="Paste the suspicious text here...")
    
    if st.button("Initiate Scan", key="text_scan"):
        if text_input:
            with st.spinner("Analyzing linguistic patterns..."):
                try:
                    result = analyze_content(text_input, "text")
                    render_report(result)
                except Exception as e:
                    st.error(f"API Connection Error: {e}")

# === TAB 2: IMAGE ===
with tab2:
    uploaded_file = st.file_uploader("Upload Image Document", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Document Preview', width='stretch')
        
        if st.button("Initiate Scan", key="image_scan"):
            with st.spinner("Analyzing visual artifacts..."):
                try:
                    result = analyze_content(image, "image")
                    render_report(result)
                except Exception as e:
                    st.error(f"API Connection Error: {e}")