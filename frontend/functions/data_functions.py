# Import dependencies
from datetime import datetime, timezone
import pandas as pd
import json
import os

def collect_project_workflows() -> list:
    """
    """
    return os.listdir("data/")

def create_repo_workflow_map() -> dict:
    """
    """
    files = collect_project_workflows()

    projects = list(set([file.split("_")[1] for file in files]))

    return {
        project: [
            wf.replace(f"workflows_{project}_", "").replace(".json", "")
            for wf in files if project in wf
        ]
        for project in projects
    }

def collect_latest_workflow_runs() -> pd.DataFrame:
    """
    """
    files = os.listdir("data/")

    workflows = []
    for file in files:
        with open(f"data/{file}", "r", encoding="utf-8") as f:
            data = json.load(f)

        last_run = data[0]
        workflows.append(last_run)

    return pd.DataFrame(workflows)

def transform_workflow_overview_df(df: pd.DataFrame) -> pd.DataFrame:
    """
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

    df["status_flag"] = df["days_since_last_run"].apply(lambda d: "🟢 Active" if d <= 60 else "🔴 Inactive")

    # Filter data columns
    df = df[
        ["repo", "workflow_name", "updated_at", "status", "html_url", "duration", "days_since_last_run", "status_flag"]
    ]

    # Sort data by repo and last days since last run
    df = df.sort_values(by=["repo", "days_since_last_run"], ascending=[True, False])

    return df
