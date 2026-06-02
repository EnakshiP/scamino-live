import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- SECURE API KEY SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ System Setup Missing: Google API Key not found in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Fraud Guard", page_icon="🛡️", layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM PREMIUM CONSUMER CSS ---
st.markdown("""
    <style>
    /* Maximize scannability and constrain modern layout */
    .block-container { padding-top: 2.5rem !important; padding-bottom: 2rem !important; max-width: 680px; }
    
    /* Consumer-friendly Card UI */
    .friendly-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Dynamic Threat Borders */
    .border-high { border-left: 6px solid #ef4444; }
    .border-medium { border-left: 6px solid #f59e0b; }
    .border-low { border-left: 6px solid #10b981; }
    
    /* Text Typography */
    .card-header { font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem; }
    .text-high { color: #dc2626; }
    .text-medium { color: #d97706; }
    .text-low { color: #059669; }
    
    .card-verdict { font-size: 1.6rem; font-weight: 800; color: #0f172a; margin-bottom: 1rem; }
    .section-lbl { font-size: 0.9rem; font-weight: 700; color: #64748b; margin-top: 1rem; margin-bottom: 0.25rem; }
    .section-desc { font-size: 1.05rem; color: #1e293b; line-height: 1.5; margin-bottom: 1.2rem; }
    
    /* Custom Stylized Button */
    div.stButton > button { 
        background-color: #2563eb; 
        color: white; 
        border-radius: 12px; 
        font-weight: 600; 
        padding: 0.6rem 1rem; 
        border: none;
        transition: all 0.2s;
    }
    div.stButton > button:hover { background-color: #1d4ed8; color: white; transform: translateY(-1px); }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SAMPLE TEXT STATE ---
if "helper_text" not in st.session_state:
    st.session_state.helper_text = ""

def trigger_example(text):
    st.session_state.helper_text = text

# --- HEADER ---
st.markdown('<h1 style="text-align: center; font-weight: 800; color: #0f172a; margin-bottom: 0px;">🛡️ Fraud Guard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">Your friendly neighborhood shield against scams, tricks, and fake messages.</p>', unsafe_allow_html=True)

# --- TABS ---
tab1, tab2 = st.tabs(["💬 Check a Message", "🖼️ Check a Screenshot"])

# === ENGINE: ANALYZE PATTERNS ===
def analyze_content(content, type="text"):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Act as an empathetic consumer security assistant. Analyze this {type} cleanly.
    Input: {content}
    
    Output ONLY these 4 lines. Do not add bolding, stars, or extra text.
    Line 1: RISK_LEVEL (Must be exactly: High, Medium, or Low)
    Line 2: VERDICT (Max 3 friendly words, e.g., 'Dangerous Scam', 'Suspicious Offer', 'Looks Safe')
    Line 3: THE_HOOK (1 short clear sentence for everyday individuals explaining what the text wants from them.)
    Line 4: RED_FLAGS (List 3 simple reasons/clues separated by commas)
    """
    
    if type == "image":
        response = model.generate_content([prompt, content])
    else:
        response = model.generate_content(prompt)
    return response.text

# === PRESENTATION ENGINE: RENDER USER FRIENDLY CARD ===
def show_friendly_results(ai_raw_output):
    lines = ai_raw_output.split('\n')
    lines = [l.replace('**', '').strip() for l in lines if l.strip()]
    
    if len(lines) >= 4:
        risk = lines.replace("Line 1:", "").strip()
        verdict = lines.replace("Line 2:", "").strip()
        hook = lines.replace("Line 3:", "").strip()
        flags = lines.replace("Line 4:", "").strip().split(',')
        
        # Determine styling weights based on friendliness parameters
        style_key = "high" if "High" in risk else "medium" if "Medium" in risk else "low"
        alert_prefix = "🚨" if style_key == "high" else "⚠️" if style_key == "medium" else "✅"
        
        # Left-flushed HTML rendering block to guarantee clean execution
        html_output = f"""<div class="friendly-card border-{style_key}">
<div class="card-header text-{style_key}">{risk} Safety Assessment</div>
<div class="card-verdict">{alert_prefix} {verdict}</div>

<div class="section-lbl">What is happening here?</div>
<div class="section-desc">{hook}</div>

<div class="section-lbl">Clues & Warning Signs to notice:</div>
<ul style="color: #334155; font-size: 1rem; padding-left: 1.2rem; margin-top: 0.2rem; line-height: 1.6;">
"""
        for flag in flags:
            html_output += f"<li>{flag.strip()}</li>\n"
            
        html_output += "</ul></div>"
        
        st.markdown(html_output, unsafe_allow_html=True)
    else:
        st.error("We encountered trouble reading this item. Please try running the check again.")

# === TAB 1: TEXT MESSAGES ===
with tab1:
    # Gentle onboarding tool
    with st.expander("💡 Not sure how it works? Test a simulated example"):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📦 Simulated Delivery Trap", use_container_width=True):
                trigger_example("Your package delivery status is pending. To update delivery destination address fees follow: link-unsafe.com")
        with c2:
            if st.button("🚨 Simulated Bank Alert", use_container_width=True):
                trigger_example("Urgent: Unusual transaction detected on your card. Click immediately to stop transfer: safety-auth-verify.net")
    
    st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: #334155; margin-bottom: 4px;">Paste the text or links you want to verify:</p>', unsafe_allow_html=True)
    text_box = st.text_area(
        label="Input Box",
        value=st.session_state.helper_text,
        height=130,
        placeholder="Paste a suspicious email, text message, or weird link here...",
        label_visibility="collapsed"
    )
    
    if st.button("Scan Message", use_container_width=True):
        if text_box:
            with st.spinner("Carefully reading details..."):
                try:
                    raw_report = analyze_content(text_box, "text")
                    show_friendly_results(raw_report)
                except Exception as e:
                    st.error("Could not link with our protection systems right now.")

# === TAB 2: SCREENSHOTS ===
with tab2:
    st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: #334155; margin-bottom: 8px;">Upload a picture or screenshot of the message:</p>', unsafe_allow_html=True)
    screenshot_file = st.file_uploader("Upload Box", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if screenshot_file:
        img_object = Image.open(screenshot_file)
        
        # Center and reduce screenshot preview footprint to prevent visual clutter
        left_pad, center_pane, right_pad = st.columns()
        with center_pane:
            st.image(img_object, caption='Your Screenshot Preview', use_container_width=True)
            
        if st.button("Scan Screenshot", use_container_width=True):
            with st.spinner("Examining image details closely..."):
                try:
                    raw_report = analyze_content(img_object, "image")
                    show_friendly_results(raw_report)
                except Exception as e:
                    st.error("Could not run image analysis systems right now.")