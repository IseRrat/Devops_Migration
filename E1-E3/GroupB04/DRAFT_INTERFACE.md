# DRAFT 接口定义

DRAFT 接收固定版本的项目和成功判据，输出可构建的 Dockerfile、镜像引用及日志。

创建请求使用 `POST /v1/dockerfile-jobs`，并携带 `Idempotency-Key` HTTP 头。服务受理后立即返回 HTTP `202`、`job_id`、`trace_id` 和 `QUEUED`；调用方使用 `GET /v1/jobs/{job_id}` 查询状态和产物。幂等重试和冲突规则遵循 `../JOB_MODEL.md`。

- 请求 Schema：`schemas/draft-request.schema.json`
- 成功输出 Schema：`schemas/draft-output.schema.json`
- 有效/无效样例：`examples/draft-*.json`

## 输入

```json
{
  "schema_version": "1.0",
  "job_type": "DRAFT",
  "trace_id": "trace-e2-b04-draft-c0",
  "repository": {
    "url": "https://git.nju.edu.cn/IseRrat/devops.git",
    "commit": "完整的40位commit SHA"
  },
  "context_files": ["README.md", "pyproject.toml"],
  "build_command": "python -m pip install .",
  "verify_command": "python -c \"from tinygrad import Tensor; assert Tensor([1, 2, 3]).shape == (3,); print('tinygrad-ok')\"",
  "expected_stdout": "tinygrad-ok",
  "max_iterations": 30,
  "timeout_seconds": 1800
}
```

字段约束：

- `repository.commit` 使用完整 commit SHA，不能使用可移动的分支名。
- `context_files` 最多两份，对应 DRAFT 论文中的项目构建上下文。
- `context_files` 只允许使用 `/` 分隔的仓库内相对路径；拒绝绝对路径、反斜杠和 `..` 路径段。
- `build_command` 是项目本身的安装或构建命令。
- `verify_command` 在最终镜像内运行，退出码必须为 0；提供 `expected_stdout` 时还必须匹配标准输出。
- 构建失败后保留完整日志，并将末尾 50 行交给 DRAFT 生成下一轮 Dockerfile。

## 输出

```json
{
  "repository_commit": "完整的40位commit SHA",
  "dockerfile": {"uri": "artifact://groupb04/job-001/Dockerfile", "sha256": "实际SHA-256"},
  "image": {
    "reference": "nju-devops/groupb04/tinygrad:01234567",
    "image_id": "sha256:<64位十六进制>",
    "digest": null,
    "platform": "linux/amd64"
  },
  "build_log": {"uri": "artifact://groupb04/job-001/build.log", "sha256": "实际SHA-256"},
  "verify_log": {"uri": "artifact://groupb04/job-001/verify.log", "sha256": "实际SHA-256"},
  "iterations": [
    {"number": 1, "dockerfile_uri": "artifact://groupb04/job-001/candidate-1.Dockerfile", "result": "ACCEPTED", "selection_reason": "构建和功能验证通过"}
  ]
}
```

Docker build 和容器内功能验证都通过时，Job 才能为 `SUCCEEDED`；任一步失败均返回 `FAILED` 并保留候选 Dockerfile 与日志。示例中的 URI 和哈希不是真实运行证据。

执行陌生仓库时不得注入课程或平台密钥。实现必须使用隔离容器，设置 CPU、内存和总超时；默认关闭运行阶段网络。DRAFT 输出转为 A04 FULL_CHECK `configuration` 的规则见 `A04_B04_ALIGNMENT.md`。
