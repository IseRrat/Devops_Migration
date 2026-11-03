# B3 E3 端到端验证基线

本目录只实现 B3 的验证职责：使用固定输入复现 B1 DRAFT 和 B2 MDFixer 的成功、失败与拒绝边界。夹具中的参考 Dockerfile/Patch 是 `INSTRUCTOR_ORACLE` 性质的预期答案，不得计作 DRAFT/MDFixer 工具自动生成结果。

## DRAFT

`draft/hello/` 是课件 Tiny Greeting 样例：

- 构建命令：`make`
- 功能验证：`./hello`
- 预期标准输出：`hello E3`
- `Dockerfile.broken`：故意缺少 C 工具链，应在 `RUN make` 失败。
- `Dockerfile.reference`：安装 `gcc`、`make`、`libc6-dev`，应构建成功并在断网运行时输出 `hello E3`。

## MDFixer

`mdfixer/` 固定 `main.o -> config.h` 这条 Missing Dependency：

- 未修复时，将 `VALUE` 从 1 改为 2，普通 `make` 仍输出 1。
- `reference.patch` 把 `config.h` 加入 `main.o` 的 prerequisites。
- 修复后将 `VALUE` 改为 3，普通 `make` 必须重新编译并输出 3。
- `invalid-candidate.patch` 引入不存在的 `missing.h`，必须拒绝，同时验证原始副本仍可构建。

## 命令

无工具链环境可运行静态检查：

```bash
python3 E1-E3/GroupB04/e3/draft/validate_draft_fixture.py
python3 E1-E3/GroupB04/e3/mdfixer/validate_mdfixer_fixture.py
python3 E1-E3/GroupB04/e3/validate_evidence.py
```

Linux 或 CI 必须强制动态验证：

```bash
python3 E1-E3/GroupB04/e3/draft/validate_draft_fixture.py --require-toolchain
python3 E1-E3/GroupB04/e3/mdfixer/validate_mdfixer_fixture.py --require-toolchain
```
