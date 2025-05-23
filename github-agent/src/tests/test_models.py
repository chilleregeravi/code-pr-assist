import pytest
from pydantic import ValidationError

from github_agent.models import PullRequestData


def test_pull_request_data_fields():
    pr = PullRequestData(title="t", body="b", number=1, diff_url="url")
    assert pr.title == "t"
    assert pr.body == "b"
    assert pr.number == 1
    assert pr.diff_url == "url"


def test_pull_request_data_validation():
    with pytest.raises(ValidationError):
        PullRequestData(title="t", body="b", number="not_a_number", diff_url="url")
