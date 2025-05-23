from unittest.mock import MagicMock

import pytest

from database_agent.exceptions import DataValidationError, PRProcessingError
from database_agent.pr_processor import PRProcessor


@pytest.fixture
def valid_pr():
    return {
        "id": 1,
        "title": "Test PR",
        "body": "Test body",
        "state": "open",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T01:00:00",
        "author": "user",
        "repo_name": "owner/repo",
        "labels": ["bug"],
        "comments": ["comment"],
    }


@pytest.fixture
def processor():
    store = MagicMock()
    return PRProcessor(vector_store=store)


def test_validate_pr_data_missing_field(processor, valid_pr):
    pr = valid_pr.copy()
    del pr["title"]
    with pytest.raises(DataValidationError):
        processor.validate_pr_data(pr)


def test_validate_pr_data_wrong_type(processor, valid_pr):
    pr = valid_pr.copy()
    pr["id"] = "not-an-int"
    with pytest.raises(DataValidationError):
        processor.validate_pr_data(pr)


def test_validate_pr_data_bad_date(processor, valid_pr):
    pr = valid_pr.copy()
    pr["created_at"] = "bad-date"
    with pytest.raises(DataValidationError):
        processor.validate_pr_data(pr)


def test_validate_pr_data_updated_before_created(processor, valid_pr):
    pr = valid_pr.copy()
    pr["updated_at"] = "2023-01-01T00:00:00"
    with pytest.raises(DataValidationError):
        processor.validate_pr_data(pr)


def test_validate_pr_data_invalid_state(processor, valid_pr):
    pr = valid_pr.copy()
    pr["state"] = "invalid"
    with pytest.raises(DataValidationError):
        processor.validate_pr_data(pr)


def test_validate_pr_data_bad_repo_name(processor, valid_pr):
    pr = valid_pr.copy()
    pr["repo_name"] = "bad repo name"
    with pytest.raises(DataValidationError):
        processor.validate_pr_data(pr)


def test_validate_pr_data_negative_id(processor, valid_pr):
    pr = valid_pr.copy()
    pr["id"] = -1
    with pytest.raises(DataValidationError):
        processor.validate_pr_data(pr)


def test_transform_pr_data_labels_and_comments_not_list(processor, valid_pr):
    pr = valid_pr.copy()
    pr["labels"] = "bug"
    pr["comments"] = "comment"
    out = processor.transform_pr_data(pr)
    assert isinstance(out["labels"], list)
    assert isinstance(out["comments"], list)
    assert "processed_at" in out


def test_transform_pr_data_missing_labels_comments(processor, valid_pr):
    pr = valid_pr.copy()
    del pr["labels"]
    del pr["comments"]
    out = processor.transform_pr_data(pr)
    assert out["labels"] == []
    assert out["comments"] == []
    assert "processed_at" in out


def test_process_and_store_pr_validation_error(processor, valid_pr):
    processor.validate_pr_data = MagicMock(side_effect=DataValidationError("fail"))
    with pytest.raises(DataValidationError):
        processor.process_and_store_pr(valid_pr)


def test_process_and_store_pr_store_error(processor, valid_pr):
    processor.validate_pr_data = MagicMock()
    processor.transform_pr_data = MagicMock(return_value=valid_pr)
    processor.vector_store.store_pr.side_effect = Exception("fail")
    with pytest.raises(PRProcessingError):
        processor.process_and_store_pr(valid_pr)


def test_process_and_store_prs_batch_some_fail(processor, valid_pr):
    bad_pr = valid_pr.copy()
    bad_pr["id"] = -1
    prs = [valid_pr, bad_pr]
    processor.vector_store.store_prs_batch.return_value = True
    with pytest.raises(DataValidationError):
        processor.process_and_store_prs_batch(prs)


def test_process_pr_success(processor, valid_pr):
    processor.vector_store.store_pr.return_value = True
    assert processor.process_pr(valid_pr) is True


def test_process_pr_error(processor, valid_pr):
    processor.vector_store.store_pr.side_effect = Exception("fail")
    with pytest.raises(PRProcessingError):
        processor.process_pr(valid_pr)


def test_process_prs_batch_success(processor, valid_pr):
    processor.vector_store.store_prs_batch.return_value = True
    assert processor.process_prs_batch([valid_pr]) is True


def test_process_prs_batch_error(processor, valid_pr):
    processor.vector_store.store_prs_batch.side_effect = Exception("fail")
    with pytest.raises(PRProcessingError):
        processor.process_prs_batch([valid_pr])


def test_process_repository_prs_success(valid_pr):
    store = MagicMock()
    github_client = MagicMock()
    github_client.get_pull_requests.return_value = [
        MagicMock(number=1, title="t", body="b", labels=[])
    ]
    processor = PRProcessor(vector_store=store, github_client=github_client)
    processor.process_prs_batch = MagicMock(return_value=True)
    assert processor.process_repository_prs("owner/repo") is True


def test_process_repository_prs_error(valid_pr):
    store = MagicMock()
    github_client = MagicMock()
    github_client.get_pull_requests.side_effect = Exception("fail")
    processor = PRProcessor(vector_store=store, github_client=github_client)
    with pytest.raises(PRProcessingError):
        processor.process_repository_prs("owner/repo")
