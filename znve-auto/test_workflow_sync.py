"""2.5 schema consistency and migration. Runtime behavior lives in node:test."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import builder

ROOT = builder.REPO_ROOT

class WorkflowSyncTests(unittest.TestCase):
    def test_schemas_have_one_source(self):
        spec = builder.load_spec()
        for name, schema in spec['workflow']['schemas'].items():
            actual = json.loads((ROOT / 'schemas' / (name + '.schema.json')).read_text(encoding='utf-8'))
            actual.pop('$schema')
            self.assertEqual(actual, schema)
        self.assertCountEqual(spec['workflow']['operations'], spec['workflow']['schemas']['workflow']['$defs'])

    def test_python_engine_is_retired_explicitly(self):
        for name in ('znve_skill.py','Auto_Installer.py','install_znve_global.py','agent.py'):
            result = subprocess.run([sys.executable, str(ROOT / 'integrations' / 'antigravity' / name)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('ZNVE_MIGRATION_REQUIRED', result.stderr)
        self.assertNotIn('znve_skill.py', json.dumps(builder.load_spec()['regions']))

    def test_shared_engine_and_no_grok_folder(self):
        self.assertFalse((ROOT / 'integrations' / 'grok').exists())
        self.assertFalse(any('grok' in t['output'] for t in builder.load_spec()['targets']))
        self.assertIn('Grok', (ROOT / 'integrations' / 'README.md').read_text(encoding='utf-8'))
        self.assertTrue((ROOT / '.github' / 'copilot-instructions.md').is_file())

    def test_legacy_contract_cases_retained(self):
        cases = json.loads((ROOT / 'znve-auto' / 'tool_contract_cases.json').read_text(encoding='utf-8'))
        self.assertEqual(len(cases['cases']), 63)

    def test_ollama_extension_is_inside_system(self):
        text = builder.render_targets(builder.load_spec())['integrations/ollama/Modelfile']
        self.assertEqual(text.count('"""'), 2)
        self.assertLess(text.index('## Spec-Driven Agent Engineering'), text.rfind('"""'))
        self.assertEqual(text[text.rfind('"""') + 3:].strip(), '')

    def test_server_version_and_openrouter_evidence_boundary(self):
        spec = builder.load_spec()
        pkg = json.loads((ROOT / 'integrations' / 'mcp-server' / 'package.json').read_text(encoding='utf-8'))
        self.assertEqual(pkg['version'], spec['mcp']['contract']['server_version'])
        envelope = json.loads((ROOT / 'integrations' / 'openrouter' / 'response-schema.json').read_text(encoding='utf-8'))['json_schema']['schema']
        self.assertIn('verification_report', envelope['required'])
        self.assertIn('No constituye evidencia', envelope['properties']['verification_report']['description'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
