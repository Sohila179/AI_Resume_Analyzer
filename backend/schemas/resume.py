from pydantic import BaseModel, Field,ConfigDict

class ResumeResponse(BaseModel):
    id: int
    resume_file: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)