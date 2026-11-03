# B3/2 E3 可追溯证据

本目录只保存真实运行产生的不可变输出；说明性结论见 `../EVIDENCE.md`。

## local-wsl-20261002

该目录保存 2026-10-02 在 WSL/Linux 中运行 `validate_b3.py --require-toolchain` 的四份日志和汇总。它证明 DRAFT/MDFixer 夹具在 Linux 工具链中的动态行为，不证明当前根 Dockerfile 已完成容器构建。

## local-b2-20261010-182634

更新 B2 采集后运行 `validate_b3.py --require-toolchain --evidence-dir` 的实际记录。外层保存四项日志和 `summary.json`；`mdfixer/` 保存实例化 MD 报告、参考/拒绝补丁、实际应用 diff、五份阶段快照、环境和逐步命令 stdout/stderr/退出码。四项均通过，拒绝候选的非零构建退出码作为预期失败保留。报告 SHA 仅绑定独立样例仓库，不是 tinygrad 主项目 SHA。

## GitLab Job 658805

- Pipeline：[`335666`](https://git.nju.edu.cn/IseRrat/devops/-/pipelines/335666)
- Job：[`658805`](https://git.nju.edu.cn/IseRrat/devops/-/jobs/658805)
- 执行提交：`279853855005de330157d88ff37e5979bc88577f`
- 原提交者：NingAloha
- artifact 下载时间：2026-09-28

`gitlab-job-658805/` 是该 Job artifact 中 `ci-evidence/e3-draft/` 的原样归档。归档内失败候选在 `RUN make` 处以退出码 127 失败，参考候选构建成功，隔离运行输出 `hello E3`。

当前 `featureB` 中 `e3/draft/hello/Dockerfile.broken` 和 `Dockerfile.reference` 的 SHA-256 分别为：

```text
b163b7ab94b5c640d183cbcd01fd9bf6f7c9ee68d9b3cb59e2097bb27f337764
3575e975d293ebe472dbfeaa0ce6046d72058185ee8ce51aaf5f02eec217a911
```

它们与 Job 658805 artifact 内的对应文件逐字节一致。因此该 Job 可以作为这两份固定 DRAFT 验收样例的真实容器证据；它不证明当前分支的 B1 根目录 `Dockerfile` 或 B2 工具本体已经运行。
