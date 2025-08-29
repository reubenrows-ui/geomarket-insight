from unittest.mock import patch, MagicMock
from google.cloud import bigquery
from tools.export_to_gcs import export_table_to_jsonl

@patch("tools.export_to_gcs.bigquery.Client")
def test_export_table_to_jsonl_calls_extract(mock_client):
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance
    mock_job = MagicMock()
    mock_instance.extract_table.return_value = mock_job

    export_table_to_jsonl(
        project_id="p",
        dataset="d",
        table="t",
        gcs_bucket="bucket",
        gcs_path="dir/out.jsonl",
        user_agent="ua",
    )

    mock_client.assert_called_once()
    mock_instance.extract_table.assert_called_once()
    args, kwargs = mock_instance.extract_table.call_args
    assert args[0] == "p.d.t"
    assert args[1] == "gs://bucket/dir/out.jsonl"

    # destination_format is a string constant
    dest_fmt = kwargs["job_config"].destination_format
    assert dest_fmt in (
        bigquery.DestinationFormat.NEWLINE_DELIMITED_JSON,  # "NEWLINE_DELIMITED_JSON"
        "NEWLINE_DELIMITED_JSON",
    )

    mock_job.result.assert_called_once()
