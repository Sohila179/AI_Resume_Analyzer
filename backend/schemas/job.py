from pydantic import BaseModel, Field, ConfigDict


class JobBase(BaseModel):
    title: str = Field(..., min_length=2)
    content: str = Field(..., min_length=10)
    required_skills: list[str] = Field(default_factory=list)


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: str | None = Field(None, min_length=2)
    content: str | None = Field(None, min_length=10)
    required_skills: list[str] | None = None


class JobResponse(JobBase):
    id: int
    employer_id: int

    model_config = ConfigDict(from_attributes=True)
    