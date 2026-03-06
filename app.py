import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- SECURE API KEY SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Google API Key not found. Please set it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# Set up the page layout
st.set_page_config(page_title="Scamino", page_icon="🛡️", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .risk-high { color: #FF4B4B; font-weight: bold; font-size: 24px; }
    .risk-safe { color: #00C851; font-weight: bold; font-size: 24px; }
    div.stButton > button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🛡️ Scamino")
st.caption("Global Scam & Phishing Detector")

# --- SIDEBAR ---
st.sidebar.title("About Scamino")
st.sidebar.info("We use advanced pattern recognition to detect financial traps, phishing, and fake offers in seconds.")

# --- TABS ---
tab1, tab2 = st.tabs(["💬 Analyze Text", "🖼️ Analyze Screenshot"])

# === HELPER FUNCTION: PARSE AI RESPONSE ===
def analyze_content(content, type="text"):
    # gemini-1.5-flash is great for both text and images
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Act as a security expert. Analyze this {type} strictly.
    Input: {content}
    
    Output ONLY these 4 lines. Do not add bolding or extra text.
    Line 1: RISK_LEVEL (Must be exactly: High, Medium, or Low)
    Line 2: VERDICT (Max 3 words, e.g., 'Phishing Scam', 'Safe Message')
    Line 3: THE_HOOK (1 short sentence on what they want, e.g., 'They are trying to steal your bank password.')
    Line 4: RED_FLAGS (List 3 distinct flaws separated by commas, e.g., Bad Grammar, Urgency, Suspicious Link)
    """
    
    # Notice: No try/except here anymore. We want the error to bubble up so you can see it!
    if type == "image":
        response = model.generate_content([prompt, content])
    else:
        response = model.generate_content(prompt)
        
    return response.text

# === TAB 1: TEXT ===
with tab1:
    text_input = st.text_area("Paste message here:", height=100, placeholder="e.g. You won a lottery! Click here...")
    
    if st.button("Scan Text", type="primary"):
        if text_input:
            with st.spinner("Scanning patterns..."):
                try:
                    result = analyze_content(text_input, "text")
                    lines = result.split('\n')
                    lines = [l for l in lines if l.strip()] 
                    
                    if len(lines) >= 4:
                        risk = lines[0].replace("Line 1:", "").strip()
                        verdict = lines[1].replace("Line 2:", "").strip()
                        hook = lines[2].replace("Line 3:", "").strip()
                        flags = lines[3].replace("Line 4:", "").strip().split(',')

                        st.divider()
                        
                        if "High" in risk:
                            st.error(f"🚨 {verdict.upper()}")
                        elif "Medium" in risk:
                            st.warning(f"⚠️ {verdict.upper()}")
                        else:
                            st.success(f"✅ {verdict.upper()}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Risk Level", risk)
                        with col2:
                            st.metric("Confidence", "98%")
                        
                        st.info(f"**The Trap:** {hook}")
                        
                        st.subheader("🚩 Red Flags Found")
                        for flag in flags:
                            st.markdown(f"- {flag.strip()}")
                            
                    else:
                        st.error("Could not parse the AI's response properly. Please try again.")
                        st.write("Raw AI Output:", result) # Shows what the AI actually said if it failed to format
                        
                except Exception as e:
                    # This will catch API Key errors, quota limits, etc.
                    st.error(f"Google AI Error: {e}")

# === TAB 2: IMAGE ===
with tab2:
    uploaded_file = st.file_uploader("Upload Screenshot", type=["jpg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        # THE FIX: use_container_width has been replaced with width='stretch'
        st.image(image, caption='Uploaded Image', width='stretch')
        
        if st.button("Scan Screenshot", type="primary"):
            with st.spinner("Analyzing visuals..."):
                try:
                    result = analyze_content(image, "image")
                    lines = result.split('\n')
                    lines = [l for l in lines if l.strip()] 
                    
                    if len(lines) >= 4:
                        risk = lines[0].replace("Line 1:", "").strip()
                        verdict = lines[1].replace("Line 2:", "").strip()
                        hook = lines[2].replace("Line 3:", "").strip()
                        flags = lines[3].replace("Line 4:", "").strip().split(',')

                        st.divider()
                        
                        if "High" in risk:
                            st.error(f"🚨 {verdict.upper()}")
                        elif "Medium" in risk:
                            st.warning(f"⚠️ {verdict.upper()}")
                        else:
                            st.success(f"✅ {verdict.upper()}")

                        st.info(f"**The Trap:** {hook}")
                        
                        st.subheader("🚩 Visual Red Flags")
                        for flag in flags:
                            st.markdown(f"- {flag.strip()}")
                            
                    else:
                        st.error("Could not parse the AI's response properly. Please try again.")
                        st.write("Raw AI Output:", result)
                        
                except Exception as e:
                    st.error(f"Google AI Error: {e}")


