# ADR-001：B 侧异步 Job 与可验证产物

## Context

DRAFT 和 MDFixer 都可能超过一次 HTTP 请求的合理时间。Dockerfile、镜像、Patch 和日志也不适合全部放入响应体。REPAIR 还必须防止把旧提交的 finding 应用到新源码。

## Decision

- 四类服务共用异步 Job 生命周期：创建返回 `202` 和 `QUEUED`，随后查询 `GET /v1/jobs/{job_id}`。
- 产物使用 `artifact://` 引用，并记录 SHA-256、生产 Job 和 commit。
- REPAIR 只接受同 commit 的 `MISSING` finding。`REDUNDANT` 不自动交给 MDFixer。
- 候选 Patch 只有在应用、构建、功能验证和重检均通过后才能接受。失败候选要保留原因并恢复原工作副本。

## Alternatives

- 同步 HTTP 等待：实现简单，但容易超时，也不利于查询多轮候选。
- 直接把日志和 Patch 放入 JSON：读取方便，但响应体过大且无法独立校验完整性。
- 允许修复 RD：可扩大功能，但超出 MDFixer 的 Missing Dependency 任务范围。

## Consequences

调用方需要保存 Job 状态和产物元数据，平台也必须定义 `artifact://` 的实际下载方式。好处是每个输入、候选、拒绝原因和最终产物都可追溯到固定版本。
