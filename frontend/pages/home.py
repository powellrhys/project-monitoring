# Import python and project dependencies
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

    # Render page title
    st.title("Personal Project Monitoring Dashboard")

    # Render container
    with st.container(border=True):

        # Render application overview paragraph
        st.write(
            """
            This project is a Streamlit-based monitoring dashboard that provides real-time visibility into the
            health and activity of my personal GitHub projects. The app integrates with the GitHub API to collect
            and visualize data from GitHub Actions workflows, giving a clear overview of recent builds, test runs,
            and deployment outcomes across all repositories. It serves as a central hub for tracking CI/CD performance,
            build durations, and any failures that might need attention — all through an interactive web interface.

            In addition to GitHub activity, the dashboard connects to Microsoft Azure using the Azure SDK to fetch and
            display up-to-date information on resource usage and cost metrics. This allows for continuous monitoring of
            cloud spend and resource consumption alongside project development activity. Together, these features create
            a unified monitoring solution that combines CI/CD insights and cloud resource tracking in a lightweight,
            data driven Streamlit app designed for personal developer productivity and cost awareness.
            """
        )
