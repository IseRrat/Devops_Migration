import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pipeline
import server

class Contracts(unittest.TestCase):
    def report(self):return {'schema_version':'e11e12-1','kind':'incremental-check','commit':'a'*40,'status':'SUCCEEDED'}
    def test_accept_current_report(self):pipeline.check_envelope(self.report(),'a'*40,'incremental-check')
    def test_reject_old_commit(self):
        with self.assertRaisesRegex(pipeline.Failure,'another commit'):pipeline.check_envelope(self.report(),'b'*40)
    def test_reject_schema(self):
        r=self.report();r['schema_version']='old'
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(r,'a'*40)
    def test_reject_failed_upstream(self):
        r=self.report();r['status']='FAILED'
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(r,'a'*40)
    def test_reject_wrong_artifact_kind(self):
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(self.report(),'a'*40,'fixed-md')
    def test_artifact_uses_relative_uri_and_content_hash(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'x.json';p.write_text('{}')
            a=pipeline.artifact(p,root,'job-1');self.assertEqual(a['uri'],'artifact://job-1/x.json');self.assertEqual(len(a['sha256']),64)
    def test_existing_evidence_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'keep').write_text('keep')
            with self.assertRaises(pipeline.Failure):pipeline.execute({},root)
            self.assertEqual((root/'keep').read_text(),'keep')
    def test_changed_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'r.json';p.write_text('{}')
            with self.assertRaises(pipeline.Failure):pipeline.load_artifact(p,'0'*64)
    def test_same_key_same_request_same_job(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);store=server.Store(root/'jobs')
            request={'mode':'e11-a','repo':str(pipeline.ROOT/'data/p'),'base':'a','target':'b'}
            with patch.object(store.pool,'submit'):
                one=store.submit(request,'same');two=store.submit(request,'same')
                self.assertEqual(one['job_id'],two['job_id'])
                changed=dict(request,target='c')
                with self.assertRaisesRegex(ValueError,'IDEMPOTENCY_CONFLICT'):store.submit(changed,'same')
            store.pool.shutdown()
    def test_api_rejects_repo_outside_data(self):
        with tempfile.TemporaryDirectory() as d:
            store=server.Store(Path(d)/'jobs')
            with self.assertRaises(ValueError):store.submit({'mode':'e11-a','repo':str(Path(d)),'base':'a','target':'b'},'k')
            store.pool.shutdown()

class StudentB241880446(unittest.TestCase):
    def test_macro_two_missing_headers_preserves_reference_and_source(self):
        from lab import fixture, scan, patch as make_patch, run
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'sample'
            fixture(project, 'macro')
            source = project / 'main.c'
            source.write_text('#include "extra.h"\n' + source.read_text())
            from lab import commit
            commit(project, 'E11 B: macro input with two missing headers')
            report = scan(project)
            self.assertEqual({f['dependency'] for f in report['findings']
                              if f['type'] == 'MISSING'}, {'config.h', 'extra.h'})
            before = (project / 'Makefile').read_bytes()
            diff, plan = make_patch(project, report)
            self.assertEqual((project / 'Makefile').read_bytes(), before)
            self.assertEqual(len(plan), 2)
            self.assertTrue(all(edit['style'] == 'macro' for edit in plan))
            candidate = root / 'candidate.patch'
            candidate.write_text(diff)
            run(['git', 'apply', '--check', str(candidate)], project)
            run(['git', 'apply', str(candidate)], project)
            text = (project / 'Makefile').read_text()
            self.assertIn('DEPS = main.c unused.h config.h extra.h', text)
            self.assertIn('main.o: $(DEPS)', text)
            self.assertFalse(any(f['type'] == 'MISSING'
                                 for f in scan(project)['findings']))

    def test_real_artifact_hash_then_stale_commit_and_tampering_rejected(self):
        import hashlib
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            original = b'{"schema_version":"e11e12-1","kind":"fixed-md","commit":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","status":"SUCCEEDED"}\n'
            path.write_bytes(original)
            expected = hashlib.sha256(original).hexdigest()
            report = pipeline.load_artifact(path, expected)
            pipeline.check_envelope(report, 'a' * 40, 'fixed-md')
            with self.assertRaises(pipeline.Failure) as stale:
                pipeline.check_envelope(report, 'b' * 40, 'fixed-md')
            self.assertEqual(stale.exception.code, 'STALE_REPORT')
            path.write_bytes(original.replace(b'SUCCEEDED', b'FAILED'))
            with self.assertRaises(pipeline.Failure) as changed:
                pipeline.load_artifact(path, expected)
            self.assertEqual(changed.exception.code, 'ARTIFACT_HASH_MISMATCH')


class StudentRestart241880446(unittest.TestCase):
    def test_restart_marks_unfinished_job_but_preserves_completed_job(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for suffix, status in [('pending', 'RUNNING'), ('done', 'SUCCEEDED')]:
                pipeline.save(root / ('job-' + suffix) / 'state.json', {
                    'job_id': 'job-' + suffix, 'status': status,
                    'idempotency_key': suffix, 'request_hash': suffix})
            store = server.Store(root)
            self.addCleanup(store.pool.shutdown)
            self.assertEqual(store.jobs['job-pending']['status'], 'FAILED')
            self.assertEqual(store.jobs['job-pending']['error']['code'],
                             'SERVER_RESTARTED')
            self.assertEqual(store.jobs['job-done']['status'], 'SUCCEEDED')
            self.assertNotIn('error', store.jobs['job-done'])


if __name__=='__main__':unittest.main()
