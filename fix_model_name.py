import re

# Read the current ollama_loader.py
with open('loaders/ollama_loader.py', 'r') as f:
    content = f.read()

# Replace the ensure_model_available method to handle model name variations
old_method = '''    async def ensure_model_available(self, model_name: str = "mistral") -> bool:
        """Check if model is available, pull it if not"""
        if not self.available_models:
            await self.initialize()
        
        if model_name in self.available_models:
            logger.info(f"Model {model_name} is already available")
            return True'''

new_method = '''    async def ensure_model_available(self, model_name: str = "mistral") -> bool:
        """Check if model is available, pull it if not"""
        if not self.available_models:
            await self.initialize()
        
        # Check for exact match or with :latest tag
        model_variants = [model_name, f"{model_name}:latest"]
        if model_name.endswith(":latest"):
            base_name = model_name.replace(":latest", "")
            model_variants.append(base_name)
        
        for variant in model_variants:
            if variant in self.available_models:
                logger.info(f"Model {variant} is available")
                return True'''

# Replace the method
content = content.replace(old_method, new_method)

# Write back the updated content
with open('loaders/ollama_loader.py', 'w') as f:
    f.write(content)

print("Updated ollama_loader.py to handle model name variations")
