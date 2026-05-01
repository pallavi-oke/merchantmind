import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
try:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    m_resp = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=20,
        messages=[{"role": "user", "content": "ping"}]
    )
    print("SUCCESS: ", m_resp.content)
except Exception as e:
    print("FAILED: ", e)
