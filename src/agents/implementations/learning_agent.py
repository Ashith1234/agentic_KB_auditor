import yaml
import os
from agents.base.base_agent import BaseAgent
from domain.entities.audit_signal import AuditSignal
from infrastructure.llm.openai_client import OpenAIClient
from infrastructure.db.review_queue import ReviewQueue
from core.logger import logger

class LearningAgent(BaseAgent):
    """Proposes updates to the KB based on audit signals."""
    
    def __init__(self):
        super().__init__(name="LearningAgent")
        self.llm = OpenAIClient()
        self.prompt_path = "configs/prompts/remediation.yaml"
        self.review_queue = ReviewQueue()
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
        Processes audit signals and proposes remediation actions.
        Expected data format: {"signals": [AuditSignal]}
        """
        if not self.prompt_config:
            return []

        signals = data.get("signals", [])
        if not signals:
            return []

        # Convert signals to a string representation for the LLM
        signals_text = "\n".join([f"- {s.signal_type}: {s.description} (Severity: {s.severity})" for s in signals])
        
        prompt = self.prompt_config["user_prompt_template"].format(signals=signals_text)
        result = self.llm.evaluate_json(prompt, system_prompt=self.prompt_config["system_prompt"])

        action = result.get("action", "suggest")
        reasoning = result.get("reasoning", "Proposed remediation based on audit signals.")

        # Store the proposal in the review queue
        self.review_queue.add_item({
            "action": action,
            "reasoning": reasoning,
            "signals": [s.dict() for s in signals],
            "status": "pending"
        })

        logger.info(f"LearningAgent proposed action: {action}")
        return [] # Proposers don't usually return new signals, they perform actions.

