# Import python and project dependencies
from frontend.pages.frontend_sections.workflow_overview import render_workflow_overview
from streamlit_components.ui_components import configure_page_config
from functions.data_functions import collect_latest_workflow_runs
import streamlit as st

# Set page config
configure_page_config(repository_name='project-monitoring',
                      page_icon=":chart_with_upwards_trend:")

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If user logged in, render streamlit content
if st.user.is_logged_in:

    # Read in workflow data
    df = collect_latest_workflow_runs()

    # Render workflow overview page
    render_workflow_overview(df=df)
