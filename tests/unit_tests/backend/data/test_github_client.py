# Import dependencies
from backend.functions.data.github_client import GitHubClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytest
import requests

# Patch the configure_logging function to return a mock logger during initialization
@patch("backend.functions.data.github_client.configure_logging")
def test_init_sets_expected_attributes(mock_logger):
    """
    Test that GitHubClient initializes correctly with expected attributes.
    """
    # Create a mock logger instance to simulate the configure_logging return
    mock_logger_instance = MagicMock()

    # Make the mocked configure_logging function return the mock logger
    mock_logger.return_value = mock_logger_instance

    # Instantiate the GitHubClient with a fake token
    client = GitHubClient(GITHUB_TOKEN="test-token")

    # Assert that the logger attribute of the client is the mocked logger
    assert client.logger == mock_logger_instance

    # Assert that the base_url is correctly set to the GitHub API repository path
    assert client.base_url == "https://api.github.com/repos/powellrhys"

    # Assert that the HEADERS dictionary includes the provided token
    assert client.HEADERS == {"Authorization": "token test-token"}


# Patch requests.get to simulate GitHub API responses
@patch("backend.functions.data.github_client.requests.get")
def test_list_repository_workflows_returns_expected_data(mock_get):
    """
    Test that list_repository_workflows returns workflows from GitHub API.
    """
    # Create a mock response object to simulate requests.get response
    mock_response = MagicMock()

    # Set the mock response JSON to return a sample workflow
    mock_response.json.return_value = {"workflows": [{"id": 1, "name": "CI"}]}

    # Make requests.get return the mock response
    mock_get.return_value = mock_response

    # Instantiate the GitHubClient
    client = GitHubClient(GITHUB_TOKEN="abc123")

    # Call list_repository_workflows with a test repository
    result = client.list_repository_workflows("repo-one")

    # Assert that requests.get was called with the correct URL and headers
    mock_get.assert_called_once_with(
        "https://api.github.com/repos/powellrhys/repo-one/actions/workflows",
        headers=client.HEADERS,
        timeout=30
    )

    # Assert that raise_for_status was called to check HTTP errors
    mock_response.raise_for_status.assert_called_once()

    # Assert that the function returned the expected list of workflows
    assert result == [{"id": 1, "name": "CI"}]


# Patch requests.get to simulate HTTP errors
@patch("backend.functions.data.github_client.requests.get")
def test_list_repository_workflows_raises_for_status_error(mock_get):
    """
    Test that HTTP errors from the GitHub API are raised properly.
    """
    # Create a mock response object
    mock_response = MagicMock()

    # Simulate an HTTP error when raise_for_status is called
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad Request")

    # Make requests.get return the mock response
    mock_get.return_value = mock_response

    # Instantiate the GitHubClient
    client = GitHubClient(GITHUB_TOKEN="abc123")

    # Assert that calling list_repository_workflows raises the HTTPError
    with pytest.raises(requests.exceptions.HTTPError):
        client.list_repository_workflows("repo-one")


# Patch requests.get for workflow metadata fetching
@patch("backend.functions.data.github_client.requests.get")
def test_collect_workflow_metadata_returns_expected_data(mock_get):
    """
    Test that collect_workflow_metadata retrieves workflow runs correctly.
    """
    # Create a mock response for the GET request
    mock_response = MagicMock()

    # Set the JSON response to return workflow_runs data
    mock_response.json.return_value = {"workflow_runs": [{"run_number": 10}]}

    # Make requests.get return the mock response
    mock_get.return_value = mock_response

    # Instantiate GitHubClient
    client = GitHubClient(GITHUB_TOKEN="token123")

    # Define a sample workflow object with an ID
    workflow = {"id": 111}

    # Call collect_workflow_metadata with a test repo and workflow
    result = client.collect_workflow_metadata("repoX", workflow)

    # Assert that requests.get was called with the correct runs endpoint
    mock_get.assert_called_once_with(
        "https://api.github.com/repos/powellrhys/repoX/actions/workflows/111/runs",
        headers=client.HEADERS
    )

    # Assert that raise_for_status was called to ensure error handling
    mock_response.raise_for_status.assert_called_once()

    # Assert that the function returned the expected workflow runs
    assert result == [{"run_number": 10}]


# Patch requests.get for error handling in metadata fetch
@patch("backend.functions.data.github_client.requests.get")
def test_collect_workflow_metadata_raises_for_status_error(mock_get):
    """
    Test that collect_workflow_metadata raises an HTTPError for failed requests.
    """
    # Create a mock response object
    mock_response = MagicMock()

    # Simulate HTTP error on raise_for_status
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")

    # Make requests.get return the mock response
    mock_get.return_value = mock_response

    # Instantiate GitHubClient
    client = GitHubClient(GITHUB_TOKEN="test")

    # Verify that HTTPError is raised when calling collect_workflow_metadata
    with pytest.raises(requests.exceptions.HTTPError):
        client.collect_workflow_metadata("repoY", {"id": 999})


# Patch configure_logging for workflow_duration tests
@patch("backend.functions.data.github_client.configure_logging")
def test_workflow_duration_returns_correct_seconds(mock_logger):
    """
    Test that workflow_duration calculates the correct duration in seconds.
    """
    # Mock the logger
    mock_logger.return_value = MagicMock()

    # Instantiate GitHubClient
    client = GitHubClient(GITHUB_TOKEN="xyz")

    # Define start and end times
    start = datetime(2025, 1, 1, 12, 0, 0)
    end = start + timedelta(minutes=5)

    # Define a sample workflow run with ISO8601 timestamps
    run = {
        "run_started_at": start.isoformat(),
        "updated_at": end.isoformat()
    }

    # Calculate the duration
    duration = client.workflow_duration(run)

    # Assert that the duration matches the expected number of seconds (5 minutes)
    assert duration == 300


# Patch configure_logging for invalid timestamp handling
@patch("backend.functions.data.github_client.configure_logging")
def test_workflow_duration_handles_invalid_timestamps_gracefully(mock_logger):
    """
    Test that workflow_duration handles invalid timestamps without exceptions.
    """
    # Create a mock logger instance
    mock_logger_instance = MagicMock()

    # Configure the mock configure_logging to return the mock logger
    mock_logger.return_value = mock_logger_instance

    # Instantiate GitHubClient
    client = GitHubClient(GITHUB_TOKEN="123")

    # Define a run with invalid timestamps
    run = {"run_number": 1, "run_started_at": "bad-timestamp", "updated_at": None}

    # Call workflow_duration and capture the result
    result = client.workflow_duration(run)

    # Verify that a warning was logged
    mock_logger_instance.warning.assert_called_once()

    # Assert that the function returns None for invalid timestamps
    assert result is None


# Patch configure_logging for aggregate workflow data
@patch("backend.functions.data.github_client.configure_logging")
def test_aggregate_workflow_data_returns_expected_structure(mock_logger):
    """
    Test that aggregate_workflow_data produces a simplified workflow data list.
    """
    # Create a mock logger
    mock_logger.return_value = MagicMock()

    # Instantiate GitHubClient
    client = GitHubClient(GITHUB_TOKEN="token")

    # Mock workflow_duration to return a fixed duration
    client.workflow_duration = MagicMock(return_value=42)

    # Define a sample workflow run list
    runs = [
        {
            "status": "completed",
            "conclusion": "success",
            "created_at": "a",
            "updated_at": "b",
            "run_number": 101,
            "html_url": "url1"
        }
    ]

    # Call aggregate_workflow_data with test repository, workflow, and runs
    result = client.aggregate_workflow_data("repoZ", "deploy", runs, "active")

    # Assert the returned value is a list
    assert isinstance(result, list)

    # Verify that repo and workflow_name are correctly set
    assert result[0]["repo"] == "repoZ"
    assert result[0]["workflow_name"] == "deploy"

    # Verify that workflow_duration was called and its value used
    assert result[0]["duration_seconds"] == 42
    client.workflow_duration.assert_called_once_with(run=runs[0])
