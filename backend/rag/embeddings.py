
from rag.chunking import split_documents
from rag.document_loader import load_documents

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def create_embeddings(chunks):

    model = SentenceTransformer(MODEL_NAME)

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )

    return embeddings


if __name__ == "__main__":

    documents = load_documents()

    chunks = split_documents(documents)

    embeddings = create_embeddings(chunks)

    print("Number of chunks:", len(chunks))

    print(
        "Embeddings shape:",
        embeddings.shape
    )

    print("\nFirst embedding:")

    print(embeddings[0])