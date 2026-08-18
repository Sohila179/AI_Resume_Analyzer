# import faiss
# import numpy as np
# from src.document_loader import load_documents
# from src.chunking import split_documents
# from src.embeddings import create_embeddings


# def create_vector_store(chunks, embeddings):
#     dimension = embeddings.shape[1]

#     index = faiss.IndexFlatL2(dimension)

#     embeddings = np.asarray(embeddings, dtype="float32")

#     index.add(embeddings)

#     return index


# if __name__ == "__main__":
#     documents = load_documents()
#     chunks = split_documents(documents)

#     embeddings = create_embeddings(chunks)

#     index = create_vector_store(chunks, embeddings)

#     print("Number of vectors in FAISS:", index.ntotal)
#     print("Vector dimension:", index.d)
import faiss
import numpy as np

from rag.document_loader import load_documents
from rag.chunking import split_documents
from rag.embeddings import create_embeddings


def create_vector_store(chunks, embeddings):

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    index.add(embeddings)

    return index


if __name__ == "__main__":

    documents = load_documents()

    chunks = split_documents(documents)

    embeddings = create_embeddings(chunks)

    index = create_vector_store(
        chunks,
        embeddings
    )

    print(
        "Number of vectors in FAISS:",
        index.ntotal
    )

    print(
        "Vector dimension:",
        index.d
    )