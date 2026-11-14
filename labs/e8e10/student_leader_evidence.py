"""B-track manual checks, to be executed in the school course container.

This orchestrates existing lab functions; it does not implement a repair algorithm.
Each invocation requires a fresh output directory and retains failed evidence.
"""
import argparse
import csv
import shutil
from pathlib import Path

from lab import buildchecker, fixture, patch, run, save, scan, validate


def candidate(project, out, name):
    before = (project / 'Makefile').read_bytes()
    (out / (name + '-before.Makefile')).write_bytes(before)
    report = scan(project)
    save(out / (name + '-input.json'), report)
    assert report['commit'] == run(['git', 'rev-parse', 'HEAD'], project).strip()
    assert {(f['type'], f['target'], f['dependency']) for f in report['findings']} == {
        ('MISSING', 'main.o', 'config.h'), ('REDUNDANT', 'main.o', 'unused.h')}
    diff, plan = patch(project, report)
    patchfile = out / (name + '.patch')
    patchfile.write_text(diff)
    save(out / (name + '-plan.json'), plan)
    assert (project / 'Makefile').read_bytes() == before
    run(['git', 'apply', '--check', str(patchfile.resolve())], project)
    assert run(['git', 'status', '--porcelain'], project).strip() == ''
    print('COMMIT_MATCH / CANDIDATE_SOURCE_UNCHANGED / APPLY_CHECK_PASS', name)
    print(diff)
    return before, report, patchfile, plan


def e8(out):
    project = out / 'project'
    fixture(project)
    before, report, patchfile, plan = candidate(project, out, 'candidate')
    save(out / 'fixed-md-report.json', report)
    save(out / 'patch-plan.json', plan)
    assert plan == [{'target': 'main.o', 'dependency': 'config.h', 'style': 'direct'}]
    stale = dict(report, commit='0' * 40)
    try:
        patch(project, stale)
    except ValueError as error:
        assert str(error) == 'STALE_REPORT'
        save(out / 'expected-failure.json', {'error': str(error)})
    else:
        raise AssertionError('stale report was not rejected')
    assert (project / 'Makefile').read_bytes() == before
    print('EXPECTED_REJECTION STALE_REPORT / SOURCE_BYTES_UNCHANGED')


def e9(out):
    expected = {
        'direct': b'main.o: main.c unused.h config.h\n',
        'macro': b'DEPS = main.c unused.h config.h\n',
        'mixed': b'main.o: main.c $(HEADERS) config.h\n',
    }
    for style in expected:
        project = out / style
        fixture(project, style)
        before, report, patchfile, plan = candidate(project, out, style)
        assert plan == [{'target': 'main.o', 'dependency': 'config.h', 'style': style}]
        copy = out / (style + '-apply-demo')
        shutil.copytree(project, copy, ignore=shutil.ignore_patterns('.git'))
        run(['git', 'init', '-b', 'main'], copy)
        run(['git', 'apply', '--check', str(patchfile.resolve())], copy)
        run(['git', 'apply', str(patchfile.resolve())], copy)
        after = (copy / 'Makefile').read_bytes()
        assert expected[style] in after
        if style == 'macro':
            assert b'main.o: $(DEPS)\n' in after
        if style == 'mixed':
            assert b'HEADERS = unused.h\n' in after
        recipes = lambda data: [line for line in data.splitlines(keepends=True)
                                if line.startswith(b'\t')]
        assert recipes(before) == recipes(after)
        assert (project / 'Makefile').read_bytes() == before
        print('STYLE_PASS / APPLY_TO_COPY_PASS / RECIPES_UNCHANGED', style)
    (out / '结论.txt').write_text(
        'direct修改目标行；macro修改DEPS定义；mixed保留宏定义和引用并修改目标行。\n'
        '三个原项目保持不变；补丁分别应用到验证副本；共享变量影响不在本检查范围。\n')


def e10(out):
    project = out / 'project'
    fixture(project)
    before, report, patchfile, plan = candidate(project, out, 'candidate')
    save(out / 'fixed-md-report.json', report)
    save(out / 'patch-plan.json', plan)
    (out / 'source-before.Makefile').write_bytes(before)

    rejected = validate(project, patchfile, out / 'reject-test', fail_test=True)
    assert rejected['accepted'] is False and rejected['checks']['test'] is False
    assert rejected['rollback'] and rejected['source_unchanged']
    assert (project / 'Makefile').read_bytes() == before
    print('EXPECTED_TEST_REJECTION', rejected)

    accepted = validate(project, patchfile, out / 'accept')
    assert accepted['accepted'] and all(accepted['checks'].values())
    assert not accepted['source_unchanged'] and not accepted['rollback']
    after = (project / 'Makefile').read_bytes()
    assert b'main.o: main.c unused.h config.h\n' in after
    assert (project / 'config.h').read_bytes() == b'#define VALUE 1\n'
    assert (out / 'accept/sandbox/config.h').read_bytes() == b'#define VALUE 2\n'
    (out / 'source-after-accept.Makefile').write_bytes(after)
    print('ACCEPTED_ALL_CHECKS_PASS', accepted)

    broken = out / 'broken.patch'
    broken.write_text('invalid patch\n')
    rejected_patch = validate(project, broken, out / 'reject-patch')
    assert not rejected_patch['accepted']
    assert rejected_patch['rollback'] and rejected_patch['source_unchanged']
    assert rejected_patch['error'] and 'git' in rejected_patch['error']
    assert (project / 'Makefile').read_bytes() == after
    print('EXPECTED_BAD_PATCH_REJECTION', rejected_patch)

    dynamic = buildchecker(project, out / 'recheck-buildchecker')
    assert not any(f['type'] == 'MISSING' for f in dynamic['findings'])
    rows = [{'case': case, 'passed': True} for case in
            ['test-rejection', 'accepted', 'patch-rejection']]
    with (out / 'results.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['case', 'passed'])
        writer.writeheader()
        writer.writerows(rows)
    print('B_GATE_PASS', rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['e8', 'e9', 'e10'])
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    out = args.out.resolve()
    if out == root / 'work' or not out.is_relative_to(root / 'work'):
        parser.error('--out must be a fresh subdirectory of repository work/')
    if out.exists():
        parser.error('output already exists; choose a new directory')
    out.mkdir(parents=True)
    # A successful gate is emitted only after all stage assertions return.
    {'e8': e8, 'e9': e9, 'e10': e10}[args.stage](out)
    gate = {'track': 'B', 'stage': args.stage, 'passed': True}
    if args.stage == 'e10':
        gate['rows'] = 3
    save(out / 'gate.json', gate)
    print('COMPLETED', args.stage, out)


if __name__ == '__main__':
    main()
