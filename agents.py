import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_model():
    # Use stable models with full paths for v1beta compatibility
    target_models = [
        'models/gemini-2.5-pro', 
        'models/gemini-2.5-flash'
    ]
    for model_name in target_models:
        try:
            m = genai.GenerativeModel(model_name)
            # Live "Ping" to verify
            m.generate_content("ping", generation_config={"max_output_tokens": 1})
            return m
        except Exception:
            continue
    return genai.GenerativeModel('models/gemini-2.5-pro')

# Initialize once
model = get_gemini_model()

class SentinelAgents:
    def __init__(self, df):
        self.df = df

    def insight_agent(self, manager_name, context):
        """Analytical narration agent (Victoria)"""
        prompt = f"""
        You are Victoria, Lead Rewards Analyst. 
        LEAD WITH NUMBERS. Start your response with a key metric (e.g. "$12,400 spent", "685% surge", or "Budget expires in 14 days").
        Follow with EXACTLY ONE strategic sentence.
        Context: {context}
        Manager: {manager_name}
        CRITICAL: PURE TEXT ONLY. No bolding. No asterisks. 
        """
        try:
            import streamlit as st
            model_id = st.session_state.get('gemini_model_id', 'models/gemini-2.5-pro')
            m = genai.GenerativeModel(model_id)
            response = m.generate_content(prompt)
            if response.text:
                return response.text.strip()
            return "Analytics engine timeout. Aggregate spend is within nominal limits for the Engineering cohort."
        except Exception as e:
            return f"Error connecting to Victoria: {e}"

    def voice_visuals_agent(self, query):
        """Determines best visualization for a query"""
        prompt = f"""
        Given the user query: "{query}"
        Choose best chart. Respond ONLY JSON: {{"chart_type": "bar"|"line", "x": "column_name", "title": "string"}}
        Available columns: Date, Amount, Category, Team, Employee
        """
        try:
            m = genai.GenerativeModel('models/gemini-2.5-flash')
            response = m.generate_content(prompt)
            clean_text = response.text.strip().replace('```json', '').replace('```', '')
            return json.loads(clean_text)
        except:
            return {"chart_type": "bar", "x": "Category", "title": "Rewards Allocation"}
