"""Tests for the Database Agent."""

import pytest

from database_agent.database_agent import DatabaseAgent


@pytest.fixture
def agent():
    """Create a DatabaseAgent instance for testing."""
    return DatabaseAgent()


def test_agent_initialization(agent):
    """Test that the agent initializes correctly."""
    assert agent is not None
    assert isinstance(agent.config, dict)


def test_analyze_database(agent):
    """Test database analysis functionality."""
    result = agent.analyze_database("test://database")
    assert isinstance(result, dict)
    assert "status" in result


def test_generate_migration(agent):
    """Test migration generation functionality."""
    changes = [{"type": "add_column", "table": "users", "column": "email"}]
    migration = agent.generate_migration(changes)
    assert isinstance(migration, str)
    assert len(migration) > 0


def test_validate_changes(agent):
    """Test change validation functionality."""
    changes = [{"type": "add_column", "table": "users", "column": "email"}]
    assert agent.validate_changes(changes) is True
