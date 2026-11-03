# B 侧公共契约汇总

## 统一异步 Job

四类服务共用 `../schemas/job.schema.json` 中的生命周期；B04 不再保存副本。创建任务后返回 HTTP `202`、`job_id`、`trace_id` 和 `QUEUED`；客户端通过 `GET /v1/jobs/{job_id}` 查询状态。所有创建端点必须携带公共契约规定的 `Idempotency-Key` HTTP 头。

| `job_type` | 创建端点 | B 侧角色 | 核心输入 | 核心输出 |
|---|---|---|---|---|
| `DRAFT` | `POST /v1/dockerfile-jobs` | 生产 | 仓库 commit、上下文、构建/验证命令 | Dockerfile、镜像、构建/验证日志 |
| `FULL_CHECK` | `POST /v1/full-check-jobs` | 消费 DRAFT 产物 | 固定 commit 和构建配置 | 实际图、声明图、MD/RD |
| `INCREMENTAL_CHECK` | `POST /v1/incremental-check-jobs` | 为后续 REPAIR 提供 finding | C0 基线、C1 commit 和相同配置 | 当前图及新增/消除 finding |
| `REPAIR` | `POST /v1/repair-jobs` | 生产 | 同 commit 的 `MISSING` finding、Makefile 和验证条件 | Patch、修复报告、构建/验证/重检证据 |

## 状态和错误

- `QUEUED` 和 `RUNNING` 表示任务已受理但尚未结束。
- `SUCCEEDED` 必须有 `output` 且不得有 `error`。检测到 MD/RD 仍然可以成功。
- `FAILED`、`TIMED_OUT` 和 `CANCELLED` 必须有 `error`，不得有 `output`；错误码使用 `ENV_3002`、`EXEC_4002`、`ANALYSIS_5001`、`CANCEL_4001` 等格式。
- 参数错误在创建任务前以 HTTP `400` 拒绝，不应创建 Job，也不应写成 MD/RD finding。

## 不可变与可追溯约束

- `repository.commit` 必须是 40 位小写十六进制 SHA，不接受分支名。
- REPAIR 只消费 `MISSING`，且 `missing_report.report_commit` 必须等于 `repository.commit`。
- 大文件通过 `artifact://` 传递，并同时记录 SHA-256、生产 Job 和源 commit；解析和错误规则见 `../JOB_MODEL.md`。
- `configuration_id` 必须与平台、Dockerfile、构建命令、验证命令、项目根目录和检测器版本一起固定。

## Schema 映射

| 文件 | 用途 |
|---|---|
| `../schemas/job.schema.json` | 唯一公共 Job 响应和终态不变式 |
| `../schemas/artifact.schema.json` | 唯一公共 artifact 引用 |
| `schemas/draft-request.schema.json` | DRAFT 创建请求 |
| `schemas/draft-output.schema.json` | DRAFT 成功输出 |
| `schemas/repair-request.schema.json` | REPAIR 创建请求 |
| `schemas/repair-output.schema.json` | REPAIR 成功输出 |
| `schemas/repair-report.schema.json` | 候选补丁的接受/拒绝原因和验证结果 |

与 A04 的字段映射和 `configuration_id` 生成规则见 `A04_B04_ALIGNMENT.md`。
