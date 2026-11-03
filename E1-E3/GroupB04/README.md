# GroupB04 E2/E3 交付索引

本目录在保留 B1 的 DRAFT 环境文件的同时，补齐 B3 负责的公共契约、无效输入样例和端到端验证入口。

## E2

- `CONTRACT_SUMMARY.md`：DRAFT/REPAIR 与统一 Job 的字段、状态、端点和错误边界。
- `../JOB_MODEL.md`、`../schemas/`：A04/B04 唯一公共 Job 与 artifact 契约。
- `schemas/`：仅维护 DRAFT 请求/输出、REPAIR 请求/输出和修复报告 Schema。
- `A04_B04_ALIGNMENT.md`：DRAFT、FULL_CHECK、INCREMENTAL_CHECK、REPAIR 的跨组字段映射。
- `examples/`：有效样例及 job type、commit、context、finding、artifact URI 和终态错误样例。
- `validate_e2_contracts.py`：标准 Draft 2020-12 Schema 与跨字段语义验证器。
- `E2_BACKLOG.md`、`ADR-001-b-side-contracts.md`、`AI_USAGE.md`：B3 负责的过程记录。

在仓库根目录执行：

```bash
python3 -m pip install -r E1-E3/GroupB04/validation-requirements.in
python3 E1-E3/GroupB04/validate_e2_contracts.py
```

## E3

- `e3/draft/`：Tiny Greeting 的失败/参考 Dockerfile 和 B1 DRAFT 静态/动态检查。
- `e3/mdfixer/`：固定 MD、参考 Patch、无效候选和拒绝后恢复验证。
- `e3/EVIDENCE.md`：本地与 GitLab CI 证据边界。
- `e3/evidence/`：真实 Job artifact、来源说明及完整性校验输入。
- `validate_b3.py`：一次执行全部 B3 检查。
- 总入口指定 `--evidence-dir` 时，`mdfixer/` 子目录保存 B2 实例化报告、实际补丁、文件快照和逐步命令输出，使用新的证据目录运行。
- `PROJECT_REVIEW.md`：按 tinygrad 项目重新核对的 E2/E3 完成情况与未决项。

```bash
python3 E1-E3/GroupB04/validate_b3.py

# Linux/CI 中禁止跳过 make 和 C 编译器验证
python3 E1-E3/GroupB04/validate_b3.py --require-toolchain
```

旧 GitLab CI 曾配置 JSON Schema、工具链验证、DRAFT 失败/成功对照和 B1 Dockerfile 复现。历史 Runner 阻塞、运行时间及证据边界见 `e3/EVIDENCE.md`；这些记录不代表新 GitHub 仓库已经执行 E2/E3 CI。

## 其他阶段

E5–E7 入口为仓库根的 [`labs/B-draft/`](../../labs/B-draft/README.md)，组级说明见 [根 README](../../README.md)。本次 E1–E3 归档没有引入旧仓库的 E4 根工程。

## 证据边界

Schema 中的 `artifact://`、Job ID、镜像 ID 和 SHA-256 示例只用于校验格式。只有真实运行产生的不可变 commit、命令输出、退出码和可读产物才能记为实验证据。
