# Import python dependencies
from shared import Variables
import streamlit as st

def get_navigation(vars: Variables) -> st.navigation:
    """
    Build and return a Streamlit navigation object for the application.

    This method defines the navigation structure of the app by mapping
    page groups (e.g., "Overview", "Trackman") to their corresponding
    Streamlit pages. It then constructs a `st.navigation` object that
    can be used to render and manage page routing within the UI.

    Returns:
        st.navigation: A Streamlit navigation object containing the
        configured pages and navigation hierarchy.
    """
    # Construct pages dictionary
    pages = {
        "Home": [st.Page(page="pages/home.py", title="Home")],
        "Workflows": [
            st.Page(page="pages/workflow_overview.py", title="Workflows Overview"),
            st.Page(page="pages/workflow_analysis.py", title="Workflows Analysis")
        ]
    }

    # Construct streamlit navigation object
    nav = st.navigation(pages)

    return nav
