#!/usr/bin/env python
"""Quick test of LLM auto-population system"""

from llm_pool import get_llm_priority_score, get_best_llms_for_operations
import json

print("=" * 60)
print("Testing LLM Priority Scoring System")
print("=" * 60)

# Test items with different sources
test_items = [
    {'name': 'GitHub Copilot', 'source': 'vscode', 'status': 'available'},
    {'name': 'Google Gemini', 'source': 'web', 'status': 'available'},
    {'name': 'ChatGPT', 'source': 'web', 'status': 'available'},
    {'name': 'Ollama', 'source': 'cli', 'status': 'available'},
    {'name': 'Llama', 'source': 'cli', 'status': 'available'},
    {'name': 'local-model', 'source': 'local', 'status': 'available'},
    {'name': 'process-llm', 'source': 'process', 'status': 'running'},
    {'name': 'unavailable-llm', 'source': 'cli', 'status': 'disabled'},
]

print("\nIndividual Priority Scores:")
print("-" * 60)
for item in test_items:
    score = get_llm_priority_score(item)
    status_info = f" ({item.get('status', 'unknown')})" if item.get('status') != 'available' else ""
    print(f"{item['name']:20} [{item['source']:7}]: {score:3} pts{status_info}")

print("\nRanking (sorted by priority):")
print("-" * 60)
ranked = sorted(test_items, key=get_llm_priority_score, reverse=True)
for i, item in enumerate(ranked, 1):
    score = get_llm_priority_score(item)
    if score > 0:  # Only show positive scores
        print(f"{i}. {item['name']:20} {score:3} pts")

print("\n" + "=" * 60)
print("✓ LLM Priority Scoring System Test Complete")
print("=" * 60)
