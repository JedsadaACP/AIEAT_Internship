# -*- coding: utf-8 -*-
"""
Simple Translation Test - Just translate, no complex rules
"""
import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ARTICLE = """Apple's AI-powered revamp of Siri will finally launch later this year, and the Cupertino giant has officially chosen Google's Gemini to power it. "Apple and Google have entered into a multi-year collaboration under which the next generation of Apple Foundation Models will be based on Google's Gemini models and cloud technology," Google and Apple shared in a joint statement on Monday.

Although Google is providing the technology, Apple's AI features will continue to run on Private Cloud Compute, Apple's own secure cloud-based system. Bloomberg first reported in September of last year that Apple was looking to pay Google around $1 billion annually for a custom Gemini model.

When the news hit the markets, Google became the fourth company to breach the $4 trillion market value benchmark. Google is proving itself to be a force to be reckoned with in the AI field.

Meanwhile, Apple hasn't been hitting the same highs in artificial intelligence. The AI Siri was supposed to arrive in early 2025, but Apple had to push the reveal back, disappointing fans and leading to an executive shakeup."""

# Simple prompt - just translate
SIMPLE_PROMPT = f"""Translate this English news article to Thai:

{ARTICLE}"""

def test_model(model_name, prompt):
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print('='*60)
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 2000
                }
            },
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("response", "No response")
            print(output)
            
            # Save to file
            filename = f"simple_translate_{model_name.replace('/', '_').replace(':', '_')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"\n[Saved to {filename}]")
            
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

# Test both models with simple prompt
test_model("translategemma:4b", SIMPLE_PROMPT)
test_model("scb10x/typhoon2.5-qwen3-4b", SIMPLE_PROMPT)
