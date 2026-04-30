import sys
from .detector import ProjectDetector
from .injector import MiddlewareInjector
from core.logger import logger

class CLIInstaller:
    def install(self, project_path: str):
        print(f"\n🔍 Scanning project at: {project_path}")
        
        detector = ProjectDetector(project_path)
        scan = detector.detect_all()

        print(f"  KB Paths    : {scan.get('kb_paths', [])}")
        print(f"  Vector DB   : {scan.get('vector_db')}")
        print(f"  LLM         : {scan.get('llm_usage')}")
        print(f"  Backend     : {scan.get('backend')}")

        print("\n🔌 Injecting middleware...")
        injector = MiddlewareInjector(project_path)
        success = injector.inject()

        if success:
            print("✅ RAG Auditor successfully installed.")
            print("   Dashboard: streamlit run src/interfaces/dashboard/streamlit_app.py")
            print("   Run audit: python src/plugin/cli.py audit")
        else:
            print("⚠️  Middleware injection failed. Please add manually:")
            print("   from observability.middleware import AuditingMiddleware")
            print("   app.add_middleware(AuditingMiddleware, pipeline=pipeline)")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        installer = CLIInstaller()
        installer.install(path)
    else:
        print("Usage: rag install <path>")

if __name__ == "__main__":
    main()
