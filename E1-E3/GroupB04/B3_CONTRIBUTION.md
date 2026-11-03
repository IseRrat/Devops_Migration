# B3 个人贡献记录

贡献者：Shi Yixuan，GitLab 用户名 `xiacikanhai`，Git 邮箱 `241830086@nju.edu.cn`。

| 提交 | 内容 | 验证/结果 |
|---|---|---|
| `88cd1e5` | E2 统一契约、6 个 Schema、17 个有效/无效样例、ADR、Backlog、AI 记录 | `validate_e2_contracts.py` 全部通过 |
| `30e5c0e` | E3 DRAFT 失败/参考样例，MDFixer 固定 MD、参考 Patch、无效候选和恢复验证 | 静态断言和 `git apply --check` 通过 |
| `29483a1` | B3 总验证入口、CI 和初版证据说明 | 本地总入口通过；首次 CI 暴露 Runner 外部依赖故障 |
| `261c58a` | 尝试使用 Runner 镜像缓存 | Runner 不允许项目设置 `if-not-present`，后续提交已修正 |
| `541bcab` | 移除不兼容拉取策略、固定 DinD 版本并加基础设施重试 | CI 明确定位为 Runner 失效代理，不是脚本失败 |
| `42ef513` | 归档与当前样例哈希一致的成功 DRAFT Job 658805 artifact | 失败码、镜像 ID 和断网运行输出均可查 |
| `818c6d3` | 增加对当前 B1 根 Dockerfile 的真实复现 Job | Pipeline 336265 因 Runner 代理故障未进入脚本 |
| `eb7c808` | 将证据来源、文件哈希和关键输出纳入自动校验 | 本地总入口四项检查全部通过 |

B3 不声称实现 DRAFT 或 MDFixer 工具本体。本人贡献是公共接口、验收边界、可重跑脚本、失败/拒绝样例、B1/B2 复现入口和证据整理。Linux Make/C/Git 动态验证已于 2026-10-02 补齐；当前仍缺受 Runner 主机失效代理阻塞的“当前版本 Docker 动态日志”，边界及恢复办法已写入 `e3/EVIDENCE.md`。
