---
paths:
  - "tests/**/*.py"
---
# Testing Rules
- Use pytest, never unittest
- File naming: test_<module>.py
- Use fixtures over setUp/tearDown
- Each test function: one assertion concept
- Use descriptive names: test_<what>_<condition>_<expected>
- Mock external services, never real API calls in tests
