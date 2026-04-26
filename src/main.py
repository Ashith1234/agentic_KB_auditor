from core.logger import logger
from interfaces.api.app import app
import uvicorn

def main():
    logger.info("Starting Agentic KB Auditor...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
