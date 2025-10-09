# Import dependencies
from frontend.functions.navigation import get_navigation
from unittest.mock import patch, MagicMock

@patch("frontend.functions.navigation.st")
def test_get_navigation(mock_st):
    """
    Test that `get_navigation` correctly builds the Streamlit navigation structure
    and returns the expected navigation object.

    Steps:
    - Mock Streamlit (`st`) methods `Page` and `navigation`.
    - Verify that `st.Page` is called three times (Home + two workflow pages).
    - Check that page paths and titles are passed correctly to each Page.
    - Confirm that `st.navigation()` is called once with a structured dict
      grouping "Home" and "Workflows" pages.
    - Assert that the function returns the same object returned by `st.navigation()`.
    """
    # Arrange ---------------------------------------------------------------
    # Mock a dummy Variables object (not used internally)
    mock_vars = MagicMock()

    # Create a mock navigation object to simulate what st.navigation() returns
    mock_navigation = MagicMock(name="nav_obj")

    # Mock Streamlit's Page() to return a dictionary describing the page
    mock_st.Page.side_effect = lambda **kwargs: {"page": kwargs["page"], "title": kwargs["title"]}

    # Mock Streamlit's navigation() to return the mock_navigation object
    mock_st.navigation.return_value = mock_navigation

    # Act -------------------------------------------------------------------
    # Call the function under test
    result = get_navigation(mock_vars)

    # Assert ---------------------------------------------------------------
    # Ensure the return value is what st.navigation() produced
    assert result == mock_navigation

    # Confirm that st.Page() was called exactly 3 times
    # (Home + Workflow Overview + Workflow Analysis)
    assert mock_st.Page.call_count == 3

    # Extract arguments used in each Page() call for validation
    page_calls = [call.kwargs for call in mock_st.Page.call_args_list]

    # Define the expected page configurations
    expected_pages = [
        {"page": "pages/home.py", "title": "Home"},
        {"page": "pages/workflow_overview.py", "title": "Workflows Overview"},
        {"page": "pages/workflow_analysis.py", "title": "Workflows Analysis"},
    ]

    # Validate that all expected pages were created
    for expected in expected_pages:
        assert expected in page_calls

    # Confirm that st.navigation() was called once
    mock_st.navigation.assert_called_once()

    # Extract the argument passed to st.navigation()
    args, _ = mock_st.navigation.call_args
    pages_arg = args[0]

    # Structural checks on the navigation configuration
    assert "Home" in pages_arg
    assert "Workflows" in pages_arg
    assert isinstance(pages_arg["Home"], list)
    assert isinstance(pages_arg["Workflows"], list)
    assert len(pages_arg["Home"]) == 1
    assert len(pages_arg["Workflows"]) == 2
