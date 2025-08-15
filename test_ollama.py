import asyncio
import aiohttp
import json

async def test_ollama():
    print("Testing Ollama connection...")
    
    base_url = "http://localhost:11434"
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"Connecting to {base_url}/api/tags...")
            
            async with session.get(f"{base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                print(f"Response status: {response.status}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    text = await response.text()
                    print(f"Raw response: {text}")
                    
                    try:
                        data = json.loads(text)
                        print(f"JSON data: {data}")
                        
                        models = data.get('models', [])
                        print(f"Models found: {len(models)}")
                        for model in models:
                            print(f"  - {model.get('name', 'Unknown')}")
                            
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                else:
                    error_text = await response.text()
                    print(f"Error response: {error_text}")
                    
    except Exception as e:
        print(f"Connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ollama())
EOF
