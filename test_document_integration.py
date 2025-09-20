#!/usr/bin/env python3
"""
Test script for document upload and integration with chat responses
"""
import asyncio
import os
import sys
import tempfile

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skynet.document_processor import DocumentProcessor
from skynet.assistant import SkynetLite


async def test_document_integration():
    """Test document upload and chat integration"""
    
    # Initialize components
    document_processor = DocumentProcessor()
    assistant = SkynetLite()
    
    # Initialize the assistant (this loads the AI model)
    try:
        await assistant.loader_manager.initialize()
        print("✅ AI system initialized")
    except Exception as e:
        print(f"⚠️ AI system not available: {e}")
        print("📝 Testing document functionality only...")
    
    # Create a test document
    test_content = """
    This is a test document about artificial intelligence.
    
    Key Points:
    - AI systems can process natural language
    - Machine learning algorithms improve over time
    - Neural networks are inspired by biological neurons
    - Large language models like GPT can generate human-like text
    """
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        print("🔍 Testing document upload...")
        
        # Read the file content as bytes
        with open(temp_file_path, 'rb') as f:
            file_data = f.read()
        
        # Test document upload
        result = await document_processor.upload_document(
            file_data,
            "test_document.txt",
            "test_user_123"
        )
        
        print(f"✅ Document uploaded: {result}")
        
        print("\n📋 Testing document listing...")
        
        # Test document listing
        documents = await document_processor.list_user_documents("test_user_123")
        print(f"✅ Found {len(documents)} documents")
        for doc in documents:
            print(f"   - {doc['original_name']} (ID: {doc['id']})")
        
        print("\n🔍 Testing document search...")
        
        # Test document search
        search_results = await document_processor.search_documents(
            "artificial intelligence", 
            "test_user_123"
        )
        print(f"✅ Found {len(search_results)} search results")
        for result in search_results:
            print(f"   - Score: {result['relevance_score']}, Content: {result['text'][:100]}...")
        
        print("\n💬 Testing chat with document context...")
        
        # Test chat with document context (only if AI is available)
        if assistant.loader_manager.loader:
            response = await assistant.chat(
                "What are the key points about AI mentioned in my documents?",
                user_id="test_user_123"
            )
            
            print(f"✅ Chat response: {response}")
            
            print("\n💬 Testing chat without document context...")
            
            # Test chat without document context (no user_id)
            response = await assistant.chat(
                "What do you know about machine learning?"
            )
            
            print(f"✅ Chat response (no docs): {response}")
        else:
            print("⚠️ Skipping chat tests - AI system not available")
        
        print("\n🧹 Cleaning up...")
        
        # Clean up - delete the uploaded document
        if documents:
            await document_processor.delete_document(documents[0]['id'], "test_user_123")
            print("✅ Test document deleted")
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            print("✅ Temporary file cleaned up")


if __name__ == "__main__":
    print("🧪 Starting document integration test...\n")
    
    try:
        asyncio.run(test_document_integration())
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
