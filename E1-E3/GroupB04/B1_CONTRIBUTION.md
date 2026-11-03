# B1 个人贡献记录

贡献者：王佳宝，GitLab 用户名 `IseRrat`，Git 邮箱 `241880446@smail.nju.edu.cn`。

| 提交 | 内容 | 验证/结果 |
|---|---|---|
| `ff95709` | 建立 GroupB04 DRAFT 环境的初版契约、Dockerfile 夹具、有效/无效样例和构建验证脚本 | 固定了 DRAFT 的输入、Job 状态、输出产物及成功判据 |
| `32d89a5` | 清理 GroupB04 文本文件行尾 | 消除 Windows/Linux 行尾差异，便于后续在 Linux 环境复现 |
| `b7db9b9` | 按作业交付范围精简初版内容，将根 Dockerfile、构建说明、DRAFT 接口和输出格式集中到 GroupB04 | 删除非必需的重复夹具和脚本，形成可直接检查的 B1 交付结构 |
| `b7de0dd` | 完成 B1 最终精简，完善 tinygrad 多阶段 Dockerfile 和断网运行验证要求 | 镜像内安装本地 wheel，容器成功运行时输出 `tinygrad-ok` |
| `6e948e4` | 将 Job/Artifact 契约移到公共目录，补充 A04/B04 字段映射、严格 Schema 约束、边界样例和 Linux 验证汇总 | 7 个 Schema、25 个有效/无效样例及跨字段语义检查全部通过；DRAFT Linux 编译输出 `hello E3` |
| `09534fd` | 归档 E2 契约、DRAFT、MDFixer 和证据校验的 WSL/Linux 原始日志 | 四份日志与 `summary.json` 可在仓库内复核 |
| `9e814da` | 记录当前版本 GitLab Pipeline 和三个 Job 的实际失败信息 | 确认失败发生在 Runner 拉取基础镜像阶段，未把基础设施故障记为 B1 验证成功或代码失败 |

B1 的主要贡献是为陌生项目 tinygrad 提供可构建、可验证的根 Dockerfile，并明确 DRAFT 的输入、输出、镜像命名和运行成功判据。Dockerfile 使用多阶段构建生成并安装本地 wheel，最终容器不依赖源码目录，断网运行的预期输出为 `tinygrad-ok`。本人还参与了 E2 公共契约收口和 E3 Linux 证据补齐。

当前仓库已保存公共契约、静态校验结果和 WSL/Linux 动态日志。受 GitLab 执行环境拉取镜像失败影响，当前 B1 根 Dockerfile 尚缺本次提交对应的成功 Docker 构建日志、镜像 ID 和断网运行日志；该边界及对应 Job 已记录在 `e3/EVIDENCE.md`，没有将历史样例或失败流水线冒充为当前版本成功证据。
