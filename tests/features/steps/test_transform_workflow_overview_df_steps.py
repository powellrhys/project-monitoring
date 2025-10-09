# Import dependencies
from frontend.functions.data_functions import transform_workflow_overview_df
from behave import given, when, then
from datetime import datetime
import pandas as pd

@given("the following workflow data")
def given_workflow_data(context):
    """
    GIVEN step:
    Build a pandas DataFrame from the Gherkin data table provided
    in the feature file.
    """
    # Convert the Behave table to a list of dictionaries
    data = [row.as_dict() for row in context.table]

    # Convert types: duration_seconds to int, updated_at to datetime
    for item in data:
        item["duration_seconds"] = int(item["duration_seconds"])
        item["updated_at"] = datetime.fromisoformat(
            item["updated_at"].replace("Z", "+00:00")
        )

    # Store the DataFrame in the Behave context
    context.input_df = pd.DataFrame(data)


@when("I call transform_workflow_overview_df")
def when_call_transform_workflow_overview_df(context):
    """
    WHEN step:
    Call the transform_workflow_overview_df function on the input DataFrame.
    """
    context.result = transform_workflow_overview_df(context.input_df)


@then("I should get a transformed pandas DataFrame")
def then_should_get_dataframe(context):
    """
    THEN step:
    Check that the result is a pandas DataFrame and contains all expected columns.
    """
    df = context.result

    # Assert result type
    assert isinstance(df, pd.DataFrame), "Result is not a pandas DataFrame."

    # Define expected columns after transformation
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

    # Assert all expected columns exist
    assert list(df.columns) == expected_cols, "DataFrame columns do not match expected."


@then("it should contain formatted durations, URLs, and status flags")
def then_check_transformed_values(context):
    """
    THEN step:
    Validate that durations are formatted as 'Xm Ys', repo URLs are correctly prefixed,
    days_since_last_run is integer, and status_flag values are valid.
    """
    df = context.result

    # Durations formatted as 'Xm Ys'
    assert all("m" in val and "s" in val for val in df["duration"]), \
        "Not all durations are properly formatted."

    # Repo URLs correctly prefixed
    assert all(val.startswith("https://github.com/powellrhys/") for val in df["repo"]), \
        "Repo URLs are not correctly prefixed."

    # days_since_last_run are integers
    assert pd.api.types.is_integer_dtype(df["days_since_last_run"]), \
        "days_since_last_run column is not integer type."

    # status_flag values only contain valid options
    valid_flags = {"🟢 Active", "🔴 Inactive"}
    assert set(df["status_flag"].unique()).issubset(valid_flags), \
        "status_flag column contains unexpected values."


@then(u'the status_flag column should correctly reflect the active_status')
def step_check_status_flag(context):
    """
    THEN step:
    Verify that each status_flag in the transformed DataFrame matches
    the expected value derived from the original input_df's active_status column.
    """
    transformed_df = context.result
    input_df = context.input_df.set_index("workflow_name")  # Use input DataFrame for reference

    for idx, row in transformed_df.iterrows():
        workflow_name = row["workflow_name"]
        active_status = input_df.loc[workflow_name, "active_status"]
        expected_flag = "🟢 Active" if active_status.strip().lower() == "active" else "🔴 Inactive"
        actual_flag = row["status_flag"]

        assert actual_flag == expected_flag, (
            f"status_flag for workflow '{workflow_name}' is '{actual_flag}' "
            f"but expected '{expected_flag}' based on active_status='{active_status}'"
        )
