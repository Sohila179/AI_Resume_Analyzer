import os
import json

from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer

from rag.retriever import search


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found."
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=api_key
)


# =========================================================
# MODELS
# =========================================================

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

LLM_MODEL = "gemini-3.6-flash"


# =========================================================
# CAREER ADVISOR
# =========================================================

class CareerAdvisor:

    def __init__(
        self,
        chunks,
        index
    ):

        self.chunks = chunks

        self.index = index

        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )


    # =====================================================
    # RETRIEVE CONTEXT
    # =====================================================

    def retrieve_context(
        self,
        question,
        top_k=3
    ):

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

        return "\n".join(
            context_parts
        )


    # =====================================================
    # BUILD NORMAL CAREER ADVISOR PROMPT
    # =====================================================

    def build_prompt(
        self,
        question,
        context
    ):

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


    # =====================================================
    # GENERATE ANSWER
    # =====================================================

    def generate_answer(
        self,
        prompt
    ):

        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )

        return response.text


    # =====================================================
    # ASK CAREER QUESTION
    # =====================================================

    def ask(
        self,
        question,
        top_k=3
    ):

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


    # =====================================================
    # GENERATE STRUCTURED CAREER ROADMAP
    # =====================================================

    def generate_roadmap(
        self,
        resume_data,
        missing_skills=None,
        target_role="AI Engineer"
    ):

        """
        Generate a personalized structured
        learning roadmap.

        The returned object is JSON-compatible
        and can be rendered directly by the frontend.
        """

        if missing_skills is None:
            missing_skills = []


        # -------------------------------------------------
        # Normalize missing skills
        # -------------------------------------------------

        if not isinstance(
            missing_skills,
            list
        ):

            missing_skills = [
                str(missing_skills)
            ]


        missing_skills = [
            str(skill).strip()
            for skill in missing_skills
            if str(skill).strip()
        ]


        # -------------------------------------------------
        # Normalize resume data
        # -------------------------------------------------

        if resume_data is None:

            resume_data = {}


        if isinstance(
            resume_data,
            str
        ):

            resume_text = resume_data

        else:

            resume_text = json.dumps(
                resume_data,
                ensure_ascii=False,
                indent=2,
                default=str
            )


        missing_skills_text = ", ".join(
            missing_skills
        )


        # -------------------------------------------------
        # Retrieve career knowledge
        # -------------------------------------------------

        knowledge_question = f"""
Create a career learning roadmap for someone
who wants to become {target_role}.

Important missing skills:
{missing_skills_text}
"""

        try:

            context = self.retrieve_context(
                knowledge_question,
                top_k=5
            )

        except Exception as error:

            print(
                "Roadmap retrieval warning:",
                error
            )

            context = ""


        # -------------------------------------------------
        # ROADMAP PROMPT
        # -------------------------------------------------

        prompt = f"""
You are an expert AI Career Advisor
and Learning Path Designer.

Your task is to create a personalized,
sequential career learning roadmap.

TARGET ROLE:
{target_role}

CANDIDATE RESUME:
{resume_text}

MISSING SKILLS:
{missing_skills_text}

KNOWLEDGE BASE:
{context}

==================================================
IMPORTANT RULES
==================================================

1. Analyze the candidate's current skills.

2. Use the missing skills to determine
   what should be learned next.

3. Do not create a completely generic roadmap.

4. The roadmap must progress from the
   candidate's current level toward the
   target role.

5. Each step must build on previous steps.

6. Include practical projects.

7. Include estimated duration.

8. Include the skills learned in every step.

9. Explain why every step matters.

10. The final step should lead toward
    the target role.

11. Keep the roadmap realistic.

12. Do not include unnecessary skills
    unrelated to the target role.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Do NOT return Markdown.

Do NOT use:

```json

Do NOT add explanations outside JSON.

Use exactly this structure:

{{
    "target_role": "{target_role}",

    "current_level": "string",

    "estimated_duration": "string",

    "current_skills": [
        "skill 1",
        "skill 2"
    ],

    "missing_skills": [
        "skill 1",
        "skill 2"
    ],

    "roadmap": [
        {{
            "step": 1,

            "title": "Learning Phase Title",

            "description": "Short explanation of this phase.",

            "duration": "2 weeks",

            "skills": [
                "Skill 1",
                "Skill 2",
                "Skill 3"
            ],

            "projects": [
                "Practical project"
            ],

            "why_it_matters":
                "Explain why this phase is important.",

            "status": "recommended"
        }}
    ],

    "final_goal": {{
        "title": "{target_role}",

        "description":
            "Description of the final career goal."
    }}
}}

==================================================
QUALITY REQUIREMENTS
==================================================

Create between 4 and 7 roadmap steps.

Each step must have:

- step
- title
- description
- duration
- skills
- projects
- why_it_matters
- status

The roadmap should look like a real
professional learning journey.

Make the sequence logical.

Example progression:

Current Skills
      ↓
Foundations
      ↓
Core Technical Skills
      ↓
Advanced Skills
      ↓
Projects
      ↓
Deployment / Professional Skills
      ↓
Target Role

But customize the actual roadmap
according to the candidate.

Return JSON only.
"""


        # -------------------------------------------------
        # CALL GEMINI
        # -------------------------------------------------

        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )


        raw_text = (
            response.text
            if response.text
            else ""
        )


        raw_text = raw_text.strip()


        # -------------------------------------------------
        # REMOVE MARKDOWN FENCES
        # -------------------------------------------------

        if raw_text.startswith(
            "```json"
        ):

            raw_text = raw_text[
                len("```json"):
            ]


        elif raw_text.startswith(
            "```"
        ):

            raw_text = raw_text[
                len("```"):
            ]


        if raw_text.endswith(
            "```"
        ):

            raw_text = raw_text[
                :-3
            ]


        raw_text = raw_text.strip()


        # -------------------------------------------------
        # PARSE JSON
        # -------------------------------------------------

        try:

            roadmap = json.loads(
                raw_text
            )

        except json.JSONDecodeError:

            # Try extracting JSON object
            # if Gemini accidentally added text.

            start = raw_text.find(
                "{"
            )

            end = raw_text.rfind(
                "}"
            )


            if (
                start != -1
                and end != -1
                and end > start
            ):

                json_text = raw_text[
                    start:end + 1
                ]

                try:

                    roadmap = json.loads(
                        json_text
                    )

                except json.JSONDecodeError as error:

                    raise ValueError(
                        "Gemini returned invalid roadmap JSON."
                    ) from error

            else:

                raise ValueError(
                    "Gemini returned invalid roadmap JSON."
                )


        # -------------------------------------------------
        # VALIDATE BASIC STRUCTURE
        # -------------------------------------------------

        if not isinstance(
            roadmap,
            dict
        ):

            raise ValueError(
                "Roadmap response must be a JSON object."
            )


        if not isinstance(
            roadmap.get(
                "roadmap"
            ),
            list
        ):

            roadmap["roadmap"] = []


        if not isinstance(
            roadmap.get(
                "current_skills"
            ),
            list
        ):

            roadmap["current_skills"] = []


        if not isinstance(
            roadmap.get(
                "missing_skills"
            ),
            list
        ):

            roadmap["missing_skills"] = (
                missing_skills
            )


        # -------------------------------------------------
        # NORMALIZE ROADMAP STEPS
        # -------------------------------------------------

        normalized_steps = []


        for index, step in enumerate(
            roadmap["roadmap"],
            start=1
        ):

            if not isinstance(
                step,
                dict
            ):

                continue


            skills = step.get(
                "skills",
                []
            )


            if not isinstance(
                skills,
                list
            ):

                skills = [
                    str(skills)
                ]


            projects = step.get(
                "projects",
                []
            )


            if not isinstance(
                projects,
                list
            ):

                projects = [
                    str(projects)
                ]


            normalized_steps.append(
                {
                    "step": index,

                    "title": str(
                        step.get(
                            "title",
                            f"Learning Phase {index}"
                        )
                    ),

                    "description": str(
                        step.get(
                            "description",
                            ""
                        )
                    ),

                    "duration": str(
                        step.get(
                            "duration",
                            "Flexible"
                        )
                    ),

                    "skills": [
                        str(skill)
                        for skill in skills
                    ],

                    "projects": [
                        str(project)
                        for project in projects
                    ],

                    "why_it_matters": str(
                        step.get(
                            "why_it_matters",
                            ""
                        )
                    ),

                    "status": str(
                        step.get(
                            "status",
                            "recommended"
                        )
                    )
                }
            )


        roadmap["roadmap"] = (
            normalized_steps
        )


        # -------------------------------------------------
        # FINAL NORMALIZATION
        # -------------------------------------------------

        roadmap["target_role"] = str(
            roadmap.get(
                "target_role",
                target_role
            )
        )


        roadmap["current_level"] = str(
            roadmap.get(
                "current_level",
                "Entry Level"
            )
        )


        roadmap["estimated_duration"] = str(
            roadmap.get(
                "estimated_duration",
                "Flexible"
            )
        )


        roadmap["final_goal"] = (
            roadmap.get(
                "final_goal",
                {
                    "title": target_role,
                    "description":
                        f"Become a qualified {target_role}."
                }
            )
        )


        if not isinstance(
            roadmap["final_goal"],
            dict
        ):

            roadmap["final_goal"] = {
                "title": target_role,
                "description":
                    f"Become a qualified {target_role}."
            }


        return roadmap


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    from rag.document_loader import (
        load_documents
    )

    from rag.chunking import (
        split_documents
    )

    from rag.embeddings import (
        create_embeddings
    )

    from rag.vector_store import (
        create_vector_store
    )


    print(
        "Loading knowledge base..."
    )


    documents = load_documents()

    chunks = split_documents(
        documents
    )


    print(
        f"Documents: {len(documents)}"
    )

    print(
        f"Chunks: {len(chunks)}"
    )


    print(
        "\nCreating embeddings..."
    )


    embeddings = create_embeddings(
        chunks
    )


    print(
        f"Embeddings shape: {embeddings.shape}"
    )


    print(
        "\nCreating FAISS index..."
    )


    index = create_vector_store(
        chunks,
        embeddings
    )


    advisor = CareerAdvisor(
        chunks,
        index
    )


    # =====================================================
    # TEST NORMAL CAREER ADVISOR
    # =====================================================

    question = (
        "What skills do I need "
        "to become an AI Engineer?"
    )


    print(
        "\nQuestion:"
    )

    print(
        question
    )


    print(
        "\nGenerating answer..."
    )


    result = advisor.ask(
        question
    )


    print(
        "\n" + "=" * 60
    )

    print(
        "ANSWER"
    )

    print(
        "=" * 60
    )


    print(
        result["answer"]
    )


    # =====================================================
    # TEST ROADMAP
    # =====================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "GENERATING CAREER ROADMAP"
    )

    print(
        "=" * 60
    )


    test_resume = {

        "name": "Candidate",

        "job_title": "Junior AI Engineer",

        "skills": [
            "Python",
            "Pandas",
            "NumPy",
            "SQL",
            "Scikit-learn"
        ],

        "education": [
            "Computer Science"
        ],

        "experience": [
            "Machine Learning projects"
        ]
    }


    test_missing_skills = [

        "Deep Learning",

        "PyTorch",

        "Docker",

        "MLOps"

    ]


    roadmap = advisor.generate_roadmap(
        resume_data=test_resume,

        missing_skills=test_missing_skills,

        target_role="AI Engineer"
    )


    print(
        json.dumps(
            roadmap,
            ensure_ascii=False,
            indent=2
        )
    )