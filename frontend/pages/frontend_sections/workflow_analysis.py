# Import dependencies
from streamlit_components.plot_functions import PlotlyPlotter
from functions.data_functions import create_repo_workflow_map
import streamlit as st


import json

def render_workflows_analysis() -> None:
    """
    """
    st.title("Workflow Analysis")

    repo_wf_map = create_repo_workflow_map()

    columns = st.columns([1, 1, 1, 2, 1])

    with columns[0]:
        repo = st.selectbox(label="Repository", options=repo_wf_map.keys())

    with columns[1]:
        workflow = st.selectbox(label="Workflow", options=repo_wf_map[repo])

    with open(f"data/workflows_{repo}_{workflow}.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    import pandas as pd

    df = pd.DataFrame(data=data)

    df['created_at'] = pd.to_datetime(df['created_at'])
    df['conclusion'] = df['conclusion'].str.capitalize()
    df['status'] = df['status'].str.capitalize()

    with columns[0]:
        st.link_button(label="Navigate to Workflow",
                       url='/'.join(data[0]["html_url"].split('/')[:-2]),
                       use_container_width=True)

    with columns[-1]:
        n_runs = st.slider(label="Most Recent Pipeline Runs", min_value=5, max_value=30, value=10)

    with st.expander(label="Workflow Performance Metrics", expanded=True):

        columns = st.columns([2, 1])

        with columns[0]:

            st.plotly_chart(PlotlyPlotter(
                df=df.head(n_runs),
                x='created_at',
                y='duration_seconds',
                title='Workflow Run Duration Over Time',
                markers=True,
                labels={'duration_seconds': 'Duration (s)', 'created_at': 'Run Date'}).plot_line())

        with columns[-1]:
            st.plotly_chart(PlotlyPlotter(
                df=df.head(n_runs),
                names='conclusion',
                title='Workflow Status Distribution'
            ).plot_pie())

    with st.expander(label="Workflow Breakdown", expanded=True):
        st.dataframe(
            df.head(n_runs).drop(["run_number"], axis=1),
            column_config={
                "repo": st.column_config.LinkColumn(
                    "Repo",
                    help="Click to view repository",
                    display_text=r"https://github.com/powellrhys/(.*)"
                ),
                "created_at": st.column_config.DatetimeColumn(
                    "Start Datetime",
                    help="Time the workflow run started",
                    format="YYYY-MM-DD HH:mm:ss",
                ),
                "updated_at": st.column_config.DatetimeColumn(
                    "Completion Datetime",
                    help="Time the workflow run last updated",
                    format="YYYY-MM-DD HH:mm:ss",
                ),
                "workflow_name": st.column_config.TextColumn("Workflow Name"),
                "status": st.column_config.TextColumn("Status"),
                "conclusion": st.column_config.TextColumn("Conclusion"),
                "html_url": st.column_config.LinkColumn(
                    "Workflow Run",
                    help="Open the GitHub Actions run",
                    display_text="View Workflow Run"
                ),
                "duration_seconds": st.column_config.TextColumn("Duration (s)"),
            },
            hide_index=True,
        )
