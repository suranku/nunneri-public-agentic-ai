"""Model-provider routing for Nunneri runtime calls.

Provider prefixes:
- ollama:<model> or unprefixed local model names -> Ollama
- gemini:<model> -> Google Generative Language API
- claude:<model> -> Anthropic Messages API
- openai:<model> -> OpenAI Responses API
"""
from __future__ import annotations

import os
import json
from typing import Any

import httpx
from langchain_core.messages import BaseMessage, HumanMessage

import ollama_queue

OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")


def split_model(model: str) -> tuple[str, str]:
    if ":" not in model:
        return "ollama", model
    prefix, name = model.split(":", 1)
    if prefix in {"ollama", "gemini", "claude", "openai"}:
        return prefix, name
    return "ollama", model


def configured_models(ollama_models: list[str] | None = None) -> list[dict[str, Any]]:
    ollama_models = ollama_models or []
    models = [
        {"id": m, "provider": "ollama", "configured": True, "local": True}
        for m in ollama_models
    ]
    models.extend([
        {
            "id": "gemini:gemini-2.0-flash",
            "provider": "gemini",
            "configured": bool(os.environ.get("GEMINI_API_KEY")),
            "env": "GEMINI_API_KEY",
        },
        {
            "id": "claude:claude-3-5-sonnet-latest",
            "provider": "anthropic",
            "configured": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "env": "ANTHROPIC_API_KEY",
        },
        {
            "id": "openai:gpt-4.1-mini",
            "provider": "openai",
            "configured": bool(os.environ.get("OPENAI_API_KEY")),
            "env": "OPENAI_API_KEY",
        },
    ])
    return models


def _lc_messages_to_provider_text(messages: list[BaseMessage]) -> str:
    parts: list[str] = []
    for m in messages:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        parts.append(f"{role}: {m.content}")
    return "\n\n".join(parts)


def _plain_messages_to_provider_text(history: list[Any], user_message: str) -> str:
    parts: list[str] = []
    for m in history:
        role = getattr(m, "role", None) or (m.get("role") if isinstance(m, dict) else "user")
        content = getattr(m, "content", None) or (m.get("content") if isinstance(m, dict) else str(m))
        parts.append(f"{role}: {content}")
    parts.append(f"user: {user_message}")
    return "\n\n".join(parts)


async def invoke_langchain_messages(
    model: str,
    system: str,
    messages: list[BaseMessage],
) -> str:
    provider, model_name = split_model(model)
    if provider == "ollama":
        return await _ollama_langchain(model_name, system, messages)
    prompt = _lc_messages_to_provider_text(messages)
    return await _invoke_cloud(provider, model_name, system, prompt)


async def invoke_plain_messages(
    model: str,
    system: str,
    history: list[Any],
    user_message: str,
) -> str:
    provider, model_name = split_model(model)
    if provider == "ollama":
        return await _ollama_plain(model_name, system, history, user_message)
    prompt = _plain_messages_to_provider_text(history, user_message)
    return await _invoke_cloud(provider, model_name, system, prompt)


async def stream_plain_messages(
    model: str,
    system: str,
    history: list[Any],
    user_message: str,
):
    # Cloud providers are returned as one chunk for now. Ollama keeps true streaming.
    provider, model_name = split_model(model)
    if provider == "ollama":
        async for token in _ollama_stream(model_name, system, history, user_message):
            yield token
        return
    yield await invoke_plain_messages(model, system, history, user_message)


async def _ollama_langchain(model: str, system: str, messages: list[BaseMessage]) -> str:
    ollama_msgs = [{"role": "system", "content": system}]
    for m in messages:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        ollama_msgs.append({"role": role, "content": str(m.content)})
    async with ollama_queue.slot():
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{OLLAMA_BASE}/api/chat",
                json={"model": model, "messages": ollama_msgs, "stream": False},
            )
            r.raise_for_status()
            return r.json()["message"]["content"]


async def _ollama_plain(model: str, system: str, history: list[Any], user_message: str) -> str:
    msgs = [{"role": "system", "content": system}]
    for m in history:
        role = getattr(m, "role", None) or (m.get("role") if isinstance(m, dict) else "user")
        content = getattr(m, "content", None) or (m.get("content") if isinstance(m, dict) else str(m))
        msgs.append({"role": role, "content": content})
    msgs.append({"role": "user", "content": user_message})
    async with ollama_queue.slot():
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{OLLAMA_BASE}/api/chat",
                json={"model": model, "messages": msgs, "stream": False},
            )
            r.raise_for_status()
            return r.json()["message"]["content"]


async def _ollama_stream(model: str, system: str, history: list[Any], user_message: str):
    msgs = [{"role": "system", "content": system}]
    for m in history:
        role = getattr(m, "role", None) or (m.get("role") if isinstance(m, dict) else "user")
        content = getattr(m, "content", None) or (m.get("content") if isinstance(m, dict) else str(m))
        msgs.append({"role": role, "content": content})
    msgs.append({"role": "user", "content": user_message})
    async with ollama_queue.slot():
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE}/api/chat",
                json={"model": model, "messages": msgs, "stream": True},
            ) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break


async def _invoke_cloud(provider: str, model: str, system: str, prompt: str) -> str:
    if provider == "gemini":
        return await _invoke_gemini(model, system, prompt)
    if provider == "claude":
        return await _invoke_anthropic(model, system, prompt)
    if provider == "openai":
        return await _invoke_openai(model, system, prompt)
    raise ValueError(f"Unsupported provider prefix: {provider}")


async def _invoke_gemini(model: str, system: str, prompt: str) -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is required for gemini:* models")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, params={"key": key}, json=body)
        r.raise_for_status()
        data = r.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts).strip()


async def _invoke_anthropic(model: str, system: str, prompt: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is required for claude:* models")
    body = {
        "model": model,
        "max_tokens": 2048,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
    return "".join(part.get("text", "") for part in data.get("content", []) if part.get("type") == "text").strip()


async def _invoke_openai(model: str, system: str, prompt: str) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is required for openai:* models")
    body = {
        "model": model,
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post("https://api.openai.com/v1/responses", headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
    if data.get("output_text"):
        return data["output_text"].strip()
    texts: list[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                texts.append(content.get("text", ""))
    return "".join(texts).strip()
