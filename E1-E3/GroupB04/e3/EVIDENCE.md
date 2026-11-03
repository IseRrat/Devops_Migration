# B3 E3 证据汇总

迁移说明（2026-11-03）：当前目录从旧 GitLab 的 `devops_product/GroupB04/e3/` 迁至 `E1-E3/GroupB04/e3/`。下文历史命令、Job、Runner 状态和原始日志保留当时来源；当前可重跑命令使用新路径。原 CI 状态不代表 GitHub 的当前检查结果。

## 当前分支可重跑检查

在仓库根目录执行：

```bash
python3 E1-E3/GroupB04/validate_b3.py
```

2026-09-28 在 Windows 环境的结果如下：

| 类别 | 当前结果 | 证据边界 |
|---|---|---|
| E2 契约 | 6 个 Schema 可解析；17 个有效/无效样例全部得到预期结果 | 本地真实执行 |
| DRAFT | 失败/参考候选和 B1 Dockerfile 静态断言通过 | 本机无 Docker、make 和 C 编译器，未声称动态通过 |
| MDFixer | 固定 MD、参考 Patch、拒绝 Patch 和恢复路径静态断言通过；两份 Patch 通过 `git apply --check` | 本机无 make 和 C 编译器，未声称当前文件动态通过 |
| 证据绑定 | Job 658805 元数据、两份 Dockerfile SHA-256、预期失败日志、镜像 ID 和运行输出全部通过检查 | 本地真实执行 `e3/validate_evidence.py` |

传入 `--evidence-dir <目录>` 可保存四项检查日志和 `summary.json`。Linux/CI 应再传入 `--require-toolchain`，禁止跳过编译与增量构建验证。

## 已归档的真实 DRAFT 容器证据

[Pipeline 335666](https://git.nju.edu.cn/IseRrat/devops/-/pipelines/335666) 的 [Job 658805](https://git.nju.edu.cn/IseRrat/devops/-/jobs/658805) 于 2026-09-26 成功完成：

- `Dockerfile.broken` 在 `RUN make` 处以退出码 127 失败，日志包含 `/bin/sh: 1: make: not found`。
- `Dockerfile.reference` 构建成功，镜像 ID 为 `sha256:1d39b81e91d4c4584cd0d80178608b76dfcfaed6e43afe990236223f714cd045`。
- `docker run --rm --network none` 退出码为 0，标准输出为 `hello E3`。
- artifact 内两份 Dockerfile 与当前 `featureB` 固定验收样例的规范化 SHA-256 完全一致。

原始 artifact 已归档在 `evidence/gitlab-job-658805/`，来源、原提交者和哈希说明见 `evidence/README.md`。这份证据只覆盖固定 DRAFT 验收样例，不冒充当前 B1 根 Dockerfile 或 B2 工具本体的运行结果。

## 2026-10-02 本地 Linux 强制验证

在 WSL/Linux 中对 `featureB` 执行：

```bash
python3 devops_product/GroupB04/validate_b3.py \
  --require-toolchain \
  --evidence-dir devops_product/GroupB04/e3/evidence/local-wsl-20261002
```

结果：公共及 B04 的 7 个 Draft 2020-12 Schema、25 个有效/无效样例和跨字段语义检查全部通过；DRAFT 本地编译输出 `hello E3`；MDFixer 复现未修复旧值 `1`、修复后增量值 `3`、无效候选拒绝和恢复通过。完整日志及 `summary.json` 位于上述 evidence 目录。

本次记录是 Make/C/Git 的 Linux 动态证据，不是 Docker 证据。当前 B1 根 Dockerfile 仍需在可用 Docker daemon 或修复后的课程 Runner 上构建并保存镜像 ID 与断网运行日志。

## 当前 GitLab CI 与基础设施阻塞

`.gitlab-ci.yml` 已定义三个 Job：

1. `b3_contracts_and_fixtures`：强制运行 E2、DRAFT、MDFixer 和证据完整性验证。
2. `b3_draft_docker`：复现固定 DRAFT 样例的预期失败和参考成功。
3. `b3_reproduce_b1_draft`：构建当前 B1 根 `Dockerfile`，断网运行并断言 `tinygrad-ok`。

[Pipeline 336265](https://git.nju.edu.cn/IseRrat/devops/-/pipelines/336265) 在提交 `818c6d31ac61ee9673e548aebeffcfb062c3a786` 上触发，三个 Job（[660498](https://git.nju.edu.cn/IseRrat/devops/-/jobs/660498)、[660499](https://git.nju.edu.cn/IseRrat/devops/-/jobs/660499)、[660500](https://git.nju.edu.cn/IseRrat/devops/-/jobs/660500)）都在仓库检出和业务脚本运行前结束，统一原因为 `runner_external_dependency_failure`。

Job 日志显示 Runner `devops-lab` 强制采用 `always` 拉取策略，但其 Docker daemon 访问镜像仓库时尝试连接本机代理 `127.0.0.1:16152`，得到 `connect: connection refused`。项目内指定 `pull_policy: if-not-present` 又会被该 Runner 配置拒绝。因此这不是验证脚本失败，仓库代码也无法修复 Runner 主机代理。

恢复条件：Runner 管理员修复/移除失效代理，或允许 `if-not-present` 并提供已缓存镜像，然后在 GitLab 重跑 Pipeline 336265。重跑成功后应下载 `b3-evidence/` artifact，并把 Job URL、commit SHA、镜像 ID 和日志作为最终 B1/B2 当前版本的动态证据。

### 2026-10-02 修复提交后的复跑

公共契约和 Linux 证据修复推送到提交 `09534fd66cd61efb9edc7e62df0f3eac58acf4f9` 后，GitLab 自动创建 [Pipeline 337413](https://git.nju.edu.cn/IseRrat/devops/-/pipelines/337413)。三个 Job 均在仓库业务脚本执行前以 `runner external dependency failure` 结束：

- [`b3_contracts_and_fixtures` / 663488](https://git.nju.edu.cn/IseRrat/devops/-/jobs/663488)
- [`b3_draft_docker` / 663489](https://git.nju.edu.cn/IseRrat/devops/-/jobs/663489)
- [`b3_reproduce_b1_draft` / 663490](https://git.nju.edu.cn/IseRrat/devops/-/jobs/663490)

因此本次失败不能用于判断 JSON Schema、DRAFT、MDFixer 或根 Dockerfile 是否通过；仓库内 `local-wsl-20261002/` 仍是当前可复核的 Linux Make/C/Git 动态证据，Docker 动态证据继续等待 Runner 恢复。
