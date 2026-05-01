import os
from dotenv import load_dotenv
load_dotenv()
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from sentinel.governance.policies import SegmentVerdict, load_policy
from datetime import datetime
import google.generativeai as genai
# import anthropic # We'll add this if the user provides a key

class SentinelSheriff:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.policy = load_policy()
        
        # Configure Storyteller (Gemini)
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.storyteller_model = genai.GenerativeModel('gemini-flash-latest')
        
        # Sheriff LLM
        self.sheriff_model = genai.GenerativeModel('gemini-flash-latest')

    def audit_segment(self, segment_id: str, text: str, metadata: dict) -> SegmentVerdict:
        """
        Runs the multi-pass audit on a script segment.
        """
        # 1. Deterministic Pass: Cross-Client Check (G-006)
        requested_client = metadata.get("client_id")
        # Simplified: check if any OTHER client name is in the text
        other_clients = ["Marlow & Finch", "Brackenridge Logistics"]
        if requested_client in other_clients:
            other_clients.remove(requested_client)
        
        for other in other_clients:
            if other.lower() in text.lower():
                return SegmentVerdict(
                    segment_id=segment_id,
                    decision="block",
                    rule_id="G-006",
                    rule_description="Cross-client data leakage detected",
                    mechanism="deterministic"
                )

        # 2. Deterministic Pass: Structured PII (G-004)
        results = self.analyzer.analyze(text=text, entities=[], language='en')
        if results:
            anonymized_result = self.anonymizer.anonymize(text=text, analyzer_results=results)
            return SegmentVerdict(
                segment_id=segment_id,
                decision="redact",
                rule_id="G-004",
                rule_description="Structured PII detected (Presidio)",
                mechanism="deterministic",
                redacted_text=text,
                replacement_text=anonymized_result.text
            )

        # 3. Deterministic Pass: Cohort Size (G-001)
        cohort_n = metadata.get("n_cohort", 100) # Default to safe if missing
        if cohort_n < self.policy.cohort_size_threshold:
            return SegmentVerdict(
                segment_id=segment_id,
                decision="block",
                rule_id="G-001",
                rule_description=f"Cohort size ({cohort_n}) below threshold ({self.policy.cohort_size_threshold})",
                mechanism="deterministic"
            )

        # 4. LLM Pass: Contextual Identification (G-005)
        # We'll use Gemini for the pilot, but the architecture calls for Claude
        prompt = f"""
        Audit the following briefing segment for contextual privacy risks.
        Look for narrative phrasings that identify individuals or small groups without using names.
        
        Segment: "{text}"
        
        Respond ONLY with a JSON object: {{"pii_found": boolean, "confidence": float, "reason": "string"}}
        """
        
        try:
            response = self.sheriff_model.generate_content(prompt)
            import json
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                audit = json.loads(json_match.group())
                if audit["pii_found"] and audit["confidence"] >= self.policy.llm_contextual_confidence_floor:
                    return SegmentVerdict(
                        segment_id=segment_id,
                        decision="redact",
                        rule_id="G-005",
                        rule_description=audit["reason"],
                        mechanism="llm",
                        confidence=audit["confidence"]
                    )
        except Exception as e:
            # Failure mode: Fall back to deterministic rules
            pass

        return SegmentVerdict(
            segment_id=segment_id,
            decision="pass",
            mechanism="hybrid"
        )
