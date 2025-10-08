# Import dependencies
from frontend.functions.navigation import get_navigation
from unittest.mock import patch, MagicMock

@patch("frontend.functions.navigation.st")
def test_get_navigation(mock_st):
    # Arrange
    mock_vars = MagicMock()  # Variables instance isn't used inside the function
    mock_navigation = MagicMock(name="nav_obj")

    # Mock Streamlit Page and navigation
    mock_st.Page.side_effect = lambda **kwargs: {"page": kwargs["page"], "title": kwargs["title"]}
    mock_st.navigation.return_value = mock_navigation

    # Act
    result = get_navigation(mock_vars)

    # Assert: the returned object is what st.navigation() returned
    assert result == mock_navigation

    # Check that st.Page was called 3 times (Home + 2 workflow pages)
    assert mock_st.Page.call_count == 3

    # Extract args to verify page paths and titles were passed correctly
    page_calls = [call.kwargs for call in mock_st.Page.call_args_list]
    expected_pages = [
        {"page": "pages/home.py", "title": "Home"},
        {"page": "pages/workflow_overview.py", "title": "Workflows Overview"},
        {"page": "pages/workflow_analysis.py", "title": "Workflows Analysis"},
    ]
    for expected in expected_pages:
        assert expected in page_calls

    # Verify st.navigation() called once with correct structure
    mock_st.navigation.assert_called_once()
    args, _ = mock_st.navigation.call_args
    pages_arg = args[0]

    # Structure check
    assert "Home" in pages_arg
    assert "Workflows" in pages_arg
    assert isinstance(pages_arg["Home"], list)
    assert isinstance(pages_arg["Workflows"], list)
    assert len(pages_arg["Home"]) == 1
    assert len(pages_arg["Workflows"]) == 2
