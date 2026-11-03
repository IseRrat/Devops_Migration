# Dockerfile / Image 输出格式

## Dockerfile

- 文件名固定为 `Dockerfile`。
- Docker build context 为项目仓库根目录。
- 最终文件计算 SHA-256，并使用 `artifact://groupb04/<job_id>/Dockerfile` 引用。

## Image

- repository：`nju-devops/groupb04/tinygrad`
- tag：项目 commit 的前 8 位
- 完整引用：`nju-devops/groupb04/tinygrad:<tag>`
- platform：`linux/amd64`，需要时另行构建 `linux/arm64`

```json
{
  "dockerfile": {
    "uri": "artifact://groupb04/job-001/Dockerfile",
    "sha256": "<Dockerfile的64位SHA-256>"
  },
  "image": {
    "reference": "nju-devops/groupb04/tinygrad:01234567",
    "image_id": "sha256:<64位十六进制>",
    "digest": null,
    "platform": "linux/amd64"
  },
  "build_log": "artifact://groupb04/job-001/build.log",
  "verify_log": "artifact://groupb04/job-001/verify.log"
}
```

本地构建时 `digest` 可以为 `null`；推送到 registry 后必须记录 registry 返回的 digest。tag 用于阅读和定位，image ID 或 digest 用于唯一标识镜像。
