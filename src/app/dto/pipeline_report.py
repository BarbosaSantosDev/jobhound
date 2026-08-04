from pydantic import BaseModel


class PipelineReport(BaseModel):
    fetched: int
    matched: int
    manual_review: int = 0
    errors: int = 0
