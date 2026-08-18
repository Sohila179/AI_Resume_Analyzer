# from pathlib import Path


# KNOWLEDGE_BASE_PATH = Path("knowledge_base")


# def load_documents():
#     documents = []

#     for file_path in KNOWLEDGE_BASE_PATH.rglob("*.txt"):

#         content = file_path.read_text(encoding="utf-8")

#         documents.append({
#             "content": content,
#             "source": str(file_path)
#         })

#     return documents


# if __name__ == "__main__":
#     documents = load_documents()

#     print(f"Number of documents: {len(documents)}")

#     for document in documents:
#         print("\n" + "=" * 60)
#         print("Source:", document["source"])
#         print(document["content"][:300])
from pathlib import Path


# AI_Resume_Analyzer/
# ├── backend/
# │   └── rag/
# │       └── document_loader.py
# └── knowledge_base/

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "backend" / "knowledge_base"
def load_documents():
    documents = []

    if not KNOWLEDGE_BASE_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge base not found at: {KNOWLEDGE_BASE_PATH}"
        )

    for file_path in KNOWLEDGE_BASE_PATH.rglob("*.txt"):

        content = file_path.read_text(
            encoding="utf-8"
        )

        documents.append({
            "content": content,
            "source": str(file_path)
        })

    return documents


if __name__ == "__main__":

    documents = load_documents()

    print(f"Knowledge Base: {KNOWLEDGE_BASE_PATH}")
    print(f"Number of documents: {len(documents)}")

    for document in documents:

        print("\n" + "=" * 60)
        print("Source:", document["source"])
        print(document["content"][:300])