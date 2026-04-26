import pytest
from kb.chunker import DocumentChunker
from langchain.schema import Document

def test_chunker():
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    docs = [Document(page_content="This is a very long string that should be chunked properly by the chunker.", metadata={"source": "test"})]
    chunks = chunker.chunk_documents(docs)
    
    assert len(chunks) > 1
    assert chunks[0].metadata["source"] == "test"
