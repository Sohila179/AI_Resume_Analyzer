import os

from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer

from rag.retriever import search

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found."
    )

client = genai.Client(
    api_key=api_key
)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "gemini-3.6-flash"


class CareerAdvisor:

    def __init__(self, chunks, index):

        self.chunks = chunks
        self.index = index

        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )


    def retrieve_context(self, question, top_k=3):

        results = search(
            question,
            self.chunks,
            self.index,
            self.embedding_model,
            top_k=top_k
        )

        context_parts = []

        for i, result in enumerate(
            results,
            start=1
        ):

            context_parts.append(
                f"""
--- Context {i} ---
Source: {result["source"]}

{result["content"]}
"""
            )

        return "\n".join(context_parts)


    def build_prompt(self, question, context):

        return f"""
You are a Career Advisor.

Answer the user's question using ONLY
the provided knowledge base.

If the answer cannot be found in the
knowledge base, say:

"I don't have enough information in the provided knowledge base."

Do not invent information.
Do not use outside knowledge.

Knowledge Base Context:
{context}

User Question:
{question}

Answer:
"""


    def generate_answer(self, prompt):

        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )

        return response.text


    def ask(self, question, top_k=3):

        context = self.retrieve_context(
            question,
            top_k=top_k
        )

        prompt = self.build_prompt(
            question,
            context
        )

        answer = self.generate_answer(
            prompt
        )

        return {
            "question": question,
            "context": context,
            "answer": answer
        }


if __name__ == "__main__":

    from rag.document_loader import load_documents
    from rag.chunking import split_documents
    from rag.embeddings import create_embeddings
    from rag.vector_store import create_vector_store

    print("Loading knowledge base...")

    documents = load_documents()
    chunks = split_documents(documents)

    print(f"Documents: {len(documents)}")
    print(f"Chunks: {len(chunks)}")

    print("\nCreating embeddings...")

    embeddings = create_embeddings(chunks)

    print(f"Embeddings shape: {embeddings.shape}")

    print("\nCreating FAISS index...")

    index = create_vector_store(chunks, embeddings)
    advisor = CareerAdvisor(chunks, index)

    question = "What skills do I need to become an AI Engineer?"

    print("\nQuestion:")
    print(question)

    print("\nGenerating answer...")

    result = advisor.ask(question)

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)

    print(result["answer"])    