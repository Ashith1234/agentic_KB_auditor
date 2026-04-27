import yaml
import os
from agents.base.base_agent import BaseAgent
from domain.entities.audit_signal import AuditSignal, SignalType
from infrastructure.llm.openai_client import OpenAIClient
from utils.id_gen import generate_id
from core.logger import logger

class CoverageAgent(BaseAgent):
    """Finds missing topics or gaps in the KB."""
    
    def __init__(self):
        super().__init__(name="CoverageAgent")
        self.llm = OpenAIClient()
        self.prompt_path = "configs/prompts/gap.yaml"
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
        Analyzes the query and retrieved chunks for knowledge gaps.
        Expected data format: {"query": str, "chunks": [{"content": str}]}
        """
        if not self.prompt_config:
            return []

        query = data.get("query", "")
        chunks = data.get("chunks", [])
        
        if not query:
            return []

        docs_text = "\n---\n".join([c.get("content", "") for c in chunks])
        
        current_prompt = self.prompt_config["user_prompt_template"].format(query=query, docs=docs_text)
        
        result = self.analyze_with_reflection(
            current_prompt=current_prompt,
            system_prompt=self.prompt_config["system_prompt"],
            llm_client=self.llm,
            max_retries=3
        )

        signals = []
        if result.get("gap_found"):
            signal = AuditSignal(
                id=generate_id(),
                signal_type=SignalType.GAP,
                description=result.get("gap_description", "Knowledge gap detected."),
                severity="medium",
                source_agent=self.name,
                metadata={"query": query, "retrieved_count": len(chunks)}
            )
            signals.append(signal)

        return signals

