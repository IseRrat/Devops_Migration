# MDFixer 固定 MD 验证样例

`fixed-md-report.template.json` 将 `main.o -> config.h` 标记为 `INSTRUCTOR_ORACLE` Missing Dependency。运行脚本时，`${SOURCE_COMMIT}` 必须替换为当次临时仓库的完整 SHA，不得把模板字符串当作真实报告。

报告 `location.source` 指向 `main.c` 第 2 行的 include，`location.declaration` 指向 Makefile 第 6 行的 `main.o` 规则；路径相对于样例源码根目录。行号描述初始版本，不是修复后版本。静态检查核对行文本，实际归档报告再与 `snapshots/before/` 对照；历史报告不追补本次字段。

- `reference.patch` 为预期可接受的参考补丁。
- `invalid-candidate.patch` 故意加入不存在的 `missing.h`，应因构建失败而拒绝。
- 拒绝无效候选后，独立原始副本必须仍能构建并输出 `1`。

单纯 clean build 成功不是充分证据。修复后再修改 `config.h`，普通 `make` 必须触发重新编译。

主项目为 tinygrad；本目录是独立 GNU Make 修复基线，具有 E3 课件所列的固定 MD 报告、修复样本和验证行为。是否可作为本组最终交付，尚无教师或组内确认记录。它不表示 tinygrad 本体存在 `main.o -> config.h`，也不是 MDFixer 自动生成的修复。tinygrad 本体尚无已确认的 MD 与参考 Patch，未决项见 [PROJECT_REVIEW.md](../../PROJECT_REVIEW.md)。

## 保存逐步证据

在仓库根目录指定新的目录运行：

```bash
python3 E1-E3/GroupB04/e3/mdfixer/validate_mdfixer_fixture.py \
  --require-toolchain --evidence-dir work/b2-e3-new-run
```

该目录必须尚不存在，以避免覆盖历史记录。仅运行验证而不需要落盘时，可以不传 `--evidence-dir`。

归档内容：

- `fixed-md-report.json`：实际临时样例仓库 SHA 替换后的人工参考报告。
- `reference.patch`、`invalid-candidate.patch`：本次使用的补丁原件；`applied.patch` 是实际应用后 Makefile 的 Git diff。
- `snapshots/`：初始、未修复增量、修复后、拒绝候选及恢复副本的 Makefile、源码和头文件。
- `commands.json`：每步命令、工作目录、退出码、stdout/stderr；对应原始输出另存于 `commands/`。
- `environment.json`：本次系统、架构、Python、Git、Make 和编译器版本。
- `observations.json`：实际验证摘要；发生异常时保存 `error`，此前命令记录仍保留。

无效候选的非零构建退出码是预期拒绝证据，不等于总验证失败。恢复检查使用新的原始副本，不声称在拒绝副本上执行了回滚。样例 SHA 不代表主项目 tinygrad 的版本。

样例 Git 提交沿用原脚本的固定作者 `B3 E3 Fixture`、占位邮箱和固定日期 `2026-09-28T00:10:00+0000`，用于生成可重复的临时样例版本；不是实际组员身份、运行日期或个人贡献提交。实际运行时间见 `environment.json`。报告来源字段 `INSTRUCTOR_ORACLE` 沿用原课程样例模板，不表示实际检测器发现或教师对本次交付的认证。

总入口 `validate_b3.py --require-toolchain --evidence-dir <新目录>` 会自动将上述产物放在 `<新目录>/mdfixer/`，外层仍保存原有四份日志和 `summary.json`。
