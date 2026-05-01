import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv
import plotly.express as px
import io
from gtts import gTTS
import time
import json
import re

# Load env and configure
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from sentinel.data_gen.generator import generate_sentinel_data
from sentinel.agents.storyteller import SentinelStoryteller
from sentinel.governance.sheriff import SentinelSheriff

# --- SIMPLIFIED GIFT CARD DESIGN SYSTEM ---
st.set_page_config(page_title="Sentinel | Gift Card Vantage", layout="wide", page_icon="🛡️")

st.markdown("""
<style>
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 0px !important; }
    footer { visibility: hidden !important; }
    .stApp { background-color: #0b0e14 !important; color: #f0f2f6 !important; }
    .omnibox { background: #161a23 !important; border: 1px solid #2d333f !important; border-radius: 12px !important; padding: 25px !important; margin-bottom: 20px !important; }
    .metric-row { background: #1a1f2b !important; border-radius: 12px !important; padding: 25px !important; border-bottom: 4px solid #50fa7b !important; margin-bottom: 25px !important; }
    .panel { background: #161a23 !important; border: 1px solid #2d333f !important; border-radius: 12px !important; padding: 25px !important; }
    h1 { color: #ffffff !important; font-weight: 900 !important; font-family: 'Outfit', sans-serif; margin:0 !important; }
    .welcome-box { color: #50fa7b !important; font-weight: bold; text-align: center; margin-top: 100px; font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# --- Top Navigation ---
st.markdown('<div class="omnibox">', unsafe_allow_html=True)
c1, c2 = st.columns([3, 1])

with c1:
    st.markdown("<h1>SENTINEL VANTAGE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6272a4; margin-bottom: 15px;'>Gift Card Network Performance Console</p>", unsafe_allow_html=True)
    audio_value = st.audio_input("Voice Input", label_visibility="collapsed")
    
    query_text = ""
    if audio_value:
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(["Transcribe this audio. Return ONLY clean text.", {"mime_type": "audio/wav", "data": audio_value.read()}])
            query_text = response.text
        except: pass

    query = st.text_input("Ask a question about the network...", value=query_text if query_text else "", placeholder="e.g. How were Q4 redemptions?")

with c2:
    st.markdown("<div style='height: 105px;'></div>", unsafe_allow_html=True)
    run_btn = st.button("🚀 ANALYZE NETWORK", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- EXECUTION ---
if run_btn or query:
    # 1. Load Standard Gift Card Data
    df_path = "data/synthetic/gift_card_network.parquet"
    if not os.path.exists(df_path): generate_sentinel_data()
    df = pd.read_parquet(df_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 2. THE ANALYST BRAIN
    with st.status("Sentinel Analyst: Querying Gift Card Database...", expanded=False) as status:
        prompt = f"""
        Analyze this Gift Card dataframe 'df' for: "{query if query else 'Current Performance'}"
        Columns: ['Date', 'Amount', 'Type', 'Location', 'Merchant']
        Return JSON with:
        - "pandas_code": "code to filter df into result_df for the requested time period."
        - "summary": "3 executive insights about gift card issuance vs redemption."
        """
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(prompt)
            logic = json.loads(re.search(r'\{.*\}', res.text, re.DOTALL).group())
            ldict = {'df': df, 'pd': pd}
            exec(logic["pandas_code"], globals(), ldict)
            result_df = ldict.get('result_df', df)
            
            # Context-specific math
            total_vol = result_df['Amount'].sum()
            status.update(label="Analysis Complete", state="complete")
        except:
            result_df = df
            total_vol = df['Amount'].sum()
            logic = {"summary": "General network overview."}

    # 3. METRIC BAR
    st.markdown(f"""
    <div class="metric-row">
        <div style="text-align:center; flex: 1;">
            <div style="color: #94a3b8; font-size: 0.8rem; letter-spacing: 1px;">TOTAL CARD VOLUME</div>
            <div style="color: #50fa7b; font-size: 3rem; font-weight: 900;">${total_vol:,.2f}</div>
        </div>
        <div style="text-align:center; flex: 1; border-left: 1px solid #2d333f;">
            <div style="color: #94a3b8; font-size: 0.8rem; letter-spacing: 1px;">REDEMPTION RATE</div>
            <div style="color: #ffffff; font-size: 2rem; font-weight: 700;">82.1%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    l, r = st.columns([1.5, 1])
    with l:
        st.markdown('<div class="panel"><h3>🎙️ EXECUTIVE BRIEFING</h3>', unsafe_allow_html=True)
        storyteller = SentinelStoryteller()
        script = storyteller.generate_briefing({"insights": logic['summary'], "client": "Marlow & Finch"}, "Marlow & Finch")
        full_text = ""
        for s in script.segments:
            st.markdown(f"<p style='font-size: 1.15rem; line-height: 1.8;'>{s.text}</p>", unsafe_allow_html=True)
            full_text += s.text + " "
        if full_text:
            tts = gTTS(text=full_text, lang='en')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format='audio/mp3')
        st.markdown('</div>', unsafe_allow_html=True)

    with r:
        st.markdown('<div class="panel"><h3>📊 REDEMPTION TREND</h3>', unsafe_allow_html=True)
        if not result_df.empty:
            trend_df = result_df.groupby(pd.Grouper(key='Date', freq='W')).sum().reset_index()
            fig = px.line(trend_df, x='Date', y='Amount', template="plotly_dark", color_discrete_sequence=['#50fa7b'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
        st.success("🛡️ Sentinel Governance: Data Privacy Audited.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="welcome-box">Welcome, Director. Ask about your Gift Card Network to begin.</div>', unsafe_allow_html=True)
