"""Read-only guardrails. No Codex recursion and no project-file mutation."""
from pathlib import Path
import json
import re
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
PROTECTED = {"AGENTS.md", "CLAUDE.md", "LICENSE"}

def guarded(path):
    p = Path(path)
    if p.is_absolute():
        try: p = p.relative_to(ROOT)
        except ValueError: return True
    name = p.as_posix()
    return (".." in p.parts or name in PROTECTED or
            name.startswith((".git/", ".codex/", ".agents/", ".github/", "paper/generated/", "paper/figures/", "build/")) or
            p.suffix in {".aux", ".log", ".bbl", ".blg", ".out", ".toc", ".pdf"})

def run_check(*args):
    try:
        p = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, timeout=20)
        return p.returncode, (p.stdout + p.stderr)[-7000:]
    except subprocess.TimeoutExpired:
        return 1, "Health check timed out; run checks manually and inspect the failure."

def handle(event):
    kind = event.get("hook_event_name")
    tool = event.get("tool_name", "")
    inp = event.get("tool_input", {})
    command = inp.get("command", "") if isinstance(inp, dict) else str(inp)
    if kind == "PreToolUse":
        if tool in {"apply_patch", "Edit", "Write"}:
            paths = re.findall(r"^\*\*\* (?:Update File|Add File|Delete File|Move to): (.+)$", command, re.M)
            if isinstance(inp, dict) and inp.get("file_path"): paths.append(inp["file_path"])
            bad = [p for p in paths if guarded(p)]
            if bad:
                return {"hookSpecificOutput": {"hookEventName": kind, "permissionDecision": "deny", "permissionDecisionReason": "Protected/generated edit: " + ", ".join(bad) + ". Edit sources and regenerate. For authorized policy maintenance, review and disable this hook via /hooks."}}
        # Shell is not parsed as a language: flag obvious risky paths, do not pretend to sandbox it.
        elif tool == "Bash" and re.search(r"paper/(?:figures|generated)/|\.codex/|\.git/|AGENTS\.md|LICENSE", command):
            return {"hookSpecificOutput": {"hookEventName": kind, "additionalContext": "This command mentions protected/generated files. Read-only inspection and the source generator are allowed; do not hand-edit outputs or policy files."}}
    elif kind == "PostToolUse":
        if tool not in {"apply_patch", "Edit", "Write"} or not re.search(r"paper/.*\.(?:tex|bib)", command): return None
        code, reason = run_check(str(ROOT / "scripts/project_health.py"), "--strict", "--no-build")
        if code:
            return {"hookSpecificOutput": {"hookEventName": kind, "additionalContext": "LaTeX validation failed. Repair these findings before completion:\n" + reason}}
    elif kind == "Stop":
        code, reason = run_check(str(ROOT / "scripts/project_health.py"), "--strict", "--no-build")
        buildcode, buildreason = run_check(str(ROOT / "scripts/build_evidence.py"), "check")
        if code or buildcode:
            message = "Run the experiment if needed, repair health findings, then build the complete paper.\n" + reason + buildreason
            if event.get("stop_hook_active"):
                # One continuation per failed stop, preventing endless loops when a tool is unavailable.
                return {"systemMessage": "Verification still incomplete; report it honestly.\n" + message}
            return {"decision": "block", "reason": message}
    return None

def main():
    try:
        result = handle(json.load(sys.stdin))
    except (ValueError, OSError, TypeError) as e:
        print("Invalid hook input: " + str(e), file=sys.stderr)
        return 1
    if result: print(json.dumps(result))
    return 0
if __name__ == "__main__": raise SystemExit(main())
