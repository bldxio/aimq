import pytest
from unittest.mock import Mock, patch
from aimq.tools.supabase.read_record import ReadRecord, ReadRecordInput

@pytest.fixture
def read_record_tool():
    return ReadRecord()

@pytest.fixture
def mock_supabase():
    with patch('aimq.tools.supabase.read_record.supabase') as mock:
        yield mock

class TestReadRecord:
    def test_init(self, read_record_tool):
        """Test initialization of ReadRecord tool."""
        assert read_record_tool.name == "read_record"
        assert read_record_tool.description == "Read a record from Supabase"
        assert read_record_tool.args_schema == ReadRecordInput
        assert read_record_tool.table == "records"
        assert read_record_tool.select == "*"

    def test_run_with_defaults(self, read_record_tool, mock_supabase):
        """Test reading a record with default parameters."""
        record_id = "test-id"
        expected_data = {"id": record_id, "name": "test"}
        
        mock_result = Mock()
        mock_result.data = [expected_data]
        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = mock_result
        mock_schema = Mock()
        mock_schema.table.return_value = mock_table
        mock_supabase.client.schema.return_value = mock_schema
        
        result = read_record_tool._run(id=record_id)
        
        assert result == expected_data
        mock_supabase.client.schema.assert_called_once_with('public')
        mock_schema.table.assert_called_once_with('records')
        mock_table.select.assert_called_once_with('*')
        mock_table.eq.assert_called_once_with('id', record_id)
        mock_table.limit.assert_called_once_with(1)
        mock_table.execute.assert_called_once()

    def test_run_with_custom_table_and_select(self, read_record_tool, mock_supabase):
        """Test reading a record with custom table and select parameters."""
        record_id = "test-id"
        table = "custom_table"
        select = "id,name"
        expected_data = {"id": record_id, "name": "test"}
        
        mock_result = Mock()
        mock_result.data = [expected_data]
        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = mock_result
        mock_schema = Mock()
        mock_schema.table.return_value = mock_table
        mock_supabase.client.schema.return_value = mock_schema
        
        result = read_record_tool._run(id=record_id, table=table, select=select)
        
        assert result == expected_data
        mock_supabase.client.schema.assert_called_once_with('public')
        mock_schema.table.assert_called_once_with(table)
        mock_table.select.assert_called_once_with(select)
        mock_table.eq.assert_called_once_with('id', record_id)
        mock_table.limit.assert_called_once_with(1)
        mock_table.execute.assert_called_once()

    def test_record_not_found(self, read_record_tool, mock_supabase):
        """Test behavior when record is not found."""
        record_id = "non-existent-id"
        
        mock_result = Mock()
        mock_result.data = []
        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = mock_result
        mock_schema = Mock()
        mock_schema.table.return_value = mock_table
        mock_supabase.client.schema.return_value = mock_schema
        
        with pytest.raises(ValueError, match=f"No record found with ID {record_id} in table records"):
            read_record_tool._run(id=record_id)
