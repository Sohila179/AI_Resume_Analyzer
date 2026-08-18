# import numpy as np

# from sentence_transformers import SentenceTransformer

# from src.document_loader import load_documents
# from src.chunking import split_documents
# from src.embeddings import create_embeddings
# from src.vector_store import create_vector_store


# MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# embedding_model = SentenceTransformer(MODEL_NAME)

# def search(query, chunks, index, model, top_k=3):

#     query_embedding = model.encode(
#         [query],
#         convert_to_numpy=True
#     )

#     query_embedding = np.asarray(
#         query_embedding,
#         dtype="float32"
#     )

#     distances, indices = index.search(
#         query_embedding,
#         top_k
#     )

#     results = []

#     for distance, index_position in zip(
#         distances[0],
#         indices[0]
#     ):

#         results.append({
#             "content": chunks[index_position]["content"],
#             "source": chunks[index_position]["source"],
#             "distance": float(distance)
#         })

#     return results


# # ============================================================
# # TEST RETRIEVAL
# # ============================================================

# if __name__ == "__main__":

#     print("Loading knowledge base...")

#     documents = load_documents()

#     print("Number of documents:", len(documents))

#     print("\nCreating chunks...")

#     chunks = split_documents(documents)

#     print("Number of chunks:", len(chunks))

#     print("\nCreating embeddings...")

#     embeddings = create_embeddings(chunks)

#     print("Embeddings shape:", embeddings.shape)

#     print("\nCreating FAISS vector store...")

#     index = create_vector_store(
#         chunks,
#         embeddings
#     )

#     print("Number of vectors:", index.ntotal)

#     print("\nLoading embedding model...")

#     model = SentenceTransformer(MODEL_NAME)

#     query = "What skills do I need to become an AI Engineer?"

#     print("\nSearching...")
# def retrieve_context(
#     query,
#     chunks,
#     index,
#     model,
#     top_k=5
# ):
    
#     results = search(
#         query,
#         chunks,
#         index,
#         model,
#         top_k=5
#     )

#     # print("\n" + "=" * 60)
#     # print("USER QUESTION")
#     # print("=" * 60)

#     # print(query)

#     # print("\n" + "=" * 60)
#     # print("RETRIEVED CHUNKS")
#     # print("=" * 60)

#     # for i, result in enumerate(results, start=1):

#     #     print("\n" + "-" * 60)
#     #     print(f"Result {i}")
#     #     print("-" * 60)

#     #     print("Source:")
#     #     print(result["source"])

#     #     print("\nDistance:")
#     #     print(result["distance"])

#     #     print("\nContent:")
#     #     print(result["content"])
#     context_parts = []

#     for result in results:

#         context_parts.append(
#             f"Source: {result['source']}\n"
#             f"{result['content']}"
#         )

#     return "\n\n---\n\n".join(context_parts)
        
import numpy as np

from sentence_transformers import SentenceTransformer

from rag.document_loader import load_documents
from rag.chunking import split_documents
from rag.embeddings import create_embeddings
from rag.vector_store import create_vector_store


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def search(
    query,
    chunks,
    index,
    model,
    top_k=3
):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for distance, index_position in zip(
        distances[0],
        indices[0]
    ):

        # Safety check
        if index_position < 0:
            continue

        results.append({
            "content": chunks[index_position]["content"],
            "source": chunks[index_position]["source"],
            "distance": float(distance)
        })

    return results


def retrieve_context(
    query,
    chunks,
    index,
    model,
    top_k=5
):

    results = search(
        query,
        chunks,
        index,
        model,
        top_k=top_k
    )

    context_parts = []

    for result in results:

        context_parts.append(
            f"Source: {result['source']}\n"
            f"{result['content']}"
        )

    return "\n\n---\n\n".join(
        context_parts
    )


if __name__ == "__main__":

    print("Loading knowledge base...")

    documents = load_documents()

    print(
        "Number of documents:",
        len(documents)
    )

    print("\nCreating chunks...")

    chunks = split_documents(documents)

    print(
        "Number of chunks:",
        len(chunks)
    )

    print("\nCreating embeddings...")

    embeddings = create_embeddings(chunks)

    print(
        "Embeddings shape:",
        embeddings.shape
    )

    print("\nCreating FAISS vector store...")

    index = create_vector_store(
        chunks,
        embeddings
    )

    print(
        "Number of vectors:",
        index.ntotal
    )

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    query = (
        "What skills do I need "
        "to become an AI Engineer?"
    )

    print("\nSearching...")

    results = search(
        query,
        chunks,
        index,
        model,
        top_k=3
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        print("\n" + "=" * 60)

        print(f"Result {i}")

        print("Source:")
        print(result["source"])

        print("\nDistance:")
        print(result["distance"])

        print("\nContent:")
        print(result["content"])