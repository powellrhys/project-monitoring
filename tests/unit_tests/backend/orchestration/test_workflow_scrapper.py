# Import dependencies
from backend.functions.orchestration.workflow_scrapper import WorkflowScrapper
from unittest.mock import patch, MagicMock
import json

@patch("backend.functions.orchestration.workflow_scrapper.configure_logging")
@patch("backend.functions.orchestration.workflow_scrapper.Variables")
def test_init_creates_expected_attributes(mock_vars, mock_logger):
    """
    Test that WorkflowScrapper initializes correctly.

    Verifies that:
    - configure_logging is called to set up a logger.
    - Variables is instantiated for environment access.
    - The provided REPOS list is stored as an instance attribute.
    """

    # Create a fake logger object and mock return
    mock_logger_instance = MagicMock()
    mock_logger.return_value = mock_logger_instance

    # Create fake Variables instance
    mock_vars_instance = MagicMock()
    mock_vars.return_value = mock_vars_instance

    # Instantiate the scrapper with a sample repo list
    repos = ["repo-one", "repo-two"]
    scrapper = WorkflowScrapper(REPOS=repos)

    # Verify logger setup
    mock_logger.assert_called_once()
    assert scrapper.logger == mock_logger_instance

    # Verify Variables instantiation
    mock_vars.assert_called_once()
    assert scrapper.vars == mock_vars_instance

    # Verify repo list assignment
    assert scrapper.REPOS == repos


@patch("backend.functions.orchestration.workflow_scrapper.GitHubClient")
@patch("backend.functions.orchestration.workflow_scrapper.configure_logging")
@patch("backend.functions.orchestration.workflow_scrapper.Variables")
def test_run_processes_all_repositories(mock_vars, mock_logger, mock_github):
    """
    Test that the `run` method processes all repositories and workflows successfully.

    Verifies that:
    - GitHubClient is initialized for each repository with the correct token.
    - All expected logging calls are made.
    - export_dict_to_blob is invoked once per workflow.
    """

    # Create fake logger and environment variable objects
    mock_logger_instance = MagicMock()
    mock_logger.return_value = mock_logger_instance
    mock_vars.return_value.GITHUB_TOKEN = "fake-token"

    # Mock GitHubClient instance and its methods
    mock_client_instance = MagicMock()
    mock_github.return_value = mock_client_instance

    # Simulate two fake workflows and workflow runs
    mock_client_instance.list_repository_workflows.return_value = [
        {"name": "build"},
        {"name": "deploy"}
    ]

    mock_client_instance.collect_workflow_metadata.side_effect = [
        [{"run_started_at": "2025-01-01T12:00:00Z", "conclusion": "success"}],
        [{"run_started_at": "2025-01-02T13:00:00Z", "conclusion": "failure"}]
    ]

    mock_client_instance.aggregate_workflow_data.side_effect = [
        [{"name": "build", "duration": 120}],
        [{"name": "deploy", "duration": 95}]
    ]

    # Create an instance of WorkflowScrapper with fake repos
    scrapper = WorkflowScrapper(REPOS=["repo1"])
    scrapper.export_dict_to_blob = MagicMock()

    # Execute the workflow run
    scrapper.run()

    # Verify the logger is called for general flow messages
    mock_logger_instance.info.assert_any_call("Running Workflow Scrapping flow \n")
    mock_logger_instance.info.assert_any_call("1/1 - Collecting workflow data for repo: repo1... \n")

    # Verify GitHubClient instantiated once with token
    mock_github.assert_called_once_with(GITHUB_TOKEN="fake-token")

    # Verify each workflow’s data export was performed
    assert scrapper.export_dict_to_blob.call_count == 2
    scrapper.export_dict_to_blob.assert_any_call(
        data=[{"name": "build", "duration": 120}],
        container="project-monitoring",
        output_filename="workflows/repo1_build.json"
    )
    scrapper.export_dict_to_blob.assert_any_call(
        data=[{"name": "deploy", "duration": 95}],
        container="project-monitoring",
        output_filename="workflows/repo1_deploy.json"
    )

@patch("backend.functions.orchestration.workflow_scrapper.GitHubClient")
@patch("backend.functions.orchestration.workflow_scrapper.configure_logging")
@patch("backend.functions.orchestration.workflow_scrapper.Variables")
def test_run_handles_json_decode_error(mock_vars, mock_logger, mock_github):
    """
    Test that a JSONDecodeError raised during workflow parsing is logged and handled.

    Verifies that:
    - logger.exception is called with the appropriate error message.
    - The loop breaks after the decoding error occurs.
    """

    # Configure fake logger, variables, and GitHub client mocks
    mock_logger_instance = MagicMock()
    mock_logger.return_value = mock_logger_instance
    mock_vars.return_value.GITHUB_TOKEN = "token"

    mock_client_instance = MagicMock()
    mock_client_instance.list_repository_workflows.return_value = [{"name": "deploy"}]
    mock_client_instance.collect_workflow_metadata.return_value = [{"run_started_at": "x", "conclusion": "y"}]
    mock_client_instance.aggregate_workflow_data.side_effect = json.JSONDecodeError("Bad JSON", "data", 0)
    mock_github.return_value = mock_client_instance

    scrapper = WorkflowScrapper(REPOS=["repo1"])
    scrapper.export_dict_to_blob = MagicMock()

    # Execute method to trigger the JSON error path
    scrapper.run()

    # Confirm JSON error is logged
    mock_logger_instance.exception.assert_called_once()
    error_message = mock_logger_instance.exception.call_args[0][0]
    assert "Failed to parse workflow run data" in error_message

    # Confirm export was never called after error
    scrapper.export_dict_to_blob.assert_not_called()
