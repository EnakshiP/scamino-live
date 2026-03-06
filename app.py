import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- SECURE API KEY SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("System Error: API Key missing from secure vault.")
    st.stop()

genai.configure(api_key=api_key)

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Scamina", layout="centered")

# --- PROFESSIONAL CUSTOM CSS ---
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 600; color: #1e293b; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #64748b; margin-bottom: 2rem; font-weight: 400; }
    
    /* Risk Banners */
    .banner-High { background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 1.2rem; border-radius: 6px; margin-bottom: 1rem;}
    .banner-Medium { background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 1.2rem; border-radius: 6px; margin-bottom: 1rem;}
    .banner-Low { background-color: #f0fdf4; border-left: 4px solid #22c55e; padding: 1.2rem; border-radius: 6px; margin-bottom: 1rem;}
    
    .text-High { color: #b91c1c; font-weight: 600; margin: 0; font-size: 1.2rem;}
    .text-Medium { color: #b45309; font-weight: 600; margin: 0; font-size: 1.2rem;}
    .text-Low { color: #15803d; font-weight: 600; margin: 0; font-size: 1.2rem;}
    
    /* Action & Summary Boxes */
    .summary-box { border-left: 3px solid #94a3b8; padding-left: 1rem; color: #334155; margin: 1.5rem 0; font-size: 1.05rem; }
    .action-box { background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 1rem; border-radius: 6px; color: #0f172a; margin-top: 1rem; font-weight: 500;}
    
    /* Microcopy */
    .microcopy { font-size: 0.85rem; color: #64748b; margin-top: 0.5rem; }
    
    /* Clean Buttons */
    div.stButton > button { width: 100%; border-radius: 6px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE FOR EXAMPLES ---
if "sample_text" not in st.session_state:
    st.session_state.sample_text = ""

def set_example(text):
    st.session_state.sample_text = text

# --- HEADER SECTION ---
st.markdown('<div class="main-header">Scamina</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Threat & Fraud Analysis</div>', unsafe_allow_html=True)

# --- TABS ---
tab1, tab2 = st.tabs(["Text Analysis", "Image Analysis"])

# === HELPER FUNCTION: PARSE AI RESPONSE ===
def analyze_content(content, type="text"):
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    prompt = f"""
    Act as a senior cybersecurity analyst. Analyze this {type} strictly.
    Input: {content}
    
    Output ONLY these 5 lines. Do not add bolding or extra text.
    Line 1: RISK_LEVEL (Must be exactly: High, Medium, or Low)
    Line 2: VERDICT (Max 3 words, e.g., 'Phishing Attempt', 'Safe Communication')
    Line 3: THE_HOOK (1 short clinical sentence explaining the scam's psychological trick.)
    Line 4: RED_FLAGS (List 3 distinct flaws separated by commas)
    Line 5: RECOMMENDED_ACTION (1 sentence telling the user exactly what to do next, e.g., 'Do not click the link and block the sender immediately.')
    """
    
    if type == "image":
        response = model.generate_content([prompt, content])
    else:
        response = model.generate_content(prompt)
        
    return response.text

# === DISPLAY LOGIC ===
def render_report(result):
    lines = result.split('\n')
    lines = [l for l in lines if l.strip()] 
    
    if len(lines) >= 5: # Now expecting 5 lines
        risk = lines[0].replace("Line 1:", "").strip()
        verdict = lines[1].replace("Line 2:", "").strip()
        hook = lines[2].replace("Line 3:", "").strip()
        flags = lines[3].replace("Line 4:", "").strip().split(',')
        action = lines[4].replace("Line 5:", "").strip()

        st.divider()
        
        # Determine CSS classes based on risk
        risk_class = "High" if "High" in risk else "Medium" if "Medium" in risk else "Low"
        
        # 1. The Verdict
        st.markdown(f"""
            <div class="banner-{risk_class}">
                <p class="text-{risk_class}">Verdict: {verdict.title()}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 2. What they want
        st.markdown(f"""
            <div class="summary-box">
                <strong>Analysis:</strong> {hook}
            </div>
        """, unsafe_allow_html=True)
        
        # 3. Action Plan (NEW)
        st.markdown(f"""
            <div class="action-box">
                🛡️ <strong>Recommended Action:</strong><br> {action}
            </div>
        """, unsafe_allow_html=True)
        
        # 4. Evidence
        st.markdown("<br><strong>Identified Risk Factors:</strong>", unsafe_allow_html=True)
        for flag in flags:
            st.markdown(f"- {flag.strip()}")
            
        # 5. Share Warning (NEW - Only for High/Medium risk)
        if risk_class in ["High", "Medium"]:
            st.divider()
            st.markdown("**Help protect others:** Copy this warning to share with family or colleagues.")
            safe_warning = f"⚠️ *Security Alert:* I just received a suspicious message claiming to be '{verdict}'. Scamina flagged it as a {risk} risk. Please be careful and do not click any links if you receive something similar!"
            st.code(safe_warning, language="markdown")
            
    else:
        st.error("System could not parse the analysis format. Please retry.")
        with st.expander("View Raw Output"):
            st.write(result)

# === TAB 1: TEXT ===
with tab1:
    # Example Chips
    st.markdown('<p class="microcopy">New to Scamina? Try an example scenario:</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📦 Fake Delivery"):
            set_example("USPS: Your package is on hold due to a missing street number. Please update your info here: http://usps-tracking-update-hub.com")
    with col2:
        if st.button("🏦 Bank Alert"):
            set_example("CHASE BANK: Your account #8892 has been temporarily locked due to suspicious activity. Verify your identity immediately at https://chase-secure-auth.net to avoid closure.")
    with col3:
        if st.button("🧹 Clear Box"):
            set_example("")
            
    text_input = st.text_area(
        "Input Message Text:", 
        value=st.session_state.sample_text,
        height=120, 
        placeholder="Paste the suspicious text, email, or URL here..."
    )
    
    if st.button("Initiate Scan", key="text_scan", type="primary"):
        if text_input:
            with st.spinner("Analyzing linguistic patterns & threat indicators..."):
                try:
                    result = analyze_content(text_input, "text")
                    render_report(result)
                except Exception as e:
                    st.error(f"API Connection Error: {e}")

# === TAB 2: IMAGE ===
with tab2:
    uploaded_file = st.file_uploader("Upload Image Document (Screenshot of SMS/Email)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Document Preview', width='stretch')
        
        if st.button("Initiate Scan", key="image_scan", type="primary"):
            with st.spinner("Analyzing visual artifacts & embedded text..."):
                try:
                    result = analyze_content(image, "image")
                    render_report(result)
                except Exception as e:
                    st.error(f"API Connection Error: {e}")