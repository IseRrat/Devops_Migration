# A04/B04 E2 交接约定

配对关系：`GroupA04` 与 `GroupB04`。本文件固定双方在 E2 使用的字段映射；公共生命周期以 `E1-E3/JOB_MODEL.md` 和 `E1-E3/schemas/` 为唯一来源。

## DRAFT 到 FULL_CHECK

B04 的 DRAFT 成功输出与原请求共同生成 A04 的 `configuration`：

| A04 `configuration` 字段 | 来源 |
|---|---|
| `draft_job_id` | DRAFT Job 的 `job_id` |
| `dockerfile` | DRAFT `output.dockerfile` |
| `image.reference` / `image.image_id` | DRAFT `output.image` |
| `platform` | DRAFT `output.image.platform` |
| `project_root` | DRAFT 请求，当前固定为 `.` |
| `build_command` | DRAFT 请求的 `build_command` |
| `verify_command` | DRAFT 请求的 `verify_command` |
| `detector_version` | A04 BuildChecker 的不可变版本 |

`configuration_id` 由编排方在上述字段全部确定后生成。其规范输入为按字段名排序的 UTF-8 JSON，值包含 Dockerfile SHA-256、平台、项目根目录、构建命令、验证命令和检测器版本；ID 为该 JSON 的 SHA-256，格式为 `cfg-<64位小写十六进制>`。任一字段变化都必须生成新 ID 并重新跑全量检测。

## FULL_CHECK / INCREMENTAL_CHECK 到 REPAIR

B04 只接受 `type=MISSING` 的 finding。REPAIR 请求必须满足：

- `missing_report.report_commit == repository.commit`。
- 报告 URI 可按公共 artifact 协议读取并通过 SHA-256 校验。
- finding 中的 `target`、`dependency` 和 commit 与报告内容一致。
- `REDUNDANT` 不进入自动修复。

## 端点与错误

- DRAFT：`POST /v1/dockerfile-jobs`
- FULL_CHECK：`POST /v1/full-check-jobs`
- INCREMENTAL_CHECK：`POST /v1/incremental-check-jobs`
- REPAIR：`POST /v1/repair-jobs`
- 查询：`GET /v1/jobs/{job_id}`

创建端点均使用公共 `Idempotency-Key` 规则。参数错误不创建 Job；环境、执行、分析器错误进入 Job `error`；MD/RD 留在成功输出。

## E3/E12 实证要求

E2 只固定协议。E3 需要保存各自基线的真实命令、环境和日志；E12 必须用同一 `configuration_id` 完成一次 A04/B04 双方均可读取的真实产物交接，并记录双方使用的 commit SHA。
