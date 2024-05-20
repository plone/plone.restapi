from pydantic import BaseModel, Field


class ErrorDefinitionDTO(BaseModel):
    type: str = Field(..., description="The type of error")
    message: str = Field(
        ..., description="A human-readable message describing the error"
    )


class ErrorOutputDTO(BaseModel):
    error: ErrorDefinitionDTO
