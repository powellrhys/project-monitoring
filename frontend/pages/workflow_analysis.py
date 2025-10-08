# Import python and project dependencies
from frontend.pages.frontend_sections.workflow_analysis import render_workflows_analysis
from streamlit_components.ui_components import configure_page_config
import streamlit as st

# Set page config
configure_page_config(repository_name='golf-ui-streamlit',
                      page_icon=":chart_with_upwards_trend:")

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If user logged in, render streamlit content
if st.user.is_logged_in:

    # Render workflow analysis page
    render_workflows_analysis()
