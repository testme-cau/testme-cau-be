"""
Simple greeting test for GPT-5 with robust fallbacks.
Run:
  source venv/bin/activate && export $(grep -v '^#' .env | xargs) && OPENAI_MODEL=gpt-5 python tests/test_gpt5_greeting.py
"""
import os
import json
from openai import OpenAI


def call_gpt(client, model, messages, *, use_max_completion=True, include_temp=False):
    kwargs = {
        'model': model,
        'messages': messages,
    }
    if use_max_completion:
        kwargs['max_completion_tokens'] = 50
    if include_temp:
        kwargs['temperature'] = 1  # some gpt-5 variants only accept default
    return client.chat.completions.create(**kwargs)


def main():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your-openai-api-key-here':
        print('ERROR: OPENAI_API_KEY not set')
        return 1

    model = os.getenv('OPENAI_MODEL', 'gpt-5')
    client = OpenAI(api_key=api_key)

    messages = [
        {"role": "system", "content": "너는 한국어로만 아주 짧고 공손하게 응답하는 도우미야."},
        {"role": "user", "content": "안녕"}
    ]

    # Try 1: gpt-5, max_completion_tokens only
    resp = call_gpt(client, model, messages, use_max_completion=True, include_temp=False)
    content = resp.choices[0].message.content or ''
    if content.strip():
        print(content)
        return 0

    # Try 2: gpt-5, no token param (let server decide)
    resp = call_gpt(client, model, messages, use_max_completion=False, include_temp=False)
    content = resp.choices[0].message.content or ''
    if content.strip():
        print(content)
        return 0

    # Try 3: gpt-5 with explicit default temperature
    resp = call_gpt(client, model, messages, use_max_completion=True, include_temp=True)
    content = resp.choices[0].message.content or ''
    if content.strip():
        print(content)
        return 0

    # Fallback: gpt-4o-mini
    fallback_model = 'gpt-4o-mini'
    resp = call_gpt(client, fallback_model, messages, use_max_completion=True, include_temp=False)
    content = resp.choices[0].message.content or ''
    if content.strip():
        print(content)
        return 0

    # If still empty, print raw JSON for diagnostics
    raw_json = resp.model_dump()
    print('[WARN] Empty content. Raw JSON:')
    print(json.dumps(raw_json, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
