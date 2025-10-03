# Import dependencies
from functions.data_functions import transform_workflow_overview_df
import streamlit as st
import pandas as pd

def render_overview_page(df: pd.DataFrame) -> None:
    """
    """
    st.title("Project Workflows Overview")

    df = transform_workflow_overview_df(df=df)

    st.dataframe(
        df,
        column_config={
            "repo": st.column_config.LinkColumn(
                "Repo",
                help="Click to view repository",
                display_text=r"https://github.com/powellrhys/(.*)"
            ),
            "updated_at": st.column_config.DatetimeColumn(
                "Completion Datetime",
                help="Time the workflow run started",
                format="YYYY-MM-DD HH:mm:ss",
            ),
            "workflow_name": st.column_config.TextColumn("Workflow Name"),
            "status": st.column_config.TextColumn("Status"),
            "html_url": st.column_config.LinkColumn(
                "Workflow Run",
                help="Open the GitHub Actions run",
                display_text="View Workflow Run"
            ),
            "duration": st.column_config.TextColumn("Duration"),
            "days_since_last_run": st.column_config.TextColumn("Days Since Latest Run"),
            "status_flag": st.column_config.TextColumn("Pipeline Active Status"),
        },
        hide_index=True,
    )
