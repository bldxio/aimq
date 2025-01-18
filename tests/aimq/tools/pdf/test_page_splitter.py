import pytest
from unittest.mock import Mock, patch
from aimq.tools.pdf.page_splitter import PageSplitter, PageSplitterInput
import pypdfium2 as pdfium
import io

@pytest.fixture
def page_splitter_tool():
    return PageSplitter()

@pytest.fixture
def mock_pdf():
    # Create a mock PDF with 2 pages using pypdfium2
    pdf = pdfium.PdfDocument.new()
    
    try:
        # Add two empty pages
        pdf.new_page(width=72, height=72)
        pdf.new_page(width=72, height=72)
        
        # Convert to bytes
        pdf_bytes = io.BytesIO()
        pdf.save(pdf_bytes)
        pdf_bytes.seek(0)
        
        mock = Mock()
        mock.data = pdf_bytes.read()
        mock.filename = "test.pdf"
        return mock
    finally:
        # Ensure PDF document is closed
        pdf.close()

class TestPageSplitter:
    def test_init(self, page_splitter_tool):
        """Test initialization of PageSplitter tool."""
        assert page_splitter_tool.name == "pdf_page_splitter"
        assert page_splitter_tool.description == "Split a PDF file into individual pages"
        assert page_splitter_tool.args_schema == PageSplitterInput

    def test_split_pdf(self, page_splitter_tool, mock_pdf):
        """Test splitting a PDF into individual pages."""
        result = page_splitter_tool._run(file=mock_pdf)
        
        assert isinstance(result, list)
        assert len(result) == 2  # Should have 2 pages
        
        # Verify each page
        for page in result:
            assert "file" in page
            assert "metadata" in page
            assert isinstance(page["metadata"], dict)
            assert "position" in page["metadata"]
            assert "width" in page["metadata"]
            assert "height" in page["metadata"]

    def test_split_empty_pdf(self, page_splitter_tool):
        """Test splitting an empty PDF."""
        # Create a PDF with one empty page
        pdf = pdfium.PdfDocument.new()
        try:
            # Add one empty page
            pdf.new_page(width=72, height=72)
            
            pdf_bytes = io.BytesIO()
            pdf.save(pdf_bytes)
            pdf_bytes.seek(0)
            
            mock = Mock()
            mock.data = pdf_bytes.read()
            mock.filename = "empty.pdf"
            
            result = page_splitter_tool._run(file=mock)
            assert isinstance(result, list)
            assert len(result) == 1  # Should have 1 page
            
            # Verify the page
            page = result[0]
            assert "file" in page
            assert "metadata" in page
            assert isinstance(page["metadata"], dict)
            assert "position" in page["metadata"]
            assert "width" in page["metadata"]
            assert "height" in page["metadata"]
        finally:
            pdf.close()

    def test_invalid_pdf(self, page_splitter_tool):
        """Test handling invalid PDF data."""
        mock = Mock()
        mock.data = b"invalid pdf data"
        mock.filename = "invalid.pdf"
        
        with pytest.raises(Exception):
            page_splitter_tool._run(file=mock)
