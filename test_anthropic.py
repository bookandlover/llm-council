"""Test script to verify Anthropic API connection and model names."""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Test different model names
MODEL_NAMES_TO_TEST = [
    "claude-sonnet-4.5",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-latest",
    "claude-3-sonnet-20240229",
]

async def test_model(model_name: str):
    """Test a specific model name."""
    print(f"\n{'='*60}")
    print(f"Testing model: {model_name}")
    print('='*60)

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "Hello, say hi back in one word."}
        ],
        "max_tokens": 20,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                content = data['content'][0]['text']
                print(f"✅ SUCCESS! Response: {content}")
                return True
            else:
                print(f"❌ FAILED")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def main():
    print("="*60)
    print("Anthropic API Model Name Test")
    print("="*60)

    if not ANTHROPIC_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY not found in .env file")
        return

    print(f"API Key found: {ANTHROPIC_API_KEY[:20]}...")

    for model_name in MODEL_NAMES_TO_TEST:
        success = await test_model(model_name)
        if success:
            print(f"\n🎉 Found working model: {model_name}")
            break

    print("\n" + "="*60)
    print("Test completed")
    print("="*60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
