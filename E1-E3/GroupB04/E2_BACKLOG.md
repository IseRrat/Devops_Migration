# B3 E2 Backlog

| 编号 | 事项 | 产物 | 验收条件 | 状态 |
|---|---|---|---|---|
| B3-E2-01 | 统一 B 侧契约 | `CONTRACT_SUMMARY.md` | DRAFT/REPAIR 与统一 Job 字段一致 | 已完成 |
| B3-E2-02 | 补齐请求与输出 Schema | `schemas/*.schema.json` | 全部可解析，成功/失败边界明确 | 已完成 |
| B3-E2-03 | 准备有效与拒绝样例 | `examples/*.json` | 覆盖 job type、commit、context、finding、URI 和终态 | 已完成 |
| B3-E2-04 | 提供无依赖验证器 | `validate_e2_contracts.py` | 有效样例通过，无效样例按预期错误码拒绝 | 已完成 |
| B3-E2-05 | 记录决策和 AI 使用 | ADR、`AI_USAGE.md` | 写明选择、代价、人工判断与验证 | 已完成 |
| B3-E2-06 | 确定跨组 artifact 下载协议 | `../JOB_MODEL.md` | URI 解析、HTTP 错误、SHA-256 和保留期已定义 | 契约已完成；E12 实证待完成 |
| B3-E2-07 | 固定 A04/B04 字段映射 | `A04_B04_ALIGNMENT.md` | DRAFT 可无歧义转换为 FULL_CHECK 配置，finding 可进入 REPAIR | 已完成 |
| B3-E2-08 | 以 JSON Schema 校验样例 | `validate_e2_contracts.py` | Draft 2020-12、格式检查和跨字段语义均执行 | 已完成 |

本 Backlog 只声明 B3 已完成的契约和本地验证。它不代表 DRAFT/MDFixer 服务本体或跨组端到端联调已完成。
