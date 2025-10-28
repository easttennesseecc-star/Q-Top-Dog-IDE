#!/usr/bin/env python3
import requests
import json

print("Testing Q Assistant LLM configuration endpoint...")

try:
    response = requests.get("http://127.0.0.1:8000/llm_config/q_assistant", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print("\n✓ Endpoint working!")
        print("\nResponse:")
        print(json.dumps(data, indent=2))
        print(f"\nStatus: {data.get('status')}")
        print(f"Ready: {data.get('ready')}")
        if data.get('llm'):
            print(f"LLM Name: {data['llm'].get('name')}")
            print(f"LLM Type: {data['llm'].get('type')}")
    else:
        print(f"✗ Error: Status {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"✗ Connection error: {e}")
