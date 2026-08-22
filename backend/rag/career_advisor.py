import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from sentence_transformers import SentenceTransformer

from rag.retriever import search


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found.")


client = genai.Client(
    api_key=api_key
)


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# استخدم موديل متاح في حسابك
LLM_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]


class CareerAdvisor:

    def __init__(self, chunks, index):

        self.chunks = chunks
        self.index = index

        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )


    # =========================================================
    # RETRIEVAL
    # =========================================================

    def retrieve_context(self, question, top_k=5):

        results = search(
            question,
            self.chunks,
            self.index,
            self.embedding_model,
            top_k=top_k
        )
        print("\n" + "=" * 80)
        print("RETRIEVER QUESTION:")
        print(question)

        print("\nRETRIEVED CONTEXT:")
        print("=" * 80)

        context_parts = []

        for i, result in enumerate(results, start=1):

            context_parts.append(
                f"""
--- Context {i} ---

Source:
{result["source"]}

Content:
{result["content"]}
"""
            )
         
    
        return "\n".join(context_parts)


    # =========================================================
    # PROMPT
    # =========================================================

    def build_prompt(self, question, context):

        return f"""
You are an AI Career Advisor.

Your job is to help users improve their careers based
ONLY on the provided knowledge base.

You MUST use the retrieved knowledge base.

Do not invent facts that are not supported by the
knowledge base.

If the knowledge base does not contain enough information,
say:

"I don't have enough information in the provided knowledge base."

However, when the knowledge base contains relevant
information, provide a useful and structured answer.

Use clear sections when appropriate.

Knowledge Base:
{context}

User Question:
{question}

Answer:
"""


    # =========================================================
    # GEMINI
    # =========================================================

    def generate_answer(self, prompt):

        last_error = None

        for model in LLM_MODELS:

            for attempt in range(3):

                try:

                    print(
                        f"Calling Gemini model: {model} "
                        f"(attempt {attempt + 1})"
                    )

                    response = client.models.generate_content(
                        model=model,
                        contents=prompt
                    )

                    if response.text:

                        return response.text

                    return "Gemini returned an empty response."

                except errors.ServerError as e:

                    last_error = e

                    print(
                        f"Gemini server error with {model}: {e}"
                    )

                    # 503 = temporary server overload
                    if getattr(e, "status_code", None) == 503:

                        wait_time = 2 ** attempt

                        print(
                            f"Retrying in {wait_time} seconds..."
                        )

                        time.sleep(wait_time)

                        continue

                    break

                except Exception as e:

                    last_error = e

                    print(
                        f"Gemini error with {model}: {e}"
                    )

                    break


        raise RuntimeError(
            f"Gemini API failed after retries. "
            f"Last error: {last_error}"
        )


    # =========================================================
    # ASK
    # =========================================================

    def ask(self, question, top_k=5):

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


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    from rag.document_loader import load_documents
    from rag.chunking import split_documents
    from rag.embeddings import create_embeddings
    from rag.vector_store import create_vector_store


    print("Loading knowledge base...")

    documents = load_documents()

    print(
        f"Documents: {len(documents)}"
    )


    chunks = split_documents(
        documents
    )

    print(
        f"Chunks: {len(chunks)}"
    )


    print("\nCreating embeddings...")

    embeddings = create_embeddings(
        chunks
    )

    print(
        f"Embeddings shape: {embeddings.shape}"
    )


    print("\nCreating FAISS index...")

    index = create_vector_store(
        chunks,
        embeddings
    )


    advisor = CareerAdvisor(
        chunks,
        index
    )


    question = (
        "What skills do I need "
        "to become an AI Engineer?"
    )


    print("\nQuestion:")
    print(question)


    print("\nGenerating answer...")


    result = advisor.ask(
        question,
        top_k=5
    )


    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)


    print(
        result["answer"]
    )