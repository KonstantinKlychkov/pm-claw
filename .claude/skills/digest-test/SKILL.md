---
name: digest-test
description: Tests the digest skill with real RSS feeds for manual verification.
allowed-tools: Bash(python:*)
disable-model-invocation: true
---
Run a quick manual test of DigestSkill with these sample feeds:
- https://news.ycombinator.com/rss
- https://feeds.bbci.co.uk/news/technology/rss.xml

Steps:
1. Create a temporary test script that imports DigestSkill
2. Initialize it with the URLs above
3. Call validate_urls() and print results
4. Call generate_digest() and print first 500 characters
5. Clean up the temporary script
6. Report whether the skill works correctly with real data
