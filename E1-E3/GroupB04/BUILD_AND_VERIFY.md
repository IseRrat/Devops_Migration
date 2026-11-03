# 历史 B1 tinygrad Dockerfile 的构建与验证

本文件对应 E2/E3 的 B1 交付。本作业仓库未包含 tinygrad 本体；先准备一份独立的 tinygrad 源码克隆，并确认所需版本。以下命令在 Devops_Migration 仓库根执行，`sourceDir` / `SOURCE_DIR` 改为该源码克隆的实际路径。Docker build context 指向目标项目，`VCS_REF` 记录目标项目的提交，而不是本作业仓库的提交。

原 Dockerfile 作为历史作业文件保留；这些命令及预期不代表本次迁移重新完成了容器构建。

## PowerShell

```powershell
$sourceDir = 'D:\projects\tinygrad'
$dockerfile = (Resolve-Path 'E1-E3/GroupB04/Dockerfile').Path
$commit = git -C $sourceDir rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw '请确认 tinygrad 源码克隆路径' }
$tag = $commit.Substring(0, 8)
$image = "nju-devops/groupb04/tinygrad:$tag"

docker build --file $dockerfile --build-arg VCS_REF=$commit --tag $image $sourceDir
if ($LASTEXITCODE -ne 0) { throw '构建失败，请保留原始日志' }
docker image inspect $image --format '{{.Id}}'
docker run --rm --network none $image
```

## Bash

```bash
(
set -e
SOURCE_DIR=/path/to/tinygrad
dockerfile="$PWD/E1-E3/GroupB04/Dockerfile"
commit="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
tag="${commit:0:8}"
image="nju-devops/groupb04/tinygrad:${tag}"

docker build --file "$dockerfile" --build-arg VCS_REF="$commit" --tag "$image" "$SOURCE_DIR"
docker image inspect "$image" --format '{{.Id}}'
docker run --rm --network none "$image"
)
```

构建命令和 `docker image inspect` 的退出码都应为 0。容器验证的退出码应为 0，标准输出应为：

```text
tinygrad-ok
```
