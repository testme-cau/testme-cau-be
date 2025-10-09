"""
Verbose probe of GPT-5 API response.
Run:
  source venv/bin/activate && export $(grep -v '^#' .env | xargs) && OPENAI_MODEL=gpt-5 python tests/test_gpt5_verbose.py
"""
import os
import json
import time
from datetime import datetime
from openai import OpenAI


def main():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your-openai-api-key-here':
        print('ERROR: OPENAI_API_KEY not set')
        return 1

    model = os.getenv('OPENAI_MODEL', 'gpt-5')
    client = OpenAI(api_key=api_key)

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Respond concisely."},
        {"role": "user", "content": (
            "Return a brief analysis JSON that includes keys:"
            " status:'ok', model:'echo', note:'This is a verbosity probe',"
            " and a short 'sample' text describing Fibonacci numbers."
            " Respond with a natural short paragraph first, then a JSON block."
        )}
    ]

    # Call with gpt-5-compatible params: avoid temperature, use max_completion_tokens
    t0 = time.time()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=300,
    )
    dt_ms = int((time.time() - t0) * 1000)

    # Raw JSON
    raw_json = resp.model_dump()

    # Extract key fields safely
    rid = raw_json.get('id')
    rmodel = raw_json.get('model')
    created = raw_json.get('created')
    created_iso = datetime.utcfromtimestamp(created).isoformat() + 'Z' if isinstance(created, int) else str(created)
    choices = raw_json.get('choices') or []
    choice0 = choices[0] if choices else {}
    finish_reason = (choice0 or {}).get('finish_reason')
    message = (choice0 or {}).get('message') or {}
    role = message.get('role')
    content = message.get('content') or ''
    content_preview = content[:600]

    usage = raw_json.get('usage') or {}
    prompt_tokens = usage.get('prompt_tokens')
    completion_tokens = usage.get('completion_tokens')
    total_tokens = usage.get('total_tokens')

    print('\n=== GPT-5 VERBOSE RESPONSE ===')
    print(f"Model: {rmodel}")
    print(f"ID: {rid}")
    print(f"Created: {created_iso}")
    print(f"Finish reason: {finish_reason}")
    print(f"Latency: {dt_ms} ms")
    print(f"Role: {role}")
    print(f"Content length: {len(content)}")
    print('\n--- Content Preview (first 600 chars) ---')
    print(content_preview)
    print('--- End Preview ---\n')

    print('Usage:')
    print(json.dumps({
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'total_tokens': total_tokens,
        'completion_tokens_details': usage.get('completion_tokens_details'),
        'prompt_tokens_details': usage.get('prompt_tokens_details'),
    }, indent=2))

    # Also print compact raw JSON (truncated if extremely long)
    raw_str = json.dumps(raw_json, indent=2)
    if len(raw_str) > 4000:
        print('\nRaw JSON (truncated):')
        print(raw_str[:4000] + '\n... [truncated] ...')
    else:
        print('\nRaw JSON:')
        print(raw_str)

    # Save to file for later inspection
    out_dir = 'tests/.artifacts'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'gpt5_last_response.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(raw_json, f, ensure_ascii=False, indent=2)
    print(f"\nSaved raw response to: {out_path}")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
