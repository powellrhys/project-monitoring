# Import dependencies
from frontend.functions.data_functions import (
    transform_workflow_overview_df,
    collect_latest_workflow_runs,
    collect_project_workflows,
    create_repo_workflow_map
)
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import pandas as pd

@patch("frontend.functions.data_functions.BlobClient")
def test_collect_project_workflows(mock_blob_client):
    """
    """
    # Setup test and mock variables
    mock_instance = MagicMock()
    mock_instance.list_blob_filenames.return_value = [
        "workflows/proj1.json",
        "workflows/proj2.json",
        "workflows/subdir/proj3.json",
    ]
    mock_blob_client.return_value = mock_instance

    # Execute function
    result = collect_project_workflows()

    # Assert result as expected
    assert result == ["proj1.json", "proj2.json", "proj3.json"]

    # Ensure blob client called once
    mock_blob_client.assert_called_once_with(source="frontend")

    # Assert list blob filenames called once
    mock_instance.list_blob_filenames.assert_called_once_with(
        container_name="project-monitoring",
        directory_path="workflows"
    )

@patch("frontend.functions.data_functions.collect_project_workflows")
def test_create_repo_workflow_map(mock_collect):
    # Arrange: simulate collected filenames
    mock_collect.return_value = [
        "repo1_build.json",
        "repo1_test.json",
        "repo2_deploy.json",
        "repo3_cleanup.json",
        "repo3_report.json",
    ]

    # Act
    result = create_repo_workflow_map()

    # Assert: structure and content
    expected = {
        "repo1": ["build", "test"],
        "repo2": ["deploy"],
        "repo3": ["cleanup", "report"],
    }

    assert result == expected
    mock_collect.assert_called_once()

@patch("frontend.functions.data_functions.BlobClient")
def test_collect_latest_workflow_runs(mock_blob_client):
    # Arrange
    mock_instance = MagicMock()

    # Simulate file list
    mock_instance.list_blob_filenames.return_value = [
        "workflows/repo1_build.json",
        "workflows/repo2_test.json",
    ]

    # Simulate read_blob_to_dict returning list-like JSONs
    mock_instance.read_blob_to_dict.side_effect = [
        [{"name": "repo1_build", "status": "success", "duration": 120}],
        [{"name": "repo2_test", "status": "failed", "duration": 90}],
    ]

    mock_blob_client.return_value = mock_instance

    # Act
    result = collect_latest_workflow_runs()

    # Assert
    assert isinstance(result, pd.DataFrame)
    assert set(result.columns) == {"name", "status", "duration"}

    # Confirm that the two expected rows exist
    assert len(result) == 2
    assert result.iloc[0]["name"] == "repo1_build"
    assert result.iloc[1]["status"] == "failed"

    # Verify BlobClient usage
    mock_blob_client.assert_any_call(source="frontend")
    mock_instance.list_blob_filenames.assert_called_once_with(
        container_name="project-monitoring",
        directory_path="workflows"
    )
    assert mock_instance.read_blob_to_dict.call_count == 2

def test_transform_workflow_overview_df():
    # Arrange: create a mock DataFrame
    now = datetime.now(timezone.utc)
    df_input = pd.DataFrame([
        {
            "repo": "repo1",
            "workflow_name": "build",
            "updated_at": (now - timedelta(days=10)).isoformat(),
            "status": "success",
            "html_url": "https://github.com/powellrhys/repo1/actions/runs/1",
            "duration_seconds": 125,
        },
        {
            "repo": "repo2",
            "workflow_name": "test",
            "updated_at": (now - timedelta(days=90)).isoformat(),
            "status": "failure",
            "html_url": "https://github.com/powellrhys/repo2/actions/runs/2",
            "duration_seconds": 360,
        },
    ])

    # Act
    result = transform_workflow_overview_df(df_input)

    # Assert: check structure
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

    # Check URL prefix and duration format
    assert result.iloc[0]["repo"].startswith("https://github.com/powellrhys/")
    assert "m" in result.iloc[0]["duration"] and "s" in result.iloc[0]["duration"]

    # Check days_since_last_run roughly matches input timing
    days_ago_1 = result[result["workflow_name"] == "build"]["days_since_last_run"].iloc[0]
    days_ago_2 = result[result["workflow_name"] == "test"]["days_since_last_run"].iloc[0]
    assert 9 <= days_ago_1 <= 11
    assert 89 <= days_ago_2 <= 91

    # Check activity flagging
    flag_1 = result[result["workflow_name"] == "build"]["status_flag"].iloc[0]
    flag_2 = result[result["workflow_name"] == "test"]["status_flag"].iloc[0]
    assert flag_1 == "🟢 Active"
    assert flag_2 == "🔴 Inactive"

    # Check sorting (by repo, then days_since_last_run desc)
    assert result.iloc[0]["repo"] <= result.iloc[1]["repo"]
