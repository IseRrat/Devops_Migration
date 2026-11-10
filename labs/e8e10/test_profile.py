import json, tempfile, unittest
from pathlib import Path
from lab import fixture,scan,patch,commit

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_independent_known_edges(self):
        r=scan(self.p)
        self.assertEqual(r['actual']['main.o'],['config.h','main.c'])
        self.assertEqual({(f['type'],f['dependency']) for f in r['findings']},{('MISSING','config.h'),('REDUNDANT','unused.h')})

    def test_unchanged_reuses_both_targets(self):
        r=scan(self.p,scan(self.p));self.assertEqual(r['reused'],['main.o','helper.o']);self.assertEqual(r['refreshed'],[])

    def test_include_added_invalidates_cache(self):
        old=scan(self.p)
        (self.p/'main.c').write_text('#include "extra.h"\n'+(self.p/'main.c').read_text());commit(self.p,'new include')
        r=scan(self.p,old)
        self.assertIn(['MISSING','main.o','extra.h'],r['added']);self.assertEqual(len(r['refreshed']),2)

    def test_patch_preserves_redundant_dependency(self):
        r=scan(self.p);diff,plan=patch(self.p,r)
        self.assertIn('+main.o: main.c unused.h config.h',diff)
        self.assertNotIn('-\tgcc',diff)
        self.assertNotIn('config.h',(self.p/'Makefile').read_text())

    def test_old_report_rejected(self):
        r=scan(self.p);r['commit']='0'*40
        with self.assertRaisesRegex(ValueError,'STALE_REPORT'):patch(self.p,r)

    def test_unsafe_dependency_rejected(self):
        r=scan(self.p);r['findings']=[{'type':'MISSING','target':'main.o','dependency':'../outside.h'}]
        with self.assertRaisesRegex(ValueError,'UNSAFE_PATH'):patch(self.p,r)

    def test_unsupported_configuration_rejected(self):
        (self.p/'Makefile').write_text((self.p/'Makefile').read_text().replace('-O0','-include unknown.h'))
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_FLAGS'):scan(self.p)

class StudentLeaderE9Mixed(unittest.TestCase):
    def test_mixed_patch_keeps_macro_and_recipes_and_resolves_md(self):
        from lab import run

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'sample'
            fixture(project, 'mixed')

            makefile = project / 'Makefile'
            original = makefile.read_bytes()
            before_recipes = [
                line for line in original.splitlines(keepends=True)
                if line.startswith(b'\t')
            ]
            report = scan(project)
            self.assertIn(
                {'type': 'MISSING', 'target': 'main.o', 'dependency': 'config.h'},
                report['findings'],
            )

            diff, plan = patch(project, report)
            self.assertEqual(
                plan,
                [{'target': 'main.o', 'dependency': 'config.h', 'style': 'mixed'}],
            )
            self.assertEqual(makefile.read_bytes(), original)

            candidate = root / 'mixed-candidate.patch'
            candidate.write_text(diff)
            run(['git', 'apply', '--check', str(candidate.resolve())], project)
            run(['git', 'apply', str(candidate.resolve())], project)

            after = makefile.read_bytes()
            self.assertIn(b'HEADERS = unused.h\n', after)
            self.assertIn(b'main.o: main.c $(HEADERS) config.h\n', after)
            after_recipes = [
                line for line in after.splitlines(keepends=True)
                if line.startswith(b'\t')
            ]
            self.assertEqual(after_recipes, before_recipes)
            repaired = scan(project)
            self.assertFalse(any(f['type'] == 'MISSING' for f in repaired['findings']))
            run(['make', 'app'], project)
            self.assertEqual(run(['./app'], project).strip(), '1')


if __name__=='__main__':unittest.main()
