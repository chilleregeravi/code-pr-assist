from pydantic import BaseModel


class PullRequestData(BaseModel):
    title: str
    body: str
    number: int
    diff_url: str
