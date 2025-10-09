# Import dependencies
from frontend.functions.data_functions import create_repo_workflow_map
from behave import given, when, then
from unittest.mock import patch

@given("the following workflow filenames are available")
def given_workflow_filenames(context):
    """
    GIVEN step:
    Reads workflow filenames from the feature file data table.

    Stores the list of filenames in `context.mock_workflow_files` so it can be
    used in the WHEN step. Each filename represents a workflow JSON file
    following the naming convention '<repo>_<workflow>.json'.
    """
    # Convert table rows from the feature file into a list of filenames
    context.mock_workflow_files = [row["filename"] for row in context.table]

@when("I call create_repo_workflow_map")
def when_call_create_repo_workflow_map(context):
    """
    WHEN step:
    Calls the `create_repo_workflow_map()` function under test.

    Uses `unittest.mock.patch` to replace the dependency `collect_project_workflows`
    with a mock that returns the filenames provided in the feature file. This
    ensures the test does not rely on external storage.
    """
    # Patch the dependency inside the module under test
    with patch("frontend.functions.data_functions.collect_project_workflows") as mock_collect:
        # Mock returns the filenames we provided in the feature file
        mock_collect.return_value = context.mock_workflow_files

        # Call the actual function and store the result in the context
        context.result = create_repo_workflow_map()

@then("I should get a dictionary mapping repositories to workflows")
def then_should_get_repo_workflow_map(context):
    """
    THEN step:
    Validates that the result returned by `create_repo_workflow_map` is a
    dictionary. Each key should be a repository name (string), and each value
    should be a list of workflow names (strings).
    """
    result = context.result

    # Check that the result is a dictionary
    assert isinstance(result, dict)

    # Verify each key is a string (repository name) and each value is a list
    for key, value in result.items():
        assert isinstance(key, str)
        assert isinstance(value, list)

@then("each repository should have a list of workflow names")
def then_each_repo_has_workflows(context):
    """
    THEN step:
    Ensures that each repository contains the expected workflows, and that
    workflow names have been cleaned: the repository prefix and '.json'
    extension should be removed.

    Dynamically validates the mapping based on the filenames provided in
    the feature file.
    """
    result = context.result

    # Determine expected repository names from the filenames
    expected_repos = set(f.split("_")[0] for f in context.mock_workflow_files)

    # Verify all expected repositories are present in the result
    assert set(result.keys()) == expected_repos

    # Verify that workflow names have been stripped of repo prefix and '.json'
    for repo, workflows in result.items():
        for wf in workflows:
            # Each workflow name should be a string
            assert isinstance(wf, str)
            # Workflow name should not start with the repo prefix
            assert not wf.startswith(f"{repo}_")
            # Workflow name should not end with '.json'
            assert not wf.endswith(".json")
