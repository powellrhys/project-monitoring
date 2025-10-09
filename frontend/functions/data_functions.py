# Import dependencies
from datetime import datetime, timezone
from shared import BlobClient
import pandas as pd

def collect_project_workflows() -> list:
    """
    Retrieve a list of all workflow JSON files stored in the local data directory.

    Returns:
        list: A list of filenames representing saved workflow data.
    """
    return [file.split("/")[-1] for file in BlobClient(source="frontend")
            .list_blob_filenames(container_name="project-monitoring", directory_path="workflows")]

def create_repo_workflow_map() -> dict:
    """
    Create a mapping between repositories and their corresponding workflows.

    Scans the data directory for workflow JSON files and groups them by repository
    name, based on the file naming convention 'workflows_<repo>_<workflow>.json'.

    Returns:
        dict: A dictionary mapping each repository name to a list of its workflows.
    """
    # Collect files
    files = collect_project_workflows()

    # Collect list of unique projects
    projects = list(set([file.split("_")[0] for file in files]))

    return {
        project: [
            wf.replace(f"{project}_", "").replace(".json", "")
            for wf in files if project in wf
        ]
        for project in projects
    }

def collect_latest_workflow_runs() -> pd.DataFrame:
    """
    Collect the most recent workflow run from each workflow JSON file.

    Reads workflow data files from the data directory, extracts the latest recorded
    run from each, and compiles the results into a pandas DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the most recent workflow run per file.
    """
    # List files
    files = BlobClient(source="frontend") \
        .list_blob_filenames(container_name="project-monitoring", directory_path="workflows")

    # Load all files and store latest workflow runs
    workflows = []
    for file in files:
        data = BlobClient(source="frontend") \
            .read_blob_to_dict(container="project-monitoring", input_filename=f"{file}")

        # Grab last run and append to workflows list
        last_run = data[0]
        workflows.append(last_run)

    return pd.DataFrame(workflows)

def transform_workflow_overview_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform workflow run data for presentation in the workflow overview dashboard.

    Enhances the input DataFrame by formatting durations, calculating days since the
    last run, flagging inactive workflows, and sorting for readability.

    Args:
        df (pd.DataFrame): A DataFrame containing workflow run data.

    Returns:
        pd.DataFrame: A transformed and sorted DataFrame ready for display.
    """
    # Convert seconds → minutes:seconds and append url prefix to repo column
    df["duration"] = df["duration_seconds"].apply(lambda x: f"{int(x // 60)}m {int(x % 60)}s")
    df["repo"] = "https://github.com/powellrhys/" + df["repo"]

    # Ensure updated_at is a datetime
    df["updated_at"] = pd.to_datetime(df["updated_at"], utc=True)

    # Today's date (UTC to match GitHub timestamps)
    today = datetime.now(timezone.utc)

    # Calculate days since last update
    df["days_since_last_run"] = (today - df["updated_at"]).dt.days

    # Create status flag column
    df["status_flag"] = df["active_status"] \
        .apply(lambda d: "🟢 Active" if d.strip().lower() == "active" else "🔴 Inactive")

    # Filter data columns
    df = df[
        ["repo", "workflow_name", "updated_at", "status", "html_url", "duration", "days_since_last_run", "status_flag"]
    ]

    # Sort data by repo and last days since last run
    df = df.sort_values(by=["repo", "days_since_last_run"], ascending=[True, False])

    return df
