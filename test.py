import os
from openai import OpenAI

# Get the API key
api_key = os.getenv("OPENAI_API_KEY", "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").strip()

# Create client
client = OpenAI(api_key=api_key)

# Test the key
try:
    # Simple list models call
    models = client.models.list(limit=1)
    print("API key is valid!")
    print("Available models:", [model.id for model in models.data])
except Exception as e:
    print(f"Error validating API key: {e}")