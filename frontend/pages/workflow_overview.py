# Import python and project dependencies
from frontend.pages.frontend_sections.workflow_overview import render_overview_page
from streamlit_components.ui_components import configure_page_config
from functions.data_functions import collect_latest_workflow_runs
import streamlit as st

# Set page config
configure_page_config(repository_name='project-monitoring')

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If user logged in, render streamlit content
if st.user.is_logged_in:

    df = collect_latest_workflow_runs()

    render_overview_page(df=df)
