import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from report_pipeline import prepare, assemble, render, check
spec = importlib.util.spec_from_file_location('collect_context', ROOT / 'scripts/collect-context.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.analysis = {'schema_version':'2.0','overview':{'summary':'Summary','intent':{'stated_intent':'Intent','implemented_changes':'Changes','verdict':'matches','explanation':'Evidence'}},'findings':[{'severity':'HIGH','status':'new','title':'Bug','locations':[{'file':'a.py','start_line':1,'end_line':1,'side':'RIGHT'}],'reason':'Reason','impact':'Impact','evidence':'Evidence'}]}
        self.comments = {'schema_version':'2.0','comments':[{'finding_id':'F-001','comment':'Please fix </script><script>alert(1)</script>'}]}
        self.context = {'schema_version':'2.0','review':{'mode':'local','repository':'test','base_sha':'a'*40,'head_sha':'b'*40},'changes':[{'path':'a.py','status':'modified','additions':1,'deletions':1,'patch':'@@ -1 +1 @@\n-old\n+new\n'}],'sources':{'a.py':{'LEFT':'old\n','RIGHT':'new\n'}}}

    def test_build_is_deterministic_and_safe(self):
        data = assemble(self.context, prepare(self.analysis), self.comments)
        html = render(data)
        self.assertEqual(html, render(data))
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertEqual(data['summary']['high'], 1)
        self.assertEqual(data['findings'][0]['locations'][0]['code_excerpt'], 'new')

    def test_command_pipeline_and_canonical_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name, data in [('analysis', self.analysis), ('context', self.context), ('comments', self.comments)]:
                (root / (name + '.json')).write_text(json.dumps(data))
            subprocess.run([sys.executable, str(ROOT / 'scripts/build-report.py'), 'prepare', '--analysis', str(root / 'analysis.json'), '--output', str(root / 'accepted.json')], check=True)
            subprocess.run([sys.executable, str(ROOT / 'scripts/build-report.py'), 'build', '--analysis', str(root / 'accepted.json'), '--context', str(root / 'context.json'), '--comments', str(root / 'comments.json'), '--output', str(root / 'report.html')], check=True)
            command = ['bash', str(ROOT / 'scripts/validate-report.sh'), str(root / 'report.html')]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            report = root / 'report.html'
            report.write_text(report.read_text() + '<div>Agent customization</div>')
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_translation_cannot_change_review_judgment(self):
        self.comments['comments'][0]['severity'] = 'LOW'
        with self.assertRaisesRegex(ValueError, 'unexpected field'):
            assemble(self.context, prepare(self.analysis), self.comments)

    def test_unknown_comment_id_and_source_ranges_fail(self):
        self.comments['comments'][0]['finding_id'] = 'F-999'
        with self.assertRaisesRegex(ValueError, 'unknown or duplicate'):
            assemble(self.context, prepare(self.analysis), self.comments)
        self.comments['comments'][0]['finding_id'] = 'F-001'
        self.analysis['findings'][0]['locations'][0]['end_line'] = 99
        with self.assertRaisesRegex(ValueError, 'outside'):
            assemble(self.context, prepare(self.analysis), self.comments)

    def test_collect_local_and_committed_snapshots(self):
        with tempfile.TemporaryDirectory() as temp:
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=temp, text=True).strip()
            git('init', '-q'); git('config','user.email','test@example.com'); git('config','user.name','Test')
            path = Path(temp) / 'a.py'; path.write_text('old\n')
            git('add','.'); git('commit','-qm','base'); base = git('rev-parse','HEAD')
            path.write_text('new\n'); git('add','.'); git('commit','-qm','head')
            (Path(temp)/'staged.txt').write_text('staged'); git('add','staged.txt')
            path.write_text('worktree\n'); (Path(temp)/'untracked.txt').write_text('extra\n')
            committed = collector.collect(temp,'commit_range',base,'HEAD')
            local = collector.collect(temp,'local',base,'HEAD')
            self.assertEqual(committed['sources']['a.py']['RIGHT'],'new\n')
            self.assertEqual(local['sources']['a.py']['RIGHT'],'worktree\n')
            self.assertEqual(len(local['changes']),3)
            self.assertEqual(local['sources']['staged.txt']['RIGHT'], 'staged')


if __name__ == '__main__': unittest.main()
