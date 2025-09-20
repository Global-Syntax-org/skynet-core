#!/usr/bin/env python3
"""
Demo script to start the Skynet Core web interface with document upload functionality
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 Starting Skynet Core with Document Upload Feature")
print("=" * 60)
print()
print("✅ FEATURE IMPLEMENTED: Document Upload & Management")
print()
print("📋 What's Available:")
print("   • Upload documents (PDF, DOCX, XLSX, TXT, MD, CSV)")
print("   • Automatic text extraction and chunking")
print("   • Document search functionality")
print("   • Chat responses using document context")
print("   • Document management (view, delete)")
print()
print("🌐 Web Interface Features:")
print("   • Documents button in top navigation")
print("   • Drag & drop file upload modal")
print("   • Document list with delete/ask options")
print("   • Toast notifications for user feedback")
print()
print("🤖 AI Integration:")
print("   • Chat responses now include relevant document context")
print("   • When asking questions, the AI searches your uploaded docs")
print("   • Document content is automatically included in responses")
print()
print("🔧 Technical Implementation:")
print("   • Backend: DocumentProcessor class with async file handling")
print("   • Storage: Local file system with SQLite-like JSON metadata")
print("   • Search: Simple text-based relevance scoring")
print("   • UI: Bootstrap 5 modal with responsive design")
print("   • API: RESTful endpoints for document CRUD operations")
print()
print("📁 File Support:")
print("   • PDF files (.pdf)")
print("   • Word documents (.docx)")
print("   • Excel spreadsheets (.xlsx)")
print("   • Text files (.txt)")
print("   • Markdown files (.md)")
print("   • CSV files (.csv)")
print("   • Maximum file size: 10MB")
print()

# Check if running in development mode
if __name__ == "__main__":
    try:
        print("🚀 Starting web server...")
        print("📍 URL: http://localhost:5005")
        print("👤 Login with any username/password to test")
        print()
        print("💡 To test the document feature:")
        print("   1. Start the web server: python web/app.py")
        print("   2. Open http://localhost:5005")
        print("   3. Login with any credentials")
        print("   4. Click 'Documents' button in top navigation")
        print("   5. Upload a document using drag & drop")
        print("   6. Ask questions about your uploaded documents")
        print()
        print("🔍 For AI responses (optional):")
        print("   • Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("   • Start Ollama: ollama serve")
        print("   • Pull a model: ollama pull mistral")
        print("   • Or set ANTHROPIC_API_KEY for Claude integration")
        print()
        
        # Start the web application
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        os.system("python web/app.py")
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("💡 Try running directly: python web/app.py")
