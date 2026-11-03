# REPAIR / MDFixer 接口定义

REPAIR 任务使用带 `Idempotency-Key` HTTP 头的 `POST /v1/repair-jobs` 创建，并通过 `GET /v1/jobs/{job_id}` 查询。幂等规则遵循 `../JOB_MODEL.md`。

- 请求 Schema：`schemas/repair-request.schema.json`
- 成功输出 Schema：`schemas/repair-output.schema.json`
- 修复报告 Schema：`schemas/repair-report.schema.json`
- 有效/无效样例：`examples/repair-*.json`

## 输入边界

- `repository.commit` 必须是完整 40 位 SHA。
- `missing_report.finding_type` 只能是 `MISSING`。
- `missing_report.report_commit` 必须与 `repository.commit` 完全相同。
- `missing_report.uri` 必须是 `artifact://` URI，同时提供实际 SHA-256。
- `makefile_path` 只允许使用 `/` 分隔的仓库内相对路径，禁止绝对路径、反斜杠和 `..` 路径段。

## 候选验证

每个候选 Patch 要依次记录应用、构建、功能验证和重检结果。只有四项均通过的候选才可接受。无效候选必须记录拒绝原因，并恢复未受污染的工作副本。

## 成功输出

`SUCCEEDED` 的输出必须包含 Patch、repair report、build log、verify log 和 recheck report 的 URI/SHA-256，以及所有候选的接受/拒绝摘要。单纯 clean build 成功不足以证明 Missing Dependency 已修复；修改目标头文件后的普通增量构建必须重新编译并产生新结果。
