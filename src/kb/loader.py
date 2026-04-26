import os
from typing import List, Dict, Any
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    DirectoryLoader
)
from core.logger import logger

class DocumentLoader:
    """
    Handles loading documents from various formats.
    """
    def __init__(self, directory_path: str):
        self.directory_path = directory_path

    def load_documents(self) -> List[Any]:
        """
        Loads all supported documents from the directory.
        """
        logger.info(f"Loading documents from {self.directory_path}")
        
        # Define loaders for different extensions
        loaders = {
            ".txt": TextLoader,
            ".pdf": PyPDFLoader,
            ".md": UnstructuredMarkdownLoader,
        }

        documents = []
        for file in os.listdir(self.directory_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in loaders:
                file_path = os.path.join(self.directory_path, file)
                try:
                    loader = loaders[ext](file_path)
                    documents.extend(loader.load())
                    logger.debug(f"Loaded {file}")
                except Exception as e:
                    logger.error(f"Failed to load {file}: {str(e)}")
        
        logger.info(f"Successfully loaded {len(documents)} document pages/files.")
        return documents
