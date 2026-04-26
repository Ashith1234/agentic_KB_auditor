import yaml
import os
from itertools import combinations
from agents.base.base_agent import BaseAgent
from domain.entities.audit_signal import AuditSignal, SignalType
from infrastructure.llm.openai_client import OpenAIClient
from utils.id_gen import generate_id
from core.logger import logger

class DuplicateAgent(BaseAgent):
    """Identifies duplicates and conflicting information."""
    
    def __init__(self):
        super().__init__(name="DuplicateAgent")
        self.llm = OpenAIClient()
        self.prompt_path = "configs/prompts/contradiction.yaml"
        self._load_prompt()

    def _load_prompt(self):
        if os.path.exists(self.prompt_path):
            with open(self.prompt_path, "r") as f:
                self.prompt_config = yaml.safe_load(f)
        else:
            logger.error(f"Prompt config not found at {self.prompt_path}")
            self.prompt_config = None

    def analyze(self, data: dict) -> list[AuditSignal]:
        """
        Analyzes pairs of document chunks for contradictions.
        Expected data format: {"chunks": [{"content": str, "metadata": dict}]}
        """
        if not self.prompt_config:
            return []

        chunks = data.get("chunks", [])
        signals = []

        # Compare chunks in pairs to find contradictions
        for chunk1, chunk2 in combinations(chunks, 2):
            content1 = chunk1.get("content", "")
            content2 = chunk2.get("content", "")
            
            if not content1 or not content2:
                continue

            prompt = self.prompt_config["user_prompt_template"].format(doc1=content1, doc2=content2)
            result = self.llm.evaluate_json(prompt, system_prompt=self.prompt_config["system_prompt"])

            if result.get("contradiction_found"):
                signal = AuditSignal(
                    id=generate_id(),
                    signal_type=SignalType.CONTRADICTION,
                    description=result.get("explanation", "Contradiction found between sources."),
                    severity="high",
                    source_agent=self.name,
                    metadata={
                        "doc1": content1[:200], 
                        "doc2": content2[:200],
                        "source1": chunk1.get("metadata", {}),
                        "source2": chunk2.get("metadata", {})
                    }
                )
                signals.append(signal)

        return signals

