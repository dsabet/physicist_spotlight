import copy
import csv
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import spotlight as s


class SpotlightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'data/archive').mkdir(parents=True)
        self.output = self.root / 'data/current.csv'
        (self.root / 'spotlight.json').write_text(json.dumps({'output': 'data/current.csv', 'aliases': {}}))
        self.output.write_bytes(b'Newsletter Date,Scientist,Description,Picture\r\n9/8/26,Dr. Existing Person,Existing description,')
        self.bundle = {
            'row': dict(zip(s.FIELDS, ['9/15/26', 'New Scientist', 'A result, with "quotes".\nAnother sentence.', ''])),
            'claims': [
                {'id': 'p', 'kind': 'physics', 'text': 'Contribution', 'sources': [{'url': 'https://university.example/bio', 'evidence': 'Evidence'}]},
                {'id': 'b', 'kind': 'biography', 'text': 'Life', 'sources': [{'url': 'https://museum.example/bio', 'evidence': 'Evidence'}]},
            ],
        }
        self.sign()

    def sign(self):
        self.bundle['fact_check'] = {'verdict': 'PASS', 'reviewer': 'fact_checker', 'notes': 'Checked', 'claims_sha256': s.digest(self.bundle['claims'])}
        self.bundle['draft_check'] = dict(self.bundle['fact_check'], row_sha256=s.digest(self.bundle['row']), supported_claim_ids=['p', 'b'])

    def test_append_preserves_bytes_and_quotes(self):
        original = self.output.read_bytes()
        before = s.snapshot(self.root)
        s.append(self.root, self.bundle, before, '2026-09-15')
        self.assertTrue(self.output.read_bytes().startswith(original))
        self.assertEqual(s.read_csv(self.output)[1][-1], self.bundle['row'])
        s.audit(self.root, before)
        with self.assertRaises(ValueError):
            s.append(self.root, self.bundle, before, '2026-09-15')
        with self.assertRaises(ValueError):
            s.append(self.root, self.bundle, s.snapshot(self.root), '2026-09-15')

    def test_legacy_header_and_blank_record(self):
        path = self.root / 'data/archive/legacy.csv'
        path.write_text(',,,\nName,Date in Newsletter,Description,Column 1\nDr Legacy Researcher,2/4/25,Work,\n')
        self.assertIn('legacy researcher', s.inventory(self.root))
        with self.assertRaisesRegex(ValueError, 'already used'):
            s.check_name(self.root, 'Legacy Researcher')

    def test_alias_and_name_normalization(self):
        (self.root / 'spotlight.json').write_text(json.dumps({'output': 'data/current.csv', 'aliases': {'E. Person': 'Existing Person'}}))
        for name in [' existing   person ', 'DR. EXISTING PERSON', 'E. Person']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                s.check_name(self.root, name)

    def test_close_match_requires_review(self):
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            s.check_name(self.root, 'Existing Persons')

    def test_bad_date_and_wrong_requested_date(self):
        for date in ['2/30/26', '']:
            row = dict(self.bundle['row'], **{'Newsletter Date': date})
            with self.assertRaises(ValueError):
                s.validate_row(row)
        with self.assertRaisesRegex(ValueError, 'requested date'):
            s.validate_bundle(self.root, self.bundle, '2026-09-16')

    def test_failed_reviews_and_stale_content(self):
        for review in ['fact_check', 'draft_check']:
            for verdict in ['FAIL', 'NEEDS_MORE_EVIDENCE']:
                bundle = copy.deepcopy(self.bundle)
                bundle[review]['verdict'] = verdict
                with self.assertRaises(ValueError):
                    s.validate_bundle(self.root, bundle)
        bundle = copy.deepcopy(self.bundle)
        bundle['row']['Description'] += ' New unsupported fact.'
        with self.assertRaisesRegex(ValueError, 'Draft changed'):
            s.validate_bundle(self.root, bundle)
        bundle = copy.deepcopy(self.bundle)
        bundle['claims'][0]['text'] = 'Changed'
        with self.assertRaisesRegex(ValueError, 'Evidence changed'):
            s.validate_bundle(self.root, bundle)

    def test_missing_evidence(self):
        self.bundle['claims'][0]['sources'] = []
        self.sign()
        with self.assertRaises(ValueError):
            s.validate_bundle(self.root, self.bundle)

    def test_rejection_does_not_write(self):
        before = s.snapshot(self.root)
        original = self.output.read_bytes()
        self.bundle['draft_check']['verdict'] = 'FAIL'
        with self.assertRaises(ValueError):
            s.append(self.root, self.bundle, before, '2026-09-15')
        self.assertEqual(original, self.output.read_bytes())

    def test_changed_history_blocks_append(self):
        before = s.snapshot(self.root)
        original = self.output.read_bytes()
        (self.root / 'data/archive/new.csv').write_text('Newsletter Date,Scientist,Description,Picture\n')
        with self.assertRaisesRegex(ValueError, 'changed'):
            s.append(self.root, self.bundle, before, '2026-09-15')
        self.assertEqual(original, self.output.read_bytes())

    def test_unknown_schema_and_bad_width_fail(self):
        for raw in [b'wrong,header\n', b'Newsletter Date,Scientist,Description,Picture\n9/8/26,A,B\n']:
            with self.assertRaises(ValueError):
                s.read_csv(self.output, raw)

    def test_audit_rejects_original_edits(self):
        before = s.snapshot(self.root)
        s.append(self.root, self.bundle, before, '2026-09-15')
        self.output.write_bytes(self.output.read_bytes().replace(b'Existing description', b'Changed description'))
        with self.assertRaisesRegex(ValueError, 'original bytes'):
            s.audit(self.root, before)

    def test_bom_and_newlines(self):
        for newline in ['\n', '\r\n']:
            with self.subTest(newline=newline):
                self.output.write_bytes(b'\xef\xbb\xbf' + (','.join(s.FIELDS) + newline).encode())
                original = self.output.read_bytes()
                s.append(self.root, self.bundle, s.snapshot(self.root), '2026-09-15')
                self.assertTrue(self.output.read_bytes().startswith(original))
                self.assertEqual(s.read_csv(self.output)[1], [self.bundle['row']])

    def test_runner_checks_model_output_before_append(self):
        project = Path(__file__).resolve().parents[1]
        shutil.copytree(project / 'scripts', self.root / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(project / 'docs', self.root / 'docs')
        shutil.copy(project / 'AGENTS.md', self.root)
        (self.root / '.gitignore').write_text('__pycache__/\n.spotlight.lock\ndata/\nresearch/\n')
        # The fake model runs only in a disposable repository. No model/network calls.
        fake = self.root / 'codex'
        fake.write_text('#!/usr/bin/env python3\n' + '''import json,os,pathlib,re,sys
sys.path.insert(0, 'scripts')
import spotlight as s
run = pathlib.Path(re.search(r'Save the complete evidence bundle to (research/[^ ]+)/candidate.json', sys.argv[2]).group(1))
mode = os.environ['TEST_SPOTLIGHT_MODE']
bundle = json.loads(pathlib.Path('fixture.json').read_text())
if mode != 'missing':
    (run / 'candidate.json').write_text(json.dumps(bundle))
(run / 'report.md').write_text('Fixture research report')
if mode == 'changed':
    pathlib.Path('AGENTS.md').write_text('Unexpected model edit')
''')
        fake.chmod(0o755)
        (self.root / 'fixture.json').write_text(json.dumps(self.bundle))
        for command in [['git', 'init', '-q'], ['git', 'add', '.'],
                        ['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.org', 'commit', '-qm', 'Fixture']]:
            subprocess.run(command, cwd=self.root, check=True, capture_output=True)
        tracked_data = subprocess.run(['git', 'ls-files', 'data'], cwd=self.root, check=True, capture_output=True, text=True)
        self.assertEqual(tracked_data.stdout, '')
        env = dict(os.environ, PATH=str(self.root) + os.pathsep + os.environ['PATH'])
        original = self.output.read_bytes()
        for mode in ['missing', 'changed', 'success']:
            # Restore only disposable fixture files between simulated runs.
            shutil.rmtree(self.root / 'research', ignore_errors=True)
            subprocess.run(['git', 'restore', 'AGENTS.md'], cwd=self.root, check=True)
            env['TEST_SPOTLIGHT_MODE'] = mode
            result = subprocess.run(['bash', 'scripts/run_spotlight.sh', '2026-09-15'],
                                    cwd=self.root, env=env, capture_output=True, text=True)
            with self.subTest(mode=mode):
                if mode == 'success':
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(len(s.read_csv(self.output)[1]), 2)
                else:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(self.output.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
