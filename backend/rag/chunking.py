
from rag.document_loader import load_documents
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = []

    for document in documents:

        document_chunks = splitter.split_text(
            document["content"]
        )

        for chunk in document_chunks:

            chunks.append({
                "content": chunk,
                "source": document["source"]
            })

    return chunks


if __name__ == "__main__":

    documents = load_documents()

    chunks = split_documents(documents)

    print(f"Number of documents: {len(documents)}")
    print(f"Number of chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks[:5]):

        print("\n" + "=" * 60)
        print(f"Chunk {i + 1}")

        print("Source:", chunk["source"])

        print(chunk["content"])