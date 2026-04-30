import yaml
import os
from typing import Dict, Any
from core.logger import logger

class PromptOptimizer:
    """Modifies agent prompts based on outcome success, failure, and human feedback."""
    
    def __init__(self, prompts_dir: str = "configs/prompts"):
        self.prompts_dir = prompts_dir
        
    def _load_prompt(self, agent_name: str) -> Dict[str, Any]:
        """Loads the current prompt configuration for an agent."""
        # Simple mapping heuristic
        file_map = {
            "VersionAgent": "version.yaml",
            "DuplicateAgent": "contradiction.yaml",
            "CoverageAgent": "coverage.yaml"
        }
        filename = file_map.get(agent_name)
        if not filename:
            return {}
            
        path = os.path.join(self.prompts_dir, filename)
        if os.path.exists(path):
            with open(path, "r") as f:
                return yaml.safe_load(f)
        return {}

    def _save_prompt(self, agent_name: str, config: Dict[str, Any]) -> None:
        file_map = {
            "VersionAgent": "version.yaml",
            "DuplicateAgent": "contradiction.yaml",
            "CoverageAgent": "coverage.yaml"
        }
        filename = file_map.get(agent_name)
        if not filename:
            return
            
        path = os.path.join(self.prompts_dir, filename)
        os.makedirs(self.prompts_dir, exist_ok=True)
        with open(path, "w") as f:
            yaml.safe_dump(config, f)
            
    def track_outcome(self, agent_name: str, outcome: str, feedback: str = ""):
        """
        Tracks an outcome (e.g., 'SUCCESS', 'REJECTED') and updates the prompt.
        """
        if outcome == "REJECTED":
            logger.info(f"Optimizing prompt for {agent_name} due to rejection.")
            config = self._load_prompt(agent_name)
            if not config:
                logger.warning(f"No prompt config found for {agent_name}")
                return
                
            # A simple rule-based optimizer: append a negative constraint based on feedback
            system_prompt = config.get("system_prompt", "")
            if "CRITICAL CONSTRAINT:" not in system_prompt:
                system_prompt += "\n\nCRITICAL CONSTRAINT: Pay closer attention to recent feedback to avoid false positives."
                
            if feedback:
                system_prompt += f"\n- Avoid this mistake: {feedback}"
                
            config["system_prompt"] = system_prompt
            self._save_prompt(agent_name, config)
            logger.info(f"Updated system prompt for {agent_name} with constraints.")
