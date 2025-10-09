# Import dependencies
from shared.functions.variables import Variables
from unittest.mock import patch
import pytest

@patch("shared.functions.variables.os.getenv")
def test_backend_source_loads_env_variables(mock_getenv):
    """
    Test that when the source is 'backend', environment variables are loaded using os.getenv.

    This verifies:
    - The blob storage connection string and GitHub token are retrieved from the environment.
    - The correct attributes are set on the Variables instance.
    """

    # Setup: Mock os.getenv to return specific fake values for our test.
    mock_getenv.side_effect = lambda key: {
        "blob_storage_connection_string": "fake-conn-string",
        "GITHUB_TOKEN": "fake-token"
    }.get(key)

    # Exercise: Initialize the Variables class with source="backend".
    vars_instance = Variables(source="backend")

    # Verify: Both expected attributes are loaded correctly.
    assert vars_instance.blob_storage_connection_string == "fake-conn-string"
    assert vars_instance.GITHUB_TOKEN == "fake-token"

    # Verify: os.getenv was called with both expected keys.
    mock_getenv.assert_any_call("blob_storage_connection_string")
    mock_getenv.assert_any_call("GITHUB_TOKEN")


@patch("shared.functions.variables.st")
def test_frontend_source_loads_from_streamlit_secrets(mock_st):
    """
    Test that when the source is not 'backend', Streamlit secrets are used instead of environment variables.

    This verifies:
    - The correct blob storage connection string is read from st.secrets.
    - The environment is not accessed for GITHUB_TOKEN.
    """

    # Setup: Mock Streamlit secrets to mimic a typical structure used in deployment.
    mock_st.secrets = {
        "general": {
            "blob_storage_connection_string": "frontend-conn-string"
        }
    }

    # Exercise: Initialize Variables with a non-backend source.
    vars_instance = Variables(source="frontend")

    # Verify: The blob storage string is correctly pulled from Streamlit secrets.
    assert vars_instance.blob_storage_connection_string == "frontend-conn-string"

    # Verify: No GITHUB_TOKEN should exist in frontend mode.
    assert not hasattr(vars_instance, "GITHUB_TOKEN")


def test_getitem_returns_existing_attribute():
    """
    Test the dictionary-style attribute access for Variables.

    This ensures:
    - Existing attributes can be retrieved using vars_instance[key].
    """

    # Setup: Create a Variables-like instance with a known attribute.
    vars_instance = Variables.__new__(Variables)
    vars_instance.blob_storage_connection_string = "sample-value"

    # Exercise: Retrieve the value using dictionary-style syntax.
    result = vars_instance["blob_storage_connection_string"]

    # Verify: The retrieved value matches the stored attribute.
    assert result == "sample-value"


def test_getitem_raises_keyerror_for_missing_key():
    """
    Test that accessing a missing key via dictionary-style syntax raises KeyError.

    This ensures:
    - Proper error handling when trying to access a non-existent attribute.
    """

    # Setup: Create an empty Variables instance without setting attributes.
    vars_instance = Variables.__new__(Variables)

    # Exercise & Verify: Expect a KeyError with a clear message for invalid key access.
    with pytest.raises(KeyError) as exc_info:
        _ = vars_instance["nonexistent_key"]

    # Verify: The error message includes the missing key name.
    assert "nonexistent_key not found in Variables" in str(exc_info.value)
