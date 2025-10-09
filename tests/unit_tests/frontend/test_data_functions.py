# Import dependencies
from datetime import datetime, timedelta, timezone
from frontend.functions.data_functions import (
    transform_workflow_overview_df,
    collect_latest_workflow_runs,
    collect_project_workflows,
    create_repo_workflow_map
)
from unittest.mock import patch, MagicMock
import pandas as pd

@patch("frontend.functions.data_functions.BlobClient")
def test_collect_project_workflows(mock_blob_client):
    """
    Test that `collect_project_workflows` correctly retrieves workflow filenames
    from blob storage and extracts only the JSON filenames (without directory paths).

    Steps:
    - Mock BlobClient to simulate available blob files.
    - Verify that the function returns the expected cleaned list of filenames.
    - Ensure the blob client methods are called correctly.
    """
    # Setup test and mock variables
    mock_instance = MagicMock()
    mock_instance.list_blob_filenames.return_value = [
        "workflows/proj1.json",
        "workflows/proj2.json",
        "workflows/subdir/proj3.json",
    ]
    mock_blob_client.return_value = mock_instance

    # Execute function under test
    result = collect_project_workflows()

    # Verify the output matches expected filenames (without folder paths)
    assert result == ["proj1.json", "proj2.json", "proj3.json"]

    # Ensure BlobClient was instantiated correctly
    mock_blob_client.assert_called_once_with(source="frontend")

    # Verify list_blob_filenames called with correct parameters
    mock_instance.list_blob_filenames.assert_called_once_with(
        container_name="project-monitoring",
        directory_path="workflows"
    )


@patch("frontend.functions.data_functions.collect_project_workflows")
def test_create_repo_workflow_map(mock_collect):
    """
    Test that `create_repo_workflow_map` correctly groups workflow files
    by their repository names and extracts workflow names.

    Steps:
    - Mock the output of `collect_project_workflows` to return sample JSON filenames.
    - Call the function and confirm it returns a dictionary mapping repos to workflows.
    - Assert correctness of grouping and order.
    """
    # Arrange: simulate collected workflow filenames
    mock_collect.return_value = [
        "repo1_build.json",
        "repo1_test.json",
        "repo2_deploy.json",
        "repo3_cleanup.json",
        "repo3_report.json",
    ]

    # Act: execute function
    result = create_repo_workflow_map()

    # Expected mapping of repos → list of workflows
    expected = {
        "repo1": ["build", "test"],
        "repo2": ["deploy"],
        "repo3": ["cleanup", "report"],
    }

    # Assert the resulting mapping is correct
    assert result == expected

    # Ensure the mocked helper function was called once
    mock_collect.assert_called_once()


@patch("frontend.functions.data_functions.BlobClient")
def test_collect_latest_workflow_runs(mock_blob_client):
    """
    Test that `collect_latest_workflow_runs` correctly reads the latest workflow
    run data from blob storage and compiles it into a DataFrame.

    Steps:
    - Mock BlobClient to simulate available workflow JSON blobs.
    - Mock each blob read to return a list of run dictionaries.
    - Validate that the returned DataFrame has the expected columns and data.
    - Confirm the correct BlobClient usage and function call counts.
    """
    # Arrange: setup BlobClient mock and expected return data
    mock_instance = MagicMock()

    # Simulate a list of workflow run file names
    mock_instance.list_blob_filenames.return_value = [
        "workflows/repo1_build.json",
        "workflows/repo2_test.json",
    ]

    # Simulate each file returning a list of run details
    mock_instance.read_blob_to_dict.side_effect = [
        [{"name": "repo1_build", "status": "success", "duration": 120}],
        [{"name": "repo2_test", "status": "failed", "duration": 90}],
    ]

    mock_blob_client.return_value = mock_instance

    # Act: execute function under test
    result = collect_latest_workflow_runs()

    # Assert: check type and structure
    assert isinstance(result, pd.DataFrame)
    assert set(result.columns) == {"name", "status", "duration"}

    # Verify DataFrame content
    assert len(result) == 2
    assert result.iloc[0]["name"] == "repo1_build"
    assert result.iloc[1]["status"] == "failed"

    # Verify BlobClient interaction correctness
    mock_blob_client.assert_any_call(source="frontend")
    mock_instance.list_blob_filenames.assert_called_once_with(
        container_name="project-monitoring",
        directory_path="workflows"
    )
    assert mock_instance.read_blob_to_dict.call_count == 2

def test_transform_workflow_overview_df():
    """
    Test that `transform_workflow_overview_df` correctly transforms workflow data
    with duration formatting, days-since-last-run calculation, and status flag
    assignment based on the `active_status` field.

    Steps:
    - Create a mock DataFrame with representative workflow data.
    - Apply the transform function.
    - Validate structure, column presence, and computed values.
    - Confirm that status flags map correctly from `active_status`.
    - Check duration formatting and repo URL construction.
    - Ensure sorting order is stable and predictable.
    """
    # Arrange input test data
    now = datetime.now(timezone.utc)
    df_input = pd.DataFrame([
        {
            "repo": "repo1",
            "workflow_name": "build",
            "updated_at": (now - timedelta(days=10)).isoformat(),
            "status": "success",
            "html_url": "https://github.com/powellrhys/repo1/actions/runs/1",
            "duration_seconds": 125,
            "active_status": "active",
        },
        {
            "repo": "repo2",
            "workflow_name": "test",
            "updated_at": (now - timedelta(days=90)).isoformat(),
            "status": "failure",
            "html_url": "https://github.com/powellrhys/repo2/actions/runs/2",
            "duration_seconds": 360,
            "active_status": "inactive",
        },
    ])

    # Act - execute function
    result = transform_workflow_overview_df(df_input)

    # Assert columns are as expected
    expected_cols = [
        "repo",
        "workflow_name",
        "updated_at",
        "status",
        "html_url",
        "duration",
        "days_since_last_run",
        "status_flag",
    ]
    assert list(result.columns) == expected_cols

    # Check repo URL prefix
    assert result.iloc[0]["repo"].startswith("https://github.com/powellrhys/")

    # Verify duration formatting
    assert all("m" in d and "s" in d for d in result["duration"])

    # Check approximate day calculations
    build_days = result[result["workflow_name"] == "build"]["days_since_last_run"].iloc[0]
    test_days = result[result["workflow_name"] == "test"]["days_since_last_run"].iloc[0]
    assert 9 <= build_days <= 11
    assert 89 <= test_days <= 91

    # Confirm correct mapping from active_status
    build_flag = result[result["workflow_name"] == "build"]["status_flag"].iloc[0]
    test_flag = result[result["workflow_name"] == "test"]["status_flag"].iloc[0]
    assert build_flag == "🟢 Active"
    assert test_flag == "🔴 Inactive"

    # Ensure sorting order by repo and recency
    assert result.iloc[0]["repo"] <= result.iloc[1]["repo"]
