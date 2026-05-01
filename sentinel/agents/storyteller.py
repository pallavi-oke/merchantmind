import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
import json
from pydantic import BaseModel
from typing import List

class ScriptSegment(BaseModel):
    segment_id: str
    speaker: str # "Analyst" or "Sheriff"
    text: str
    emphasis: bool = False
    metadata: dict = {}

class BriefingScript(BaseModel):
    segments: List[ScriptSegment]

class SentinelStoryteller:
    def __init__(self):
        # Configure Storyteller (Gemini)
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_briefing(self, findings: dict, client_name: str) -> BriefingScript:
        """
        Translates structured findings into a multi-segment script.
        """
        prompt = f"""
        You are the Storyteller Agent for Sentinel. 
        Your task is to draft an executive briefing script based on these findings for {client_name}:
        {json.dumps(findings)}
        
        Rules:
        1. Break the script into small segments (1-3 sentences each).
        2. Assign each segment a unique ID.
        3. Speaker must be "Analyst".
        4. Focus on insights: redemption rates, anomalies, and peer comparisons.
        5. DO NOT invent data. Only use what is in the findings.
        6. Return ONLY a JSON object matching this schema: {{"segments": [{{"segment_id": "...", "speaker": "Analyst", "text": "..."}}]}}
        """
        
        response = self.model.generate_content(prompt)
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            script_data = json.loads(json_match.group())
            return BriefingScript(**script_data)
        else:
            raise ValueError("Failed to generate structured script from Storyteller")
