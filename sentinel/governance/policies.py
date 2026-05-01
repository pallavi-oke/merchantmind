from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, List, Optional
import yaml
import os

class SegmentVerdict(BaseModel):
    segment_id: str
    decision: Literal["pass", "redact", "block"]
    rule_id: Optional[str] = None
    rule_description: Optional[str] = None
    mechanism: Literal["deterministic", "llm", "hybrid"]
    confidence: Optional[float] = None
    redacted_text: Optional[str] = None
    replacement_text: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class GovernancePolicy(BaseModel):
    cohort_size_threshold: int = 50
    peer_cohort_threshold: int = 20
    significance_p_value_floor: float = 0.10
    significance_min_n: int = 30
    llm_contextual_confidence_floor: float = 0.70

def load_policy():
    policy_path = "sentinel/governance/policies.yaml"
    if os.path.exists(policy_path):
        with open(policy_path, "r") as f:
            config = yaml.safe_load(f)
            return GovernancePolicy(**config)
    return GovernancePolicy()

# Create default policy file if missing
if not os.path.exists("sentinel/governance/policies.yaml"):
    with open("sentinel/governance/policies.yaml", "w") as f:
        yaml.dump(GovernancePolicy().model_dump(), f)
