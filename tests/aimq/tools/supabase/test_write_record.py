from unittest.mock import Mock, patch

import pytest

from aimq.tools.supabase.write_record import WriteRecord, WriteRecordInput


@pytest.fixture
def write_record_tool():
    return WriteRecord()


@pytest.fixture
def mock_supabase():
    with patch("aimq.tools.supabase.write_record.supabase") as mock:
        yield mock


class TestWriteRecord:
    def test_init(self, write_record_tool):
        """Test initialization of WriteRecord tool."""
        assert write_record_tool.name == "write_record"
        assert (
            write_record_tool.description
            == "Write a record to Supabase. If an ID is provided, updates existing record; otherwise creates new record."
        )
        assert write_record_tool.args_schema == WriteRecordInput

    def test_run_update_record(self, write_record_tool, mock_supabase):
        """Test updating an existing record."""
        table = "test_table"
        record_id = "test-id"
        data = {"name": "test"}
        expected_data = {"id": record_id, **data}

        mock_table = Mock()
        mock_table.update.return_value.eq.return_value.execute.return_value = Mock(
            data=[expected_data]
        )
        mock_supabase.client.table.return_value = mock_table

        result = write_record_tool._run(table=table, data=data, id=record_id)

        assert result == expected_data
        mock_supabase.client.table.assert_called_with(table)
        mock_table.update.assert_called_once_with(data)
        mock_table.update.return_value.eq.assert_called_once_with("id", record_id)

    def test_run_create_record(self, write_record_tool, mock_supabase):
        """Test creating a new record."""
        table = "test_table"
        data = {"name": "test"}
        expected_data = {"id": "new-id", **data}

        mock_table = Mock()
        mock_table.insert.return_value.execute.return_value = Mock(data=[expected_data])
        mock_supabase.client.table.return_value = mock_table

        result = write_record_tool._run(table=table, data=data, id=None)

        assert result == expected_data
        mock_supabase.client.table.assert_called_with(table)
        mock_table.insert.assert_called_once_with(data)

    def test_record_not_found_on_update(self, write_record_tool, mock_supabase):
        """Test behavior when updating a non-existent record."""
        table = "test_table"
        record_id = "non-existent-id"
        data = {"name": "test"}

        mock_table = Mock()
        mock_table.update.return_value.eq.return_value.execute.return_value = Mock(data=[])
        mock_supabase.client.table.return_value = mock_table

        with pytest.raises(ValueError, match=f"No record found with ID {record_id}"):
            write_record_tool._run(table=table, data=data, id=record_id)
