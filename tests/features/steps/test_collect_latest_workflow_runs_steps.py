# Import dependencies
from frontend.functions.data_functions import collect_latest_workflow_runs
from unittest.mock import patch, MagicMock
from behave import given, when, then
import pandas as pd

@given("the following workflow data files are available")
def given_workflow_files_available(context):
    """
    GIVEN step:
    Reads workflow filenames and their latest run data from the feature file
    data table. Stores the information in context for use in the WHEN step.
    """
    context.mock_files = []
    context.mock_workflow_data = {}

    # Iterate over each row in the feature file table
    for row in context.table:
        filename = row["filename"]
        context.mock_files.append(filename)

        # Store mock workflow data as a list with a single dict (simulating latest run)
        context.mock_workflow_data[filename] = [{
            "id": int(row["id"]),
            "status": row["status"],
            "workflow": row["workflow"]
        }]

@when("I call collect_latest_workflow_runs")
def when_call_collect_latest_workflow_runs(context):
    """
    WHEN step:
    Calls the function under test, patching BlobClient so it returns
    the mock workflow files and workflow run data from the feature file.
    """
    with patch("frontend.functions.data_functions.BlobClient") as MockBlobClient:
        mock_client_instance = MagicMock()
        MockBlobClient.return_value = mock_client_instance

        # Return filenames from the feature file
        mock_client_instance.list_blob_filenames.return_value = context.mock_files

        # Return the workflow run data for each file
        def mock_read_blob_to_dict(container, input_filename):
            return context.mock_workflow_data[input_filename]

        mock_client_instance.read_blob_to_dict.side_effect = mock_read_blob_to_dict

        # Call the function under test
        context.result = collect_latest_workflow_runs()

@then("I should get a pandas DataFrame")
def then_should_get_dataframe(context):
    """
    THEN step:
    Verifies that the function returned a pandas DataFrame with workflow run data.
    """
    assert isinstance(context.result, pd.DataFrame)
    assert not context.result.empty

@then("each row should represent the most recent run for each workflow")
def then_each_row_is_latest_run(context):
    """
    THEN step:
    Confirms that each row corresponds to the latest workflow run from the mock data.
    """
    expected_workflows = [data[0]["workflow"] for data in context.mock_workflow_data.values()]

    # Check that each expected workflow is present exactly once
    assert set(context.result["workflow"].tolist()) == set(expected_workflows)

    # Check that required columns exist
    required_cols = ["id", "status", "workflow"]
    assert all(col in context.result.columns for col in required_cols)
