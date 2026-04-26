import sys
from .detector import ProjectDetector
from .injector import MiddlewareInjector
from core.logger import logger

class CLIInstaller:
    def install(self, project_path: str):
        logger.info(f"Scanning project at {project_path}")
        detector = ProjectDetector(project_path)
        scan_results = detector.detect_all()
        
        logger.info(f"Scan results: {scan_results}")
        
        injector = MiddlewareInjector(project_path)
        # Wait for manager approval before injecting
        logger.info("Installation initiated. Waiting for manager approval...")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        installer = CLIInstaller()
        installer.install(path)
    else:
        print("Usage: rag install <path>")

if __name__ == "__main__":
    main()
