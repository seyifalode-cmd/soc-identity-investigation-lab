"""Standard-library regression checks for the portfolio lab."""
import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
with contextlib.redirect_stdout(io.StringIO()):
    SOURCE = runpy.run_path(str(ROOT / 'code/cell-01.py'))
detect, event, pattern = (SOURCE[k] for k in ('detect', 'event', 'pattern'))


class DetectorRegression(unittest.TestCase):
    def test_out_of_order_arrival(self):
        self.assertEqual(detect(list(reversed(pattern))), detect(pattern))

    def test_different_users_do_not_combine(self):
        self.assertEqual(detect(pattern[:3] + [event('other', 180, 'Success', user='maya')]), [])

    def test_different_applications_do_not_combine(self):
        success = dict(pattern[-1], app='OtherPortal')
        self.assertEqual(detect(pattern[:3] + [success]), [])

    def test_one_second_outside_window(self):
        self.assertEqual(detect(pattern[:3] + [event('late', 301, 'Success')]), [])

    def test_duplicate_success_is_one_candidate(self):
        self.assertEqual(len(detect(pattern + [pattern[-1]])), 1)

    def test_evidence_ids_are_traceable(self):
        self.assertEqual(detect(pattern)[0]['evidence_ids'], ['f1', 'f2', 'f3', 's1'])

    def test_distinct_successes_each_match(self):
        matches = detect(pattern + [event('s2', 240, 'Success')])
        self.assertEqual([a['alert_id'] for a in matches], ['rule1:s1', 'rule1:s2'])

    def test_conflicting_ids_document_last_record_wins(self):
        # A known teaching limitation, not a recommended integrity policy.
        conflict = dict(pattern[0], result='Success')
        self.assertEqual(detect(pattern + [conflict]), [])
        self.assertEqual(len(detect([conflict] + pattern)), 1)


class RepositoryChecks(unittest.TestCase):
    def test_notebook_matches_cells(self):
        nb = json.loads((ROOT / 'notebooks/Project1-Walkthrough.ipynb').read_text())
        cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
        self.assertEqual(len(cells), 6)
        for i, cell in enumerate(cells, 1):
            self.assertEqual(''.join(cell['source']), (ROOT / f'code/cell-{i:02d}.py').read_text())
            self.assertEqual(cell['outputs'], [])
            self.assertIsNone(cell['execution_count'])

    def test_source_pdf_integrity(self):
        manifest = json.loads((ROOT / 'evidence/source-manifest.json').read_text())
        for filename, expected in manifest.items():
            data = (ROOT / 'docs' / filename).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected['sha256'])
            self.assertEqual(len(data), expected['bytes'])

    def test_fixture_counts(self):
        for filename, count in [('login-events.csv', 6), ('application-events.csv', 3)]:
            with (ROOT / 'data' / filename).open(newline='') as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), count)

    def test_local_markdown_targets(self):
        for path in ROOT.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                self.assertTrue((path.parent / target.split('#')[0]).exists(), (path, target))

    def test_full_lab_and_optimized_mode_guard(self):
        runner = ROOT / 'code/run_lab.py'
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(runner), directory],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('10 checks passed.', result.stdout)
            self.assertIn('RECOVERY PASS:', result.stdout)
            alerts = [json.loads(line) for line in (Path(directory) / 'project1_alerts.jsonl').read_text().splitlines()]
            self.assertEqual(len(alerts), 1)
            self.assertEqual(alerts[0]['evidence_ids'], ['f1', 'f2', 'f3', 's1'])
            audit = json.loads((Path(directory) / 'project1_response_audit.json').read_text())
            self.assertEqual([(row['action'], row['result']) for row in audit], [
                ('login', 'success'), ('view-order', 'success'),
                ('admin-revoke-sessions', 'completed'), ('admin-disable-account', 'completed'),
                ('view-order', 'rejected-session'), ('login', 'blocked-disabled'),
                ('admin-reset-and-enable', 'completed'), ('login', 'bad-credentials'),
                ('view-order', 'rejected-session'), ('login', 'success'), ('view-order', 'success'),
            ])
            optimized = subprocess.run([sys.executable, '-O', str(runner), directory],
                                       capture_output=True, text=True, timeout=10)
            self.assertNotEqual(optimized.returncode, 0)
            self.assertIn('Run without -O', optimized.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
