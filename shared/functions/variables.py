# Install python dependencies
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

class Variables():
    """
    """
    def __init__(self, source: str = "backend"):
        """
        Initialize and load all required environment variables into attributes.

        Attributes:
            blob_account_connection_string (str): Azure Blob Storage connection string.
        """
        # Shared variables
        if source == "backend":
            self.blob_account_connection_string = os.getenv("blob_storage_connection_string")
        else:
            self.blob_account_connection_string = st.secrets["general"]["blob_storage_connection_string"]

    def __getitem__(self, key):
        """
        Allow dictionary-style access to environment variable attributes.

        Args: key (str): The attribute name to retrieve.

        Returns: Any: The value of the requested attribute.

        Raises: KeyError: If the requested key does not exist as an attribute.
        """
        # If class as attributes, return items
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key} not found in Variables")
