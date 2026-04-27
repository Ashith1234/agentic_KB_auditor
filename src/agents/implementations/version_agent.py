import yaml
import os
from agents.base.base_agent import BaseAgent
from domain.entities.audit_signal import AuditSignal, SignalType
from infrastructure.llm.openai_client import OpenAIClient
from utils.id_gen import generate_id
from core.logger import logger

class VersionAgent(BaseAgent):
    """Detects outdated content."""
    
    def __init__(self):
        super().__init__(name="VersionAgent")
        self.llm = OpenAIClient()
        self.prompt_path = "configs/prompts/version.yaml"
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
        Analyzes document chunks for outdated information.
        Expected data format: {"chunks": [{"content": str, "metadata": dict}]}
        """
        if not self.prompt_config:
            return []

        chunks = data.get("chunks", [])
        signals = []

        for chunk in chunks:
            content = chunk.get("content", "")
            if not content:
                continue

            current_prompt = self.prompt_config["user_prompt_template"].format(content=content)
            
            # Use the inherited do-while reflection loop
            result = self.analyze_with_reflection(
                current_prompt=current_prompt,
                system_prompt=self.prompt_config["system_prompt"],
                llm_client=self.llm,
                max_retries=3
            )

            if result.get("outdated_found"):
                signal = AuditSignal(
                    id=generate_id(),
                    signal_type=SignalType.OUTDATED,
                    description=result.get("explanation", "Outdated information detected."),
                    severity=result.get("severity", "medium"),
                    source_agent=self.name,
                    metadata={"original_content": content, "source": chunk.get("metadata", {})}
                )
                signals.append(signal)

        return signals
