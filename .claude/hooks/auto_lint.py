"""PostToolUse hook: auto-lint Python files after Write/Edit."""
import json
import subprocess
import sys


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    # Get the file path from tool input
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path") or tool_input.get("path", "")

    # Only process Python files
    if not file_path.endswith(".py"):
        sys.exit(0)

    # Run ruff check (lint only, don't fix)
    result = subprocess.run(
        ["ruff", "check", file_path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Output lint issues as feedback for Claude
        output = {
            "userMessage": f"Lint issues in {file_path}:\n{result.stdout}"
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
