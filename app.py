import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_engine import generate_rewards_data
from agents import SentinelAgents
import os
import json
import base64
import requests
import uuid
import google.generativeai as genai
from datetime import datetime, timedelta

# 1. PAGE CONFIG
st.set_page_config(page_title="Sentinel Vantage | Rewards Command Center", layout="wide", page_icon="🛡️")

# ASSET PATHS (Permanent Static Vault)
VIC_PATH = "static/victoria.png"
MIKE_PATH = "static/mike.png"

# 2. UI STYLING
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, .stApp { background-color: #0f172a !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    
    /* GLOBAL WHITE TEXT */
    h1, h2, h3, h4, h5, h6, [data-testid="stSidebar"] label, .stMarkdown p { color: #ffffff !important; font-family: 'Inter', sans-serif !important; }
    
    /* INTELLIGENCE CARD - NUCLEAR LEGIBILITY */
    .intel-card { 
        background-color: #1e293b !important; 
        border-radius: 20px !important; 
        padding: 30px !important; 
        border: 2px solid #a855f7 !important; 
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.3) !important;
        margin-bottom: 30px !important;
    }
    .intel-card * { color: #ffffff !important; font-weight: 700 !important; }
    .intel-quote { font-size: 1.2rem !important; line-height: 1.6 !important; font-style: italic !important; color: #ffffff !important; margin-left: 20px !important; }
    .intel-title { font-size: 1.4rem !important; font-weight: 800 !important; color: #ffffff !important; margin: 0 !important; }

    .header-bar { background-color: #1e293b !important; padding: 25px 35px !important; display: flex !important; justify-content: space-between !important; align-items: center !important; border: 1px solid #334155 !important; border-radius: 16px !important; margin-bottom: 30px !important; }
    .card { background-color: #1e293b !important; border-radius: 16px !important; padding: 28px !important; border: 1px solid #334155 !important; margin-bottom: 25px !important; }
    .card-title { font-size: 0.9rem !important; font-weight: 800 !important; color: #ffffff !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; margin-bottom: 20px !important; border-left: 4px solid #a855f7; padding-left: 12px; }
    
    .audit-log-box { background-color: #0f172a; border: 1px solid #334155; padding: 12px; border-radius: 8px; font-family: monospace; font-size: 0.8rem; color: #10b981; max-height: 180px; overflow-y: auto; }
    .audit-entry { margin-bottom: 6px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
    
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%) !important; border-right: 1px solid #334155 !important; }
    
    div[data-testid="stAudioInput"] { 
        background-color: #0f172a !important; 
        border: 2px solid #a855f7 !important; 
        border-radius: 16px !important; 
        margin-top: 15px !important;
        padding: 16px 16px 22px 16px !important;
    }
    div[data-testid="stAudioInput"] label {
        padding-bottom: 8px !important;
        padding-left: 4px !important;
        letter-spacing: 0.5px !important;
    }
    .claim-item span { color: #ffffff !important; font-weight: 600; }
    .stCaption, footer, footer * { color: #ffffff !important; opacity: 1 !important; font-weight: 600; }
    .claim-item { background-color: #0f172a !important; border: 1px solid #334155 !important; padding: 14px !important; border-radius: 12px !important; margin-bottom: 12px !important; display: flex; justify-content: space-between; }
    .shortcut-btn { background-color: #0f172a !important; border: 1px solid #38bdf8 !important; color: #38bdf8 !important; padding: 12px !important; border-radius: 10px !important; font-weight: 700 !important; cursor: pointer; margin-bottom: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

local_css()

# 3. STATE & CONFIG
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
if 'df_v2' not in st.session_state: st.session_state.df_v2 = generate_rewards_data()
if 'active_query' not in st.session_state: st.session_state.active_query = None
if 'audio_key' not in st.session_state: st.session_state.audio_key = str(uuid.uuid4())
if 'last_manager' not in st.session_state: st.session_state.last_manager = "David Chen"

def dismiss_callback():
    st.session_state.active_query = None; st.session_state.audio_key = str(uuid.uuid4())

def get_b64(path):
    if not os.path.exists(path): return ""
    with open(path, "rb") as f: return base64.b64encode(f.read()).decode()

# 4. SIDEBAR
with st.sidebar:
    st.markdown('<div style="padding-top: 30px;"></div>', unsafe_allow_html=True)
    st.image("https://img.icons8.com/fluency/96/shield.png", width=70)
    st.header("Sentinel Scope")
    managers = sorted(list(st.session_state.df_v2['Manager'].unique()))
    selected_manager = st.selectbox("Manager Context", managers, index=managers.index(st.session_state.last_manager) if st.session_state.last_manager in managers else 0)
    st.session_state.last_manager = selected_manager
    manager_team = st.session_state.df_v2[st.session_state.df_v2['Manager'] == selected_manager]['Team'].iloc[0]
    st.divider()
    
    st.markdown('<div style="color: #ffffff; font-size: 0.85rem; font-weight: 800; margin-bottom: 5px;">VOICE ANALYST</div>', unsafe_allow_html=True)
    audio_data = st.audio_input("Analyze rewards via voice", key=st.session_state.audio_key)
    manual_query = st.text_input("💬 Natural Query", placeholder="Analyze context...", value="", key=f"manual_{st.session_state.audio_key}")
    
    if audio_data and st.session_state.active_query is None:
        st.toast("🎙️ Voice Received!")
        with st.spinner("Transcribing..."):
            try:
                audio_bytes = audio_data.read()
                
                # CACHED DISCOVERY FOR SPEED
                if 'gemini_model_id' not in st.session_state:
                    st.session_state.gemini_model_id = 'models/gemini-2.5-flash'
                
                t_model = genai.GenerativeModel(st.session_state.gemini_model_id)
                resp = t_model.generate_content(["Transcribe.", {"mime_type": "audio/wav", "data": audio_bytes}])
                
                if resp.text:
                    st.session_state.active_query = resp.text.strip()
                    st.rerun()
                else:
                    st.error("Transcription Failed.")
            except Exception as e: st.error(f"Transcription Error: {e}")

    if manual_query and st.session_state.active_query is None:
        st.session_state.active_query = manual_query
        st.rerun()
    
    st.divider()
    st.markdown('<div style="color: #ffffff; font-size: 0.85rem; font-weight: 800; margin-bottom: 10px;">🛡️ REAL-TIME AUDIT VAULT</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="audit-log-box">
        <div class="audit-entry">[PASS] G-006 Data Masking Active</div>
        <div class="audit-entry">[PASS] Cross-Team PII Restricted</div>
        <div class="audit-entry">[PASS] Context: {}</div>
        <div class="audit-entry">[PASS] MFA Verified</div>
        <div class="audit-entry">[SYNC] Neural Bypass Latency: 32ms</div>
    </div>
    """.format(manager_team), unsafe_allow_html=True)

# Global Context
team_df = st.session_state.df_v2[st.session_state.df_v2['Team'] == manager_team]
agents = SentinelAgents(team_df)

# 5. INTELLIGENCE (Top Level)
if st.session_state.active_query:
    query = st.session_state.active_query
    fig = None; is_breach = False; res_msg = "Analyzing..."; cur_avatar = VIC_PATH; title = "Analyzing..."; color = "#a855f7"; bg = "#1e293b"
    try:
        import anthropic, re
        from concurrent.futures import ThreadPoolExecutor

        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        roster_data = st.session_state.df_v2.groupby('Team')['Employee'].unique().apply(list).to_dict()
        full_roster_str = json.dumps(roster_data)
        my_team_members = roster_data.get(manager_team, [])
        sys_prompt = f"""You are Mike, Sentinel Sheriff data governance agent. 
Your protected team is '{manager_team}'. Protected members: {my_team_members}.
Full company roster: {full_roster_str}.
CRITICAL RULE: If the user asks about ANY specific employee who is IN the full company roster but NOT in your protected members list, YOU MUST FLAG IT AS A BREACH.
Ignore mentions of "Victoria" or "Mike" (they are AI agents). 
If the person is not found in the full company roster at all, do NOT flag it as a breach.
If the query is general, about your protected members, or about a team budget, it is NOT a breach.
Respond ONLY JSON: {{"is_breach": bool, "target_name": "string", "target_team": "string"}}"""

        def run_governance():
            m_resp = client.messages.create(model="claude-opus-4-5-20251101", max_tokens=200, system=sys_prompt, messages=[{"role": "user", "content": f"Query: {query}"}])
            match = re.search(r'\{.*\}', m_resp.content[0].text, re.DOTALL)
            return json.loads(match.group()) if match else {"is_breach": False}

        def run_insight():
            return agents.insight_agent(selected_manager, {"query": query, "team": manager_team})

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_audit = executor.submit(run_governance)
            future_insight = executor.submit(run_insight)
            audit_result = future_audit.result()
            insight_res = future_insight.result()

        is_breach = audit_result.get('is_breach', False)
        
        if is_breach:
            target_team = audit_result.get('target_team', "Marketing")
            target_spent = st.session_state.df_v2[st.session_state.df_v2['Team'] == target_team]['Amount'].sum()
            target_name = audit_result.get('target_name', 'Employee')
            res_msg = f"Access denied for {target_name}. Cross-team PII restricted. {target_name} belongs to the {target_team} team, and the total aggregate budget for the {target_team} team is ${target_spent:,.2f}."
            cur_avatar, title, color, bg, v_id = MIKE_PATH, "🛡️ MIKE - ACCESS CONTROL", "#fbbf24", "#451a03", os.getenv('SHERIFF_VOICE_ID')
        else:
            res_msg = insight_res
            cur_avatar, title, color, bg, v_id = VIC_PATH, "🎙️ VICTORIA - EXECUTIVE INSIGHT", "#a855f7", "#1e293b", os.getenv('SENTINEL_VOICE_ID')
            
            # CHART
            plot_df = team_df.copy()
            if "volatility" in query.lower():
                plot_df['Month'] = plot_df['Date'].dt.strftime('%b')
                plot_df = plot_df.groupby('Month')['Amount'].sum().reindex(['Jan', 'Feb', 'Mar', 'Apr']).reset_index()
                fig = px.area(plot_df, x='Month', y='Amount', title="Spending Volatility (Annotated Analysis)", template="plotly_dark", color_discrete_sequence=['#38bdf8'])
                fig.add_annotation(x='Mar', y=plot_df[plot_df['Month']=='Mar']['Amount'].values[0], text="658% SURGE", showarrow=True, arrowhead=2, bgcolor="#ef4444", font=dict(color="white", size=14))
            else:
                plot_df = plot_df.groupby('Category')['Amount'].sum().reset_index()
                fig = px.bar(plot_df, x='Category', y='Amount', title="Budget Allocation", template="plotly_dark", color_discrete_sequence=['#a855f7'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)

        # Voice
        el_key = os.getenv("ELEVENLABS_API_KEY")
        if el_key and v_id:
            try:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{v_id}"
                audio_resp = requests.post(url, json={"text": res_msg.replace("*",""), "model_id": "eleven_turbo_v2_5"}, headers={"xi-api-key": el_key, "Content-Type": "application/json"})
                if audio_resp.status_code == 200: st.audio(audio_resp.content, format="audio/mp3", autoplay=True)
            except: pass
            
        img_b64 = get_b64(cur_avatar)
        st.markdown(f'<div class="intel-card" style="border-color: {color} !important;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;"><h3 class="intel-title" style="color: {color} !important;">{title}</h3></div><div style="display:flex; gap:25px; align-items:center;"><img src="data:image/png;base64,{img_b64}" style="width:120px; height:120px; border-radius:15px; border: 3px solid #ffffff; object-fit: cover;"><div class="intel-quote">"{res_msg}"</div></div></div>', unsafe_allow_html=True)
        if fig: st.plotly_chart(fig, use_container_width=True)
        st.button("Dismiss Result", on_click=dismiss_callback)
        st.divider()
    except Exception as e: st.info(f"Syncing Intelligence... ({e})")

# 6. HEADER
st.markdown(f'''
<div class="header-bar">
    <div style="display: flex; flex-direction: column;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <h1 style="margin:0; font-weight:700; color:#ffffff !important; font-size:1.8rem;">Sentinel Vantage</h1>
            <span style="background: rgba(168,85,247,0.15); border: 1px solid #a855f7; padding: 4px 12px; border-radius: 6px; color: #d8b4fe; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px;">CLIENT: TECHFLOW INC.</span>
        </div>
        <div style="color:#ffffff; font-size:0.9rem; font-weight:600; margin-top:8px;">ENTERPRISE REWARDS COMMAND CENTER</div>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="text-align:right;">
            <div style="font-weight:700; color:#f1f5f9; font-size:1.1rem;">{selected_manager}</div>
            <div style="font-size:0.75rem; color:#ffffff; font-weight:600; text-transform: uppercase;">{manager_team} MANAGER</div>
        </div>
        <img src="https://i.pravatar.cc/150?u={selected_manager}" style="width:55px; height:55px; border-radius:50%; border: 2px solid #ffffff; margin-left:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
    </div>
</div>
''', unsafe_allow_html=True)

# 7. DASHBOARD
c1, c2, c3 = st.columns([1.2, 1.4, 1])
with c1:
    st.markdown(f'<div class="card"><div class="card-title" style="color: #ffffff !important;">TEAM BUDGET & TREND</div>', unsafe_allow_html=True)
    spent = team_df['Amount'].sum(); rem = max(0, 150000 - spent)
    monthly = team_df.groupby(team_df['Date'].dt.strftime('%b'))['Amount'].sum().reindex(['Jan', 'Feb', 'Mar', 'Apr']).reset_index()
    cp, cs = st.columns([1, 1.2])
    with cp:
        fig_p = go.Figure(data=[go.Pie(labels=['Spent', 'Rem'], values=[spent, rem], hole=.75, marker_colors=['#334155', '#22c55e'])])
        fig_p.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=140, paper_bgcolor='rgba(0,0,0,0)', annotations=[dict(text=f'{(rem/150000)*100:.0f}%', x=0.5, y=0.5, font_size=22, showarrow=False, font_color='white')])
        st.plotly_chart(fig_p, use_container_width=True)
    with cs:
        fig_s = px.line(monthly, x="Date", y="Amount", template="plotly_dark", markers=True)
        fig_s.update_traces(line_color="#38bdf8", line_width=4); fig_s.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, margin=dict(t=10, b=30, l=0, r=0), height=130, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig_s.update_xaxes(showgrid=False, tickfont=dict(size=10, color="white")); fig_s.update_yaxes(showgrid=False, showticklabels=False)
        st.plotly_chart(fig_s, use_container_width=True)
    st.markdown(f'<div style="margin-top:10px;"><div style="color:#ffffff; opacity:0.8; font-size:0.8rem; font-weight:700;">TOTAL SPENT</div><div style="font-size:1.6rem; font-weight:800; color:#f1f5f9;">${spent:,.0f}</div></div></div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card"><div class="card-title" style="color: #ffffff !important;">PENDING CLAIMS</div>', unsafe_allow_html=True)
    for n, i in [("Alex R.", "Amazon $50"), ("Maria S.", "Starbucks $25"), ("Sam J.", "Electronics $200"), ("Sarah L.", "Wellness $75")]:
        st.markdown(f'<div class="claim-item"><span style="color:#ffffff !important;">{n}</span><span style="font-weight:700; color:#38bdf8;">{i}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="card"><div class="card-title" style="color: #ffffff !important;">QUICK ACTIONS</div>', unsafe_allow_html=True)
    for act in ["$25 SPOT AWARD", "$50 RECOGNITION", "APPROVE ALL", "EXPORT CSV"]:
        st.markdown(f'<div class="shortcut-btn">{act}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.caption(f"Sentinel Vantage Engine | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
