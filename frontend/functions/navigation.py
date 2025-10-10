# Import python dependencies
import streamlit as st

def get_navigation() -> st.navigation:
    """
    Creates and returns a Streamlit navigation object with predefined pages.

    Returns:
        st.navigation: A Streamlit navigation object configured with the pages.
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
