import re
from core.logger import logger

class SecurityLayer:
    """Masks PII and protects sensitive data."""
    
    def mask_pii(self, text: str) -> str:
        # Mask emails
        text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL REDACTED]', text)
        # Mask phones
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE REDACTED]', text)
        return text

    def protect_api_keys(self, text: str) -> str:
        # Protect API keys (e.g. OpenAI)
        text = re.sub(r'sk-[a-zA-Z0-9]{32,}', '[API KEY REDACTED]', text)
        return text
        
    def sanitize_log(self, log_entry: dict) -> dict:
        sanitized = {}
        for k, v in log_entry.items():
            if isinstance(v, str):
                v = self.mask_pii(v)
                v = self.protect_api_keys(v)
            sanitized[k] = v
        return sanitized
