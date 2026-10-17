"""Static Git-object reader tests; no scientific project module is imported."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('shared_pinned_reader', HERE/'pinned.py')
pinned = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pinned)  # Only the reader under test, never project modules.


class PinnedReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='.reader_test_', dir=HERE)
        cls.repo = Path(cls.temp.name)
        cls.git('init', '-q')
        cls.raw = b"raise RuntimeError('THIS SOURCE MUST NEVER EXECUTE')\n"
        (cls.repo/'sample.py').write_bytes(cls.raw)
        cls.git('add', 'sample.py')
        # This is an isolated disposable test repository, not the research Git index.
        cls.git('-c', 'user.name=Static test', '-c', 'user.email=static@example.invalid',
                '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Reader fixture')
        cls.pin = {'commit': cls.git('rev-parse', 'HEAD').decode().strip(), 'path': 'sample.py',
                   'blob_oid': cls.git('rev-parse', 'HEAD:sample.py').decode().strip(),
                   'sha256': hashlib.sha256(cls.raw).hexdigest()}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @classmethod
    def git(cls, *args):
        return subprocess.check_output(['git', '-C', str(cls.repo), *args], stderr=subprocess.STDOUT)

    def test_reads_commit_bytes_without_execution(self):
        self.assertEqual(pinned.read_blob(self.repo, self.pin), self.raw)

    def test_rejects_branch_name(self):
        with self.assertRaises(ValueError):
            pinned.read_blob(self.repo, {**self.pin, 'commit': 'main'})

    def test_rejects_wrong_blob(self):
        with self.assertRaises(ValueError):
            pinned.read_blob(self.repo, {**self.pin, 'blob_oid': '0'*40})

    def test_rejects_wrong_sha(self):
        with self.assertRaises(ValueError):
            pinned.read_blob(self.repo, {**self.pin, 'sha256': '0'*64})

    def test_rejects_wrong_or_noncanonical_path(self):
        for path in ('missing.py', '../sample.py', '/sample.py', './sample.py', 'x/../sample.py'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                pinned.read_blob(self.repo, {**self.pin, 'path': path})

    def test_worktree_and_index_changes_do_not_change_pinned_bytes(self):
        (self.repo/'sample.py').write_text('uncommitted different contents\n')
        self.git('add', 'sample.py')
        (self.repo/'sample.py').write_text('second unstaged change\n')
        self.assertEqual(pinned.read_blob(self.repo, self.pin), self.raw)
        self.assertNotEqual((self.repo/'sample.py').read_bytes(), self.raw)

    def test_actual_twelve_module_ast_closure_without_imports(self):
        manifest = json.loads((HERE/'manifest.json').read_bytes())
        before = set(sys.modules)
        audit = pinned.audit_manifest(HERE.parent, manifest)
        self.assertEqual(set(audit['modules']), pinned.MODULES)
        self.assertTrue(all(row['ast'] == 'PASS' for row in audit['modules'].values()))
        self.assertFalse(pinned.MODULES & (set(sys.modules)-before))


if __name__ == '__main__':
    unittest.main(verbosity=2)
