import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.rag.retriever import index_documents

if __name__ == "__main__":
    print(f"Indexed {index_documents(reset=True)} chunks")
