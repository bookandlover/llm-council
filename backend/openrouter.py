"""Multi-provider API client for making LLM requests to native APIs."""

import httpx
from typing import List, Dict, Any, Optional
from .config import (
    OPENAI_API_KEY, OPENAI_API_URL,
    ANTHROPIC_API_KEY, ANTHROPIC_API_URL,
    GOOGLE_API_KEY, GOOGLE_API_URL
)


async def query_openai(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """Query OpenAI API directly."""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                OPENAI_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }

    except httpx.HTTPStatusError as e:
        print(f"Error querying OpenAI model {model}: {e}")
        try:
            print(f"Response body: {e.response.text}")
        except:
            pass
        return None
    except Exception as e:
        print(f"Error querying OpenAI model {model}: {e}")
        return None


async def query_anthropic(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """Query Anthropic API directly."""
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    # Convert messages format for Anthropic
    # Extract system message if present
    system_message = None
    converted_messages = []

    for msg in messages:
        if msg['role'] == 'system':
            system_message = msg['content']
        else:
            converted_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

    payload = {
        "model": model,
        "messages": converted_messages,
        "max_tokens": 4096,
    }

    if system_message:
        payload["system"] = system_message

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            content = data['content'][0]['text']

            return {
                'content': content,
                'reasoning_details': None
            }

    except httpx.HTTPStatusError as e:
        print(f"Error querying Anthropic model {model}: {e}")
        print(f"Request payload: {payload}")
        try:
            print(f"Response body: {e.response.text}")
        except:
            pass
        return None
    except Exception as e:
        print(f"Error querying Anthropic model {model}: {e}")
        return None


async def query_google(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """Query Google Gemini API directly."""
    # Gemini API URL format: base_url/{model}:generateContent?key={api_key}
    url = f"{GOOGLE_API_URL}/{model}:generateContent?key={GOOGLE_API_KEY}"

    headers = {
        "Content-Type": "application/json",
    }

    # Convert messages to Gemini format
    contents = []
    system_instruction = None

    for msg in messages:
        if msg['role'] == 'system':
            system_instruction = msg['content']
        elif msg['role'] == 'user':
            contents.append({
                'role': 'user',
                'parts': [{'text': msg['content']}]
            })
        elif msg['role'] == 'assistant':
            contents.append({
                'role': 'model',
                'parts': [{'text': msg['content']}]
            })

    payload = {
        "contents": contents,
    }

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            content = data['candidates'][0]['content']['parts'][0]['text']

            return {
                'content': content,
                'reasoning_details': None
            }

    except httpx.HTTPStatusError as e:
        print(f"Error querying Google model {model}: {e}")
        try:
            print(f"Response body: {e.response.text}")
        except:
            pass
        return None
    except Exception as e:
        print(f"Error querying Google model {model}: {e}")
        return None


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via its native API.

    Args:
        model: Model identifier (e.g., "openai/gpt-4o", "anthropic/claude-sonnet-4.5")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    # Parse provider and model name from identifier
    if '/' not in model:
        print(f"Invalid model identifier format: {model}")
        return None

    provider, model_name = model.split('/', 1)

    # Route to appropriate API based on provider
    if provider == 'openai':
        return await query_openai(model_name, messages, timeout)
    elif provider == 'anthropic':
        return await query_anthropic(model_name, messages, timeout)
    elif provider == 'google':
        return await query_google(model_name, messages, timeout)
    else:
        print(f"Unknown provider: {provider}")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel using their native APIs.

    Args:
        models: List of model identifiers (e.g., ["openai/gpt-4o", "anthropic/claude-sonnet-4.5"])
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    import asyncio

    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
