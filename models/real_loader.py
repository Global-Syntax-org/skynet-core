import subprocess
import asyncio

class OllamaModelLoader:
    def __init__(self):
        self.model_name = None

    def ensure_model_available(self, model_name: str) -> bool:
        self.model_name = model_name
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to list models: {result.stderr}")
                return False

            if model_name not in result.stdout:
                print(f"🔍 Model '{model_name}' not found locally. Pulling...")
                pull_result = subprocess.run(["ollama", "pull", model_name], capture_output=True, text=True)
                if pull_result.returncode != 0:
                    print(f"❌ Failed to pull model '{model_name}': {pull_result.stderr}")
                    return False
                print(f"✅ Model '{model_name}' pulled successfully.")
            else:
                print(f"✅ Model '{model_name}' is already available.")
            return True
        except Exception as e:
            print(f"❌ Exception during model check: {e}")
            return False

    async def load_model(self):
        if not self.model_name:
            raise RuntimeError("Model name not set before loading.")
        print(f"🚀 Loading model '{self.model_name}'...")
        await asyncio.sleep(0.1)  # Simulate async load
        return True

    def close(self):
        print("🧹 OllamaModelLoader cleanup complete.")

