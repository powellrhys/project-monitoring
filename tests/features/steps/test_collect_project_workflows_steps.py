# Import dependencies
from frontend.functions.data_functions import collect_project_workflows
from behave import given, when, then
from unittest.mock import patch

@given("the following workflow filenames are available in container")
def given_workflow_filenames(context):
    """
    GIVEN step:
    Reads workflow filenames from the feature file data table and stores
    them in the context for use in the WHEN step.

    Each filename represents a workflow JSON file stored in the
    project-monitoring container, e.g., "workflows/build_pipeline.json".
    """
    # Convert the table rows into a list of filenames
    context.mock_blob_files = [row["filename"] for row in context.table]

@when("I call collect_project_workflows")
def when_call_collect_project_workflows(context):
    """
    WHEN step:
    Calls the `collect_project_workflows()` function under test.

    Patches `BlobClient` in the module under test to return the
    workflow filenames provided in the feature file, avoiding any
    external storage dependency.
    """
    # Patch BlobClient used inside data_functions
    with patch("frontend.functions.data_functions.BlobClient") as MockBlobClient:
        # Mock instance returned when BlobClient is instantiated
        mock_client_instance = MockBlobClient.return_value
        # Return the workflow filenames from the feature file
        mock_client_instance.list_blob_filenames.return_value = context.mock_blob_files

        # Call the function and store result in the context
        context.result = collect_project_workflows()

@then("I should get a list of workflow filenames")
def then_should_get_list_of_filenames(context):
    """
    THEN step:
    Verifies that the result of `collect_project_workflows()` is a list
    and contains at least one workflow filename.
    """
    assert isinstance(context.result, list)
    assert len(context.result) > 0

@then('each filename should be a string ending with ".json"')
def then_each_filename_is_json(context):
    """
    THEN step:
    Verifies that every filename in the list is a string and ends with '.json'.
    Ensures that workflow filenames conform to expected JSON file format.
    """
    for filename in context.result:
        assert isinstance(filename, str)
        assert filename.endswith(".json")
