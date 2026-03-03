---
name: python-best-practices
description: Python coding standards and performance optimization
---

# Python Best Practices Skill

## Code Quality

### 1. Type Hints
```python
def process_article(article_id: int, content: str) -> Dict[str, Any]:
    """Process an article and return results."""
    ...
```

### 2. Docstrings
```python
def translate_article(self, article_id: int) -> Dict:
    """
    Translate article to Thai.
    
    Args:
        article_id: The database ID of the article
        
    Returns:
        Dict with keys: headline, lead, body, success
        
    Raises:
        InferenceError: If model not loaded
    """
```

### 3. Error Handling
```python
# Good: Specific exceptions
try:
    result = api.call()
except requests.Timeout:
    logger.warning("API timeout")
except requests.ConnectionError:
    logger.error("Cannot connect to API")

# Bad: Bare except
try:
    result = api.call()
except:  # Never do this
    pass
```

## Performance Optimization

### 1. Database Queries
- Use `LIMIT` and `OFFSET` for pagination
- Create indexes on frequently queried columns
- Use `COALESCE()` for nullable columns
- Batch inserts instead of individual inserts

### 2. Threading
- Use `threading.Thread(daemon=True)` for background tasks
- For Flet: Use `page.run_task()` with `asyncio.to_thread()`
- Avoid shared state between threads

### 3. Memory
- Use generators for large data: `yield` instead of `return list`
- Close database connections in `finally` blocks
- Use context managers (`with` statements)

### 4. String Operations
```python
# Good: Join for multiple strings
result = "".join([s1, s2, s3])

# Bad: Repeated concatenation
result = s1 + s2 + s3  # Creates intermediate objects
```

## Anti-Patterns to Avoid

1. **Never use mutable default arguments**
   ```python
   # Bad
   def func(items=[]):
       items.append(1)
   
   # Good
   def func(items=None):
       items = items or []
   ```

2. **Never suppress all exceptions**
   ```python
   # Bad
   except Exception:
       pass
   
   # Good
   except SpecificError as e:
       logger.error(f"Error: {e}")
   ```

3. **Avoid global state** - Use class attributes or dependency injection
