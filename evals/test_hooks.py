from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("guard", ROOT / ".codex/hook_guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
class HookTests(unittest.TestCase):
    def test_protected_patch_denied(self):
        for name in ['paper/figures/convergence.pdf', 'paper/generated/table.tex', 'AGENTS.md', '.codex/hooks.json', '../outside.tex']:
            result = guard.handle({'hook_event_name':'PreToolUse', 'tool_name':'apply_patch', 'tool_input':{'command':'*** Update File: '+name}})
            self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')
    def test_source_patch_allowed(self):
        self.assertIsNone(guard.handle({'hook_event_name':'PreToolUse', 'tool_name':'apply_patch', 'tool_input':{'command':'*** Update File: paper/sections/convergence.tex'}}))
    def test_stop_failure_and_loop_guard(self):
        with patch.object(guard, 'run_check', return_value=(1, 'repair required')):
            self.assertEqual(guard.handle({'hook_event_name':'Stop'})['decision'], 'block')
            self.assertIn('systemMessage', guard.handle({'hook_event_name':'Stop', 'stop_hook_active':True}))
    def test_healthy_stop(self):
        with patch.object(guard, 'run_check', return_value=(0, 'PASS')):
            self.assertIsNone(guard.handle({'hook_event_name':'Stop'}))
    def test_post_edit_feedback(self):
        with patch.object(guard, 'run_check', return_value=(1, 'undefined-reference')):
            result = guard.handle({'hook_event_name':'PostToolUse','tool_name':'apply_patch','tool_input':{'command':'*** Update File: paper/main.tex'}})
            self.assertIn('undefined-reference', result['hookSpecificOutput']['additionalContext'])
    def test_stdin_contract(self):
        p = subprocess.run([sys.executable, str(ROOT/'.codex/hook_guard.py')], input=json.dumps({'hook_event_name':'PreToolUse','tool_name':'apply_patch','tool_input':{'command':'*** Update File: paper/figures/convergence.pdf'}}), text=True, capture_output=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout)['hookSpecificOutput']['permissionDecision'], 'deny')
if __name__ == '__main__': unittest.main()
