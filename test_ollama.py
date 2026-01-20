"""Quick test to verify new Ollama engine works correctly."""
from app.services.ai_engine import InferenceController

c = InferenceController()
c.load_model()

print("=" * 60)
print("OLLAMA ENGINE VERIFICATION TEST")
print("=" * 60)

# Test 3 articles
for aid in [1, 5, 10]:
    try:
        result = c.score_article(article_id=aid)
        print(f"\nArticle {aid}:")
        print(f"  Scores: {result['scores']}")
        print(f"  Time: {round(result['elapsed_seconds'], 2)}s")
        print(f"  Raw response preview: {result['raw_response'][:80]}...")
    except Exception as e:
        print(f"\nArticle {aid}: ERROR - {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
