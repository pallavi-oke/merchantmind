import os
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
from sentinel.data_gen.generator import generate_sentinel_data
from sentinel.agents.storyteller import SentinelStoryteller
from sentinel.governance.sheriff import SentinelSheriff

load_dotenv()

def verify_pipeline():
    print("--- 🛡️ Sentinel Pipeline Verification ---")
    
    # 1. Verify Data Generation
    print("[1/4] Verifying Data Generator...")
    try:
        df = generate_sentinel_data("Brackenridge Logistics", num_records=10)
        print(f"✅ Data Gen Success: Generated {len(df)} records.")
    except Exception as e:
        print(f"❌ Data Gen Failed: {e}")
        return

    # 2. Verify Gemini Connectivity & Model Name
    print("[2/4] Verifying Gemini Connectivity...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or "your_api_key" in api_key:
        print("❌ Gemini Failed: No valid API key found in .env")
        return
        
    genai.configure(api_key=api_key)
    # Test model names
    models_to_try = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash"]
    working_model = None
    
    for m_name in models_to_try:
        try:
            print(f"  Trying model: {m_name}...")
            model = genai.GenerativeModel(m_name)
            response = model.generate_content("ping")
            if response.text:
                print(f"✅ Gemini Success: Model '{m_name}' is working.")
                working_model = m_name
                break
        except Exception as e:
            print(f"  - '{m_name}' failed: {e}")
            
    if not working_model:
        print("❌ Gemini Failed: Could not find a working model name.")
        return

    # 3. Verify Storyteller
    print("[3/4] Verifying Storyteller Agent...")
    try:
        storyteller = SentinelStoryteller()
        # Patch model name if needed
        storyteller.model = genai.GenerativeModel(working_model)
        findings = {"q3_redemption": "82.4%", "peer_median": "84.2%"}
        script = storyteller.generate_briefing(findings, "Brackenridge Logistics")
        print(f"✅ Storyteller Success: Generated {len(script.segments)} segments.")
    except Exception as e:
        print(f"❌ Storyteller Failed: {e}")
        return

    # 4. Verify Sheriff
    print("[4/4] Verifying Sheriff Agent...")
    try:
        sheriff = SentinelSheriff()
        # Patch model name if needed
        sheriff.sheriff_model = genai.GenerativeModel(working_model)
        text = "Contact jordan.lee@brackenridge.com"
        verdict = sheriff.audit_segment("test_seg", text, {"client_id": "Brackenridge Logistics", "n_cohort": 100})
        print(f"✅ Sheriff Success: Decision was '{verdict.decision}'.")
    except Exception as e:
        print(f"❌ Sheriff Failed: {e}")
        return

    print("\n🎉 ALL COMPONENTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_pipeline()
