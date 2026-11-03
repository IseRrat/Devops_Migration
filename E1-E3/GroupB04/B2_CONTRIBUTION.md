# B2 个人贡献记录

贡献者：高吟曦，GitLab 用户名：`Shelia-Yinxi`，Git 邮箱：`231880168@smail.nju.edu.cn`.

| 提交 | 内容 | 验证/结果 |
|---|---|---|
| | 扩展 `e3/mdfixer/validate_mdfixer_fixture.py`，增加 `--evidence-dir`，记录每步命令、stdout/stderr 和退出码 | 实际运行保存 32 条命令；无效候选的非零构建退出码及 `missing.h` 错误原文已归档 |
| | 保存实例化固定 MD 报告、参考/无效补丁、实际 Makefile diff 和五份阶段源码快照 | 报告 SHA 与临时样例仓库一致；初始、未修复增量、修复后、拒绝及恢复副本可复核 |
| | 修改 `validate_b3.py`，将 B2 详细产物接入总证据目录的 `mdfixer/` 子目录 | 总入口强制工具链验证的四项检查退出码均为 0，`failures` 为空 |
| | 添加 `e3/mdfixer/test_evidence.py`，检查失败命令归档及报告、补丁、快照与实际输出 | 两项测试通过 |
| | 补充 MDFixer README、证据索引及项目检查报告，说明人工基线、实际运行与未确认内容 | 文档区分独立 GNU Make 基线与 tinygrad 本体修复；最终交付认可仍待确认 |

B2 职责是 Missing Dependency 修复。本次在既有独立 C/GNU Make 样例上完善证据采集，未将此前已记录为 B3 的接口、固定夹具或参考补丁创建工作重新归属给 B2。实际观察为：未修复时修改 `config.h` 后增量输出仍为 `1`，参考补丁修复后再次修改头文件输出 `3`，无效候选被拒绝，新的原始副本能够构建并输出 `1`。

真实运行证据见 [local-b2-20261010-182634/summary.json](e3/evidence/local-b2-20261010-182634/summary.json)，逐步命令和原始输出见该目录下的 `mdfixer/commands.json` 与 `mdfixer/commands/`。
