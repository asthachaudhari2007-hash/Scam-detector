# -*- coding: utf-8 -*-
"""
Quick standalone test for your Gemini API key/setup.
Run this directly to see the exact error, without going through Flask.

Usage (from your scam-detector folder, with venv active):
    python test_gemini.py
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] python-dotenv loaded, .env file read (if present)")
except ImportError:
    print("[WARN] python-dotenv not installed - .env file will NOT be read automatically")
    print("       Run: pip install python-dotenv")

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("[FAIL] GEMINI_API_KEY is not set in the environment.")
    print("       Check your .env file has a line: GEMINI_API_KEY=your-key-here")
    print("       And that it's in the same folder as this script.")
    raise SystemExit(1)

print(f"[OK] GEMINI_API_KEY found (starts with: {api_key[:6]}...)")

try:
    from google import genai
    print("[OK] google-genai package is installed")
except ImportError:
    print("[FAIL] google-genai is not installed.")
    print("       Run: pip uninstall google-generativeai -y")
    print("       Then: pip install google-genai")
    raise SystemExit(1)

client = genai.Client(api_key=api_key)

# Try a couple of models in order — if the first is overloaded (503),
# fall back to a lighter/older one that usually has more headroom.
candidate_models = ["gemini-3.5-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash"]

last_error = None
for model_name in candidate_models:
    try:
        print(f"[OK] Client created, sending a test message to {model_name}...")

        response = client.models.generate_content(
            model=model_name,
            contents="Say hello in one short sentence.",
        )

        print("\n========================================")
        print(f"SUCCESS with model '{model_name}'! Gemini responded:")
        print(response.text)
        print("========================================")
        break

    except Exception as e:
        print(f"[FAIL] {model_name} -> {type(e).__name__}: {e}\n")
        last_error = e
else:
    print("\n========================================")
    print("All candidate models failed. Last error:")
    print(f"Error type: {type(last_error).__name__}")
    print(f"Error message: {last_error}")
    print("========================================")
    raise last_error