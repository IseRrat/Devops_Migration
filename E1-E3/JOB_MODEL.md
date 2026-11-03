# E2 统一异步任务模型

本文件是 A04/B04 共用的任务生命周期契约。各组只能在自己的目录维护服务专用请求和输出 Schema，不得复制维护 Job 状态、错误或公共产物定义。

公共 JSON Schema 位于：

- `E1-E3/schemas/job.schema.json`
- `E1-E3/schemas/artifact.schema.json`

## 创建与查询

四个创建端点均返回 HTTP `202`。创建请求必须携带 `Idempotency-Key` HTTP 头；同一调用方使用同一键和相同请求体重试时，服务必须返回同一个 `job_id`。同一键配合不同请求体时返回 HTTP `409` 和 `VALIDATION_0002`。

| `job_type` | 创建端点 | 生产方 |
|---|---|---|
| `DRAFT` | `POST /v1/dockerfile-jobs` | B04 |
| `FULL_CHECK` | `POST /v1/full-check-jobs` | A04 |
| `INCREMENTAL_CHECK` | `POST /v1/incremental-check-jobs` | A04 |
| `REPAIR` | `POST /v1/repair-jobs` | B04 |

所有任务通过 `GET /v1/jobs/{job_id}` 查询。

## 状态不变式

- `QUEUED`、`RUNNING` 不得携带 `output` 或 `error`。
- `SUCCEEDED` 必须携带 `output`，不得携带 `error`。
- `FAILED`、`TIMED_OUT`、`CANCELLED` 必须携带 `error`，不得携带 `output`。
- MD/RD finding 是成功分析结果，放入 `output`；环境、执行和分析器异常放入 `error`。

错误码格式为 `VALIDATION_####`、`ENV_####`、`EXEC_####`、`ANALYSIS_####` 或 `CANCEL_####`。参数错误在创建 Job 前以 HTTP `400` 返回；幂等键冲突使用 HTTP `409`。

## 产物读取

`artifact://<group>/<job_id>/<path>` 通过以下 HTTP 地址读取：

```text
GET /v1/artifacts/<group>/<job_id>/<path>
```

响应必须提供 `Content-Type`、`Content-Length` 和 `ETag`；调用方下载后校验契约中的 SHA-256。不存在返回 `ARTIFACT_4040`，无权限返回 `ARTIFACT_4030`，哈希不一致返回 `ARTIFACT_4090`。课程阶段的产物至少保留到 E12 验收结束。

示例 URI 只说明字段形状。只有能通过上述规则读取、可校验 SHA-256 且绑定不可变 commit 的文件才可作为运行证据。
