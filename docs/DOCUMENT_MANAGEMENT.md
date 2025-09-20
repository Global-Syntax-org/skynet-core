# 📄 Document Management Guide

## Overview

Skynet Core's document management system allows you to upload, process, and search through various document types. The AI assistant can automatically find and use relevant information from your documents when answering questions.

## 🚀 Getting Started

### Accessing Document Management

1. **Web Interface**: Click the "Documents" button in the main chat interface
2. **API**: Use the REST endpoints for programmatic access

### Supported File Types

| Format | Extension | Description |
|--------|-----------|-------------|
| PDF | `.pdf` | Portable Document Format |
| Word | `.docx` | Microsoft Word documents |
| Excel | `.xlsx` | Microsoft Excel spreadsheets |
| Text | `.txt` | Plain text files |
| Markdown | `.md` | Markdown formatted text |
| CSV | `.csv` | Comma-separated values |

### File Size Limits

- **Maximum file size**: 10MB per document
- **Recommended size**: Under 5MB for optimal processing speed

## 📤 Uploading Documents

### Via Web Interface

1. **Open Document Manager**
   - Click the "Documents" button in the main interface
   - The document management modal will open

2. **Upload Methods**
   - **Drag & Drop**: Drag files directly into the upload area
   - **File Browser**: Click "Choose files" to browse and select documents
   - **Multiple Files**: Select multiple files at once for batch upload

3. **Upload Process**
   - Files are validated for type and size
   - Text content is automatically extracted
   - Documents are chunked for AI processing
   - Success/error notifications are displayed

### Via API

```bash
# Upload a document
curl -X POST "http://localhost:5005/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf" \
  -b "session_cookie"
```

## 🔍 Document Search

### Automatic Search During Chat

When you ask questions, the AI automatically searches your documents for relevant context:

```
You: What were the key findings in the research report?
🔍 Searching your documents...
🤖 Skynet: Based on your uploaded research report, the key findings include...
```

### Manual Document Search

```bash
# Search documents via API
curl -X POST "http://localhost:5005/api/documents/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "quarterly revenue"}' \
  -b "session_cookie"
```

### Search Features

- **Semantic Search**: Finds relevant content even with different wording
- **Multi-word Queries**: Handles complex search terms
- **Relevance Scoring**: Results ranked by relevance to your query
- **Context Preservation**: Maintains document source information

## 📋 Document Management

### Viewing Your Documents

1. Open the Document Manager modal
2. View list of uploaded documents with:
   - Document name
   - File type
   - Upload date
   - File size

### Deleting Documents

1. **Via Web Interface**:
   - Click the delete (trash) icon next to any document
   - Confirm deletion in the popup

2. **Via API**:
   ```bash
   curl -X DELETE "http://localhost:5005/api/documents/{document_id}" \
     -b "session_cookie"
   ```

## 🔧 Technical Details

### Document Processing Pipeline

1. **Upload Validation**
   - MIME type verification
   - File size checking
   - User authentication

2. **Text Extraction**
   - PDF: PyPDF2 library
   - Word: python-docx library
   - Excel: openpyxl library
   - Text/Markdown: Direct reading
   - CSV: Pandas processing

3. **Content Chunking**
   - Text split into manageable segments
   - Overlapping chunks for context preservation
   - Metadata preservation (source, page numbers)

4. **Storage**
   - Documents stored in SQLite database
   - User-specific isolation
   - Efficient retrieval indexing

### Security Features

- **User Isolation**: Users can only access their own documents
- **Authentication Required**: All document operations require login
- **File Validation**: Strict MIME type and size checking
- **Secure Storage**: Documents encrypted in database

## 🛠️ Configuration

### Environment Variables

```bash
# Document storage settings
DOCUMENT_UPLOAD_FOLDER="data/uploads"
MAX_DOCUMENT_SIZE_MB=10
ALLOWED_EXTENSIONS="pdf,docx,xlsx,txt,md,csv"

# Processing settings
DOCUMENT_CHUNK_SIZE=1000
DOCUMENT_CHUNK_OVERLAP=200
```

### File Processing Configuration

```python
# In skynet/document_processor.py
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
```

## 🔍 API Reference

### Upload Document

**POST** `/api/documents/upload`

**Headers**: `Content-Type: multipart/form-data`

**Body**: Form data with `file` field

**Response**:
```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "document_id": "doc_123456",
  "filename": "report.pdf"
}
```

### List Documents

**GET** `/api/documents/list`

**Response**:
```json
{
  "success": true,
  "documents": [
    {
      "id": "doc_123456",
      "name": "report.pdf",
      "type": "application/pdf",
      "size": 1024576,
      "uploaded_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Search Documents

**POST** `/api/documents/search`

**Body**:
```json
{
  "query": "quarterly revenue",
  "max_results": 5
}
```

**Response**:
```json
{
  "success": true,
  "results": [
    {
      "document_id": "doc_123456",
      "document_name": "Q1_Report.pdf",
      "relevance_score": 0.85,
      "text": "Quarterly revenue increased by 15%...",
      "metadata": {
        "page": 3,
        "chunk_id": "chunk_789"
      }
    }
  ]
}
```

### Delete Document

**DELETE** `/api/documents/{document_id}`

**Response**:
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

## 🐛 Troubleshooting

### Common Issues

**Upload Failed**:
- Check file size (must be under 10MB)
- Verify file type is supported
- Ensure you're logged in

**Search Not Working**:
- Verify documents were successfully processed
- Check if text extraction completed
- Try different search terms

**API Authentication Errors**:
- Ensure session cookie is included
- Verify user is logged in
- Check authentication headers

### Debug Information

Enable debug logging to see document processing details:

```python
import logging
logging.getLogger('skynet.document_processor').setLevel(logging.DEBUG)
```

## 🔄 Integration with AI Chat

The document system seamlessly integrates with the AI chat functionality:

1. **Automatic Context**: When you ask questions, relevant documents are automatically searched
2. **Source Attribution**: AI responses include references to source documents
3. **Context Preservation**: Document context is maintained throughout conversations
4. **Multi-Document**: AI can synthesize information from multiple documents

### Example Integration

```
You: Compare the revenue figures from Q1 and Q2 reports
🔍 Searching your documents...
📄 Found relevant content in: Q1_Report.pdf, Q2_Report.pdf
🤖 Skynet: Based on your quarterly reports:

Q1 Revenue: $2.3M (from Q1_Report.pdf, page 5)
Q2 Revenue: $2.8M (from Q2_Report.pdf, page 3)

This represents a 21.7% increase from Q1 to Q2...
```

## 📈 Performance Optimization

### Best Practices

1. **File Size**: Keep documents under 5MB for faster processing
2. **Text Quality**: OCR'd PDFs may have lower search accuracy
3. **Descriptive Names**: Use clear, descriptive filenames
4. **Organization**: Group related documents for better context

### Processing Performance

- **Small files** (< 1MB): Process in seconds
- **Medium files** (1-5MB): Process in 10-30 seconds  
- **Large files** (5-10MB): Process in 30-60 seconds

## 🔮 Future Enhancements

Planned improvements for the document management system:

- [ ] **OCR Support**: Process scanned PDFs and images
- [ ] **Document Versioning**: Track document updates and changes
- [ ] **Folder Organization**: Organize documents into folders/categories
- [ ] **Advanced Search**: Boolean operators, date filters, type filters
- [ ] **Document Sharing**: Share documents between users
- [ ] **Bulk Operations**: Upload and manage multiple documents at once
- [ ] **Preview Generation**: Thumbnail previews for documents
- [ ] **Full-Text Indexing**: Enhanced search performance

---

For more information, see the main [README.md](README.md) or check the [API documentation](docs/api.md).
