# AI_USAGE.md

## 2026-09-28：B3 E2 契约和验证

- 工具/任务：Codex 协助检查 E2/E3 课件、`featureA`、`featureB` 及 B3 分工，并在 `featureB` 补齐 B 侧公共契约。
- 提示摘要：仅完成 B3 的 Schema 汇总、ADR、Backlog、AI 记录、无效样例和验证工作，不把 B1/B2 工具本体冒充为 B3 产物。
- AI 建议：将统一 Job 终态不变式写入 Schema，为 DRAFT/REPAIR 同时提供请求和输出 Schema，并用无效 JSON 固定拒绝边界。
- 人工判断：采纳异步 Job、不可变 commit、artifact SHA-256 和“REPAIR 只消费同 commit MISSING”约束。拒绝把示例 URI/哈希写成真实服务证据。
- 关联文件：`CONTRACT_SUMMARY.md`、`schemas/`、`examples/`、`validate_e2_contracts.py`、`E2_BACKLOG.md`、`ADR-001-b-side-contracts.md`。
- 验证：使用无第三方依赖的脚本解析全部 Schema，有效样例必须通过，无效样例必须返回预期错误码。

## 2026-09-28：B3 E3 端到端验证

- 工具/任务：Codex 协助将课件中的 DRAFT 失败/成功基线和 MDFixer 修复/拒绝基线落为可重跑脚本及 CI。
- AI 建议：将静态结构检查与 Linux 动态行为验证分开；在 CI 中强制要求 `make` 和 C 编译器；使用独立临时仓库防止候选 Patch 污染原始样例。
- 人工判断：参考 Dockerfile/Patch 标记为 `INSTRUCTOR_ORACLE` 性质的验收样例，不冒充 B1/B2 工具自动生成结果。本地缺少工具链时只记录静态通过，不声称动态成功。
- 关联文件：`e3/`、`validate_b3.py`、`.gitlab-ci.yml`、`B3_CONTRIBUTION.md`。
- 验证：本地执行契约、DRAFT、MDFixer 静态检查和证据完整性校验；归档并校验了成功 Job 658805 的真实 DRAFT 容器 artifact。GitLab CI 已配置真实编译、增量修复、无效候选拒绝、Docker 对照和 B1 复现，但当前 Runner 的本机代理连接被拒绝，三个 Job 均未进入仓库脚本；没有将基础设施失败误记为业务验证失败或成功。

## 2026-10-02：公共契约收敛与复核修正

- 工具/任务：Codex 根据人工复核结果修正 E2/E3 交付，用户明确要求直接修改 `featureB`，并把公共契约放到公共位置。
- AI 建议：将 Job 生命周期和 artifact 引用移到 `devops_product/`，让 B04 只维护服务专用 Schema；使用标准 JSON Schema Draft 2020-12 验证器，并补充路径、布尔整数、终态冲突和候选一致性负例。
- 人工判断：采纳公共单一来源、A04/B04 字段映射、幂等规则和 artifact 下载约定；不把本次本地 Linux 验证冒充为 GitLab/Docker 证据。
- 关联文件：`../JOB_MODEL.md`、`../schemas/`、`A04_B04_ALIGNMENT.md`、`schemas/`、`examples/`、`validate_e2_contracts.py`、`e3/evidence/local-wsl-20261002/`。
- 验证：运行标准 Schema 校验、跨字段语义校验及 Linux 强制工具链测试；Docker 当前版本仍需在可用 daemon 或修复后的课程 Runner 上复现。
