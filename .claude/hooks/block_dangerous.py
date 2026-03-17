"""PreToolUse hook: block dangerous bash commands."""
import json
import re
import sys

DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+\*",
    r":(){ :\|:& };:",       # fork bomb
    r"mkfs\.",                # format disk
    r"dd\s+if=.*of=/dev/",   # disk overwrite
    r"> /dev/sda",
]


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command):
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked dangerous command matching: {pattern}"
                }
            }
            print(json.dumps(output))
            sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
