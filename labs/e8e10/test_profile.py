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


class StudentE8B241880446(unittest.TestCase):
    """Adapt the E8 B recipe example, then test a real redundant-only report."""

    def test_redundant_only_preserves_extra_header_and_recipe_bytes(self):
        from lab import run
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'sample'
            fixture(project)
            makefile = project / 'Makefile'
            original = makefile.read_bytes()
            diff, plan = patch(project, scan(project))
            candidate = root / 'candidate.patch'
            candidate.write_text(diff)
            run(['git', 'apply', str(candidate.resolve())], project)
            recipes = lambda data: [
                line for line in data.splitlines() if line.startswith(b'\t')]
            self.assertEqual(recipes(original), recipes(makefile.read_bytes()))
            self.assertIn(b'main.o: main.c unused.h config.h', makefile.read_bytes())
            self.assertEqual(plan[0]['style'], 'direct')

            # Extra input beyond the handbook example: two redundant headers.
            makefile.write_text(makefile.read_text().replace(
                'main.o: main.c unused.h config.h',
                'main.o: main.c unused.h config.h extra.h'))
            commit(project, 'E8 B: redundant-only declaration fixture')
            report = scan(project)
            self.assertEqual(
                {(f['type'], f['target'], f['dependency'])
                 for f in report['findings']},
                {('REDUNDANT', 'main.o', 'unused.h'),
                 ('REDUNDANT', 'main.o', 'extra.h')})

            before = makefile.read_bytes()
            no_diff, no_edits = patch(project, report)
            self.assertEqual(no_diff, '')
            self.assertEqual(no_edits, [])
            self.assertEqual(makefile.read_bytes(), before)
            self.assertEqual(recipes(original), recipes(before))
            self.assertIn(b'unused.h config.h extra.h', before)


class StudentE9B241880446(unittest.TestCase):
    """Handbook macro example and the shared-variable impact extension."""

    def test_macro_style_patch_updates_definition(self):
        from lab import run
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'sample'
            fixture(p, 'macro')
            before = (p / 'Makefile').read_bytes()
            diff, plan = patch(p, scan(p))
            self.assertEqual((p / 'Makefile').read_bytes(), before)
            candidate = Path(directory) / 'candidate.patch'
            candidate.write_text(diff)
            run(['git', 'apply', str(candidate.resolve())], p)
            text = (p / 'Makefile').read_text()
            self.assertIn('DEPS = main.c unused.h config.h', text)
            self.assertIn('main.o: $(DEPS)', text)
            self.assertEqual(plan[0]['style'], 'macro')
            self.assertFalse(any(x['type'] == 'MISSING' for x in scan(p)['findings']))

    def test_shared_macro_also_changes_other_targets_dependencies(self):
        from lab import run
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'sample'
            fixture(p, 'macro')
            makefile = p / 'Makefile'
            makefile.write_text(makefile.read_text().replace(
                'helper.o: helper.c', 'helper.o: helper.c $(DEPS)'))
            commit(p, 'E9 B: two targets share DEPS')
            before = makefile.read_bytes()
            report = scan(p)
            self.assertEqual(report['declared']['helper.o'],
                             ['helper.c', 'main.c', 'unused.h'])
            diff, plan = patch(p, report)
            self.assertEqual(plan, [{'target': 'main.o',
                                    'dependency': 'config.h', 'style': 'macro'}])
            self.assertEqual(makefile.read_bytes(), before)
            candidate = Path(directory) / 'candidate.patch'
            candidate.write_text(diff)
            run(['git', 'apply', '--check', str(candidate.resolve())], p)
            run(['git', 'apply', str(candidate.resolve())], p)
            result = scan(p)
            self.assertEqual(result['declared']['helper.o'],
                             ['config.h', 'helper.c', 'main.c', 'unused.h'])
            self.assertEqual(result['actual']['helper.o'], ['helper.c'])
            self.assertIn({'type': 'REDUNDANT', 'target': 'helper.o',
                           'dependency': 'config.h'}, result['findings'])
            self.assertFalse(any(x['type'] == 'MISSING' for x in result['findings']))
            self.assertIn('helper.o: helper.c $(DEPS)', makefile.read_text())
            recipes = lambda data: [line for line in data.splitlines()
                                    if line.startswith(b'\t')]
            self.assertEqual(recipes(before), recipes(makefile.read_bytes()))


class StudentE10B241880446(unittest.TestCase):
    """Handbook build-failure example and a buildable incomplete patch."""

    def test_build_failure_keeps_original_makefile(self):
        from lab import validate
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / 'sample'
            fixture(p)
            diff, plan = patch(p, scan(p))
            candidate = root / 'candidate.patch'
            candidate.write_text(diff)
            before = (p / 'Makefile').read_bytes()
            (p / 'main.c').write_text('this is invalid C;\n')
            result = validate(p, candidate, root / 'validation')
            self.assertTrue(result['checks']['patch_applies'])
            self.assertFalse(result['checks'].get('build', False))
            self.assertIn('COMMAND_FAILED', result['error'])
            self.assertFalse(result['accepted'])
            self.assertTrue(result['rollback'])
            self.assertTrue(result['source_unchanged'])
            self.assertEqual((p / 'Makefile').read_bytes(), before)

    def test_buildable_patch_with_remaining_missing_edge_is_rejected(self):
        import difflib
        from lab import validate
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / 'sample'
            fixture(p)
            (p / 'helper.c').write_text(
                '#include "extra.h"\nint helper(void){return EXTRA;}\n')
            commit(p, 'E10 B: helper also uses extra.h')
            report = scan(p)
            self.assertEqual(
                {(f['target'], f['dependency']) for f in report['findings']
                 if f['type'] == 'MISSING'},
                {('main.o', 'config.h'), ('helper.o', 'extra.h')})
            makefile = p / 'Makefile'
            before = makefile.read_bytes()
            # Deliberately repair only main.o, leaving helper.o/extra.h missing.
            partial = before.decode().replace(
                'main.o: main.c unused.h',
                'main.o: main.c unused.h config.h')
            candidate = root / 'incomplete.patch'
            candidate.write_text(''.join(difflib.unified_diff(
                before.decode().splitlines(True), partial.splitlines(True),
                fromfile='a/Makefile', tofile='b/Makefile')))
            result = validate(p, candidate, root / 'validation')
            self.assertEqual(result['checks'], {
                'patch_applies': True, 'build': True, 'test': True,
                'header_change': True, 'no_missing': False})
            self.assertIsNone(result['error'])
            self.assertFalse(result['accepted'])
            self.assertTrue(result['rollback'])
            self.assertTrue(result['source_unchanged'])
            self.assertEqual(makefile.read_bytes(), before)
            recheck = json.loads((root / 'validation/recheck.json').read_text())
            self.assertEqual(
                {(f['target'], f['dependency']) for f in recheck['findings']
                 if f['type'] == 'MISSING'},
                {('helper.o', 'extra.h')})


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
