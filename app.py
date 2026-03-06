import os
import random
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
st.set_page_config(page_title="Scamino", layout="centered", initial_sidebar_state="collapsed")

# --- PREMIUM MOBILE-FIRST CSS ---
st.markdown("""
    <style>
    /* Hide default Streamlit top padding for an app-like feel */
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 720px; }
    
    /* Typography */
    .app-title { font-size: 2.2rem; font-weight: 800; color: #0f172a; letter-spacing: -0.05em; margin-bottom: 0.2rem; }
    .app-subtitle { font-size: 1rem; color: #64748b; font-weight: 400; margin-bottom: 2rem; }
    
    /* Modern Result Card */
    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Pill Badges */
    .badge-container { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
    .badge { padding: 0.4rem 0.8rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
    
    .badge-High { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
    .badge-Medium { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
    .badge-Low { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
    .badge-threat { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
    
    /* Content Sections */
    .section-title { font-size: 0.85rem; text-transform: uppercase; color: #94a3b8; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: 0.05em; }
    .hook-text { font-size: 1.1rem; color: #1e293b; font-weight: 500; margin-bottom: 1.5rem; line-height: 1.5; }
    
    .action-box { background: #f8fafc; border-left: 4px solid #3b82f6; padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1.5rem; }
    .action-text { color: #0f172a; font-weight: 500; font-size: 0.95rem; margin: 0; }
    
    /* Defanged Link Terminal */
    .link-terminal { background: #0f172a; color: #38bdf8; font-family: monospace; padding: 1rem; border-radius: 8px; font-size: 0.85rem; word-break: break-all; margin-bottom: 1.5rem; }
    
    /* Buttons */
    div.stButton > button { background-color: #0f172a; color: white; border-radius: 12px; font-weight: 600; padding: 0.5rem 1rem; border: none; transition: all 0.2s; }
    div.stButton > button:hover { background-color: #1e293b; color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transform: translateY(-1px); }
    
    /* Mobile Adjustments */
    @media (max-width: 600px) {
        .app-title { font-size: 1.8rem; }
        .result-card { padding: 1.2rem; }
        .hook-text { font-size: 1rem; }
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "sample_text" not in st.session_state:
    st.session_state.sample_text = ""
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

def set_example(text):
    st.session_state.sample_text = text

# --- APP HEADER ---
st.markdown('<div class="app-title">Scamino</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Smarter Threat Detection. Safer Inbox.</div>', unsafe_allow_html=True)

# --- TABS ---
tab1, tab2 = st.tabs(["Analyze Text", "Analyze Image"])

# === AI PARSER ===
def analyze_content(content, type="text"):
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    prompt = f"""
    Act as a senior cybersecurity analyst. Analyze this {type} strictly.
    Input: {content}
    
    Output ONLY these 6 lines. Do not add bolding or extra text.
    Line 1: RISK_LEVEL (Must be exactly: High, Medium, or Low)
    Line 2: THREAT_TYPE (Max 3 words, e.g., 'Phishing', 'Tech Support Scam', 'Safe')
    Line 3: THE_HOOK (1 short clinical sentence explaining the psychological trick.)
    Line 4: RED_FLAGS (List 3 distinct flaws separated by commas)
    Line 5: EXTRACTED_LINKS (Find any URLs or domains. If found, "defang" them like hXXp://badsite[.]com. If none, write "None found".)
    Line 6: RECOMMENDED_ACTION (1 clear sentence on what to do next.)
    """
    
    if type == "image":
        response = model.generate_content([prompt, content])
    else:
        response = model.generate_content(prompt)
        
    return response.text

# === MODERN RENDER ENGINE (Fixed Indentation) ===
def render_app_card(result):
    lines = result.split('\n')
    lines = [l.replace('**', '').strip() for l in lines if l.strip()] 
    
    if len(lines) >= 6:
        risk = lines[0].replace("Line 1:", "").strip()
        threat = lines[1].replace("Line 2:", "").strip()
        hook = lines[2].replace("Line 3:", "").strip()
        flags = lines[3].replace("Line 4:", "").strip().split(',')
        links = lines[4].replace("Line 5:", "").strip()
        action = lines[5].replace("Line 6:", "").strip()

        risk_class = "High" if "High" in risk else "Medium" if "Medium" in risk else "Low"
        
        html_card = f"""<div class="result-card">
<div class="badge-container">
<span class="badge badge-{risk_class}">{risk} RISK</span>
<span class="badge badge-threat">{threat}</span>
</div>
<div class="section-title">Analysis</div>
<div class="hook-text">{hook}</div>
"""
        
        if links.lower() not in ["none found", "none"]:
            html_card += f"""<div class="section-title">Suspicious Destination Detected</div>
<div class="link-terminal">{links}</div>
"""
            
        html_card += f"""<div class="section-title">Next Step</div>
<div class="action-box">
<p class="action-text">{action}</p>
</div>
<div class="section-title">Evidence Found</div>
<ul style="color: #475569; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0.5rem;">
"""
        for flag in flags:
            html_card += f"<li>{flag.strip()}</li>\n"
            
        html_card += "</ul></div>"
        
        st.markdown(html_card, unsafe_allow_html=True)
        
        st.session_state.scan_history.insert(0, {"threat": threat, "risk": risk, "hook": hook})
        if len(st.session_state.scan_history) > 3:
            st.session_state.scan_history.pop()
            
    else:
        st.error("Could not process request. Please try again.")
        with st.expander("Raw AI Output"):
            st.write(result)

# === TAB 1: TEXT ===
with tab1:
    # 1. HIDE DEMOS IN AN EXPANDER SO IT'S CLEAR THEY ARE JUST EXAMPLES
    with st.expander("💡 Don't have a suspicious message? Try a demo"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📦 Load Fake Delivery Demo"):
                set_example("USPS: Your package is on hold due to a missing street number. Please update your info here: http://usps-tracking-update-hub.com")
        with col2:
            if st.button("🏦 Load Bank Alert Demo"):
                set_example("CHASE BANK: Your account #8892 has been locked. Verify identity at https://chase-secure-auth.net.")
        
        if st.button("🧹 Clear Box", use_container_width=True):
            set_example("")
            
    # 2. CLEAR INSTRUCTIONS FOR THE USER'S OWN TEXT
    st.markdown('<p style="font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; margin-top: 1rem;">Analyze Your Message</p>', unsafe_allow_html=True)
    text_input = st.text_area(
        "Paste your suspicious text, email, or URL here:", 
        value=st.session_state.sample_text,
        height=140, 
        placeholder="Paste your text here...",
        label_visibility="collapsed"
    )
    
    if st.button("Scan Content", use_container_width=True):
        if text_input:
            with st.spinner("Analyzing..."):
                try:
                    result = analyze_content(text_input, "text")
                    render_app_card(result)
                except Exception as e:
                    st.error(f"API Connection Error: {e}")

# === TAB 2: IMAGE ===
with tab2:
    st.markdown('<p style="font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Upload Screenshot</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload an image file", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        # 3. SHRINK THE IMAGE BY WRAPPING IT IN A CENTERED COLUMN
        col_spacer1, col_img, col_spacer2 = st.columns([1, 2, 1])
        with col_img:
            st.image(image, caption='Image Preview', use_container_width=True)
        
        if st.button("Scan Image", use_container_width=True):
            with st.spinner("Analyzing visuals..."):
                try:
                    result = analyze_content(image, "image")
                    render_app_card(result)
                except Exception as e:
                    st.error(f"API Connection Error: {e}")

# --- RECENT SCANS (HISTORY) ---
if st.session_state.scan_history:
    st.markdown('<div style="margin-top: 3rem;" class="section-title">Recent Scans</div>', unsafe_allow_html=True)
    for item in st.session_state.scan_history:
        color = "#ef4444" if item['risk'] == "High" else "#f59e0b" if item['risk'] == "Medium" else "#22c55e"
        st.markdown(f"""
            <div style="padding: 0.8rem; border-bottom: 1px solid #f1f5f9; display: flex; align-items: center; gap: 1rem;">
                <div style="width: 10px; height: 10px; border-radius: 50%; background-color: {color};"></div>
                <div style="flex-grow: 1;">
                    <div style="font-weight: 600; font-size: 0.9rem; color: #0f172a;">{item['threat']}</div>
                    <div style="font-size: 0.8rem; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 250px;">{item['hook']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)