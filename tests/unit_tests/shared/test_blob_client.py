# Import dependencies
from shared.functions.blob_client import BlobClient
from unittest.mock import patch, MagicMock
import pytest
import json

@patch("shared.functions.blob_client.Variables")
@patch("shared.functions.blob_client.BlobServiceClient")
def test_list_blob_filenames_returns_expected_list(mock_blob_service, mock_vars):
    """
    Test that `list_blob_filenames` retrieves all blob names from a container
    using the provided directory prefix.

    This verifies that:
    - The Azure BlobServiceClient is created with the correct connection string.
    - The method lists blobs correctly via `list_blobs()`.
    - The blob names are extracted and returned as a list of strings.
    - The correct Azure methods are invoked with the expected parameters.
    """

    # Setup: Mock the configuration and Azure Blob service objects.
    # We simulate a scenario where the container contains two JSON files.
    mock_vars.return_value.blob_storage_connection_string = "fake-connection"
    mock_blob_client_instance = MagicMock()
    mock_container_client = MagicMock()

    blob1 = MagicMock()
    blob1.name = "folder/blob1.json"
    blob2 = MagicMock()
    blob2.name = "folder/blob2.json"
    mock_container_client.list_blobs.return_value = [blob1, blob2]

    mock_blob_client_instance.get_container_client.return_value = mock_container_client
    mock_blob_service.from_connection_string.return_value = mock_blob_client_instance

    client = BlobClient(source="backend")

    # Exercise: Call the function that retrieves blob names.
    result = client.list_blob_filenames(container_name="test-container", directory_path="folder/")

    # Verify: Check that the blob names are correctly extracted.
    assert result == ["folder/blob1.json", "folder/blob2.json"]

    # Verify: Ensure Azure SDK methods were called correctly.
    mock_blob_service.from_connection_string.assert_called_once_with("fake-connection")
    mock_blob_client_instance.get_container_client.assert_called_once_with("test-container")
    mock_container_client.list_blobs.assert_called_once_with(name_starts_with="folder/")


@patch("shared.functions.blob_client.Variables")
@patch("shared.functions.blob_client.BlobServiceClient")
def test_export_dict_to_blob_uploads_json(mock_blob_service, mock_vars):
    """
    Test that `export_dict_to_blob` serializes Python data to JSON and uploads it to Azure Blob Storage.

    This confirms:
    - Data is converted to JSON correctly.
    - A BlobServiceClient and BlobClient are created properly.
    - The JSON content is uploaded with the correct overwrite flag.
    """

    # Setup: Create mocks for configuration and Azure Blob clients.
    mock_vars.return_value.blob_storage_connection_string = "conn-string"
    mock_service_client = MagicMock()
    mock_blob_client = MagicMock()
    mock_service_client.get_blob_client.return_value = mock_blob_client
    mock_blob_service.from_connection_string.return_value = mock_service_client

    client = BlobClient(source="backend")
    sample_data = [{"key": "value"}]

    # Exercise: Execute the function that uploads the data to Azure Blob Storage.
    client.export_dict_to_blob(sample_data, "container1", "output.json")

    # Verify: The BlobServiceClient was initialized with the expected connection string.
    mock_blob_service.from_connection_string.assert_called_once_with("conn-string")

    # Verify: The correct blob was targeted for upload.
    mock_service_client.get_blob_client.assert_called_once_with(
        container="container1", blob="output.json"
    )

    # Verify: The uploaded content matches the serialized JSON string.
    uploaded_json = json.dumps(sample_data)
    mock_blob_client.upload_blob.assert_called_once_with(uploaded_json, overwrite=True)


@patch("shared.functions.blob_client.Variables")
@patch("shared.functions.blob_client.BlobServiceClient")
def test_read_blob_to_dict_downloads_and_parses_json(mock_blob_service, mock_vars):
    """
    Test that `read_blob_to_dict` downloads JSON blob content and returns
    the deserialized Python object.

    This ensures:
    - The blob is downloaded correctly using Azure SDK mocks.
    - The byte stream is decoded and parsed as JSON.
    - The function returns the correct Python object.
    """

    # Setup: Prepare mocked connection, service client, and blob client.
    # We simulate a valid JSON payload returned from Azure.
    mock_vars.return_value.blob_storage_connection_string = "fake-string"
    mock_service_client = MagicMock()
    mock_blob_client = MagicMock()

    fake_data = [{"x": 1, "y": 2}]
    mock_download = MagicMock()
    mock_download.readall.return_value = json.dumps(fake_data).encode("utf-8")

    mock_blob_client.download_blob.return_value = mock_download
    mock_service_client.get_blob_client.return_value = mock_blob_client
    mock_blob_service.from_connection_string.return_value = mock_service_client

    client = BlobClient(source="backend")

    # Exercise: Read and parse blob content from the simulated Azure client.
    result = client.read_blob_to_dict(container="test-container", input_filename="file.json")

    # Verify: The data returned from the method matches the expected Python object.
    assert result == fake_data

    # Verify: The expected Azure client methods were called.
    mock_blob_service.from_connection_string.assert_called_once_with("fake-string")
    mock_service_client.get_blob_client.assert_called_once_with(
        container="test-container", blob="file.json"
    )
    mock_blob_client.download_blob.assert_called_once()
    mock_download.readall.assert_called_once()


@patch("shared.functions.blob_client.Variables")
@patch("shared.functions.blob_client.BlobServiceClient")
def test_read_blob_to_dict_raises_jsondecodeerror_on_invalid_json(mock_blob_service, mock_vars):
    """
    Test that `read_blob_to_dict` raises `json.JSONDecodeError` when invalid JSON is downloaded.

    This verifies the error-handling behavior of the function when malformed
    JSON content is retrieved from a blob.
    """

    # Setup: Mock Azure Blob client to simulate invalid JSON download.
    mock_vars.return_value.blob_storage_connection_string = "fake-string"
    mock_service_client = MagicMock()
    mock_blob_client = MagicMock()

    mock_download = MagicMock()
    mock_download.readall.return_value = b"{invalid-json}"  # Simulated bad JSON
    mock_blob_client.download_blob.return_value = mock_download
    mock_service_client.get_blob_client.return_value = mock_blob_client
    mock_blob_service.from_connection_string.return_value = mock_service_client

    client = BlobClient(source="backend")

    # Exercise & Verify: Expect json.JSONDecodeError to be raised when parsing invalid data.
    with pytest.raises(json.JSONDecodeError):
        client.read_blob_to_dict(container="test-container", input_filename="bad.json")
