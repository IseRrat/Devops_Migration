# B04 DevOps 课程作业

本仓库汇集 B 组阶段作业：E2/E3 历史产物归档在 `E1-E3/`，E5–E7 的 DRAFT 实验在 `labs/B-draft/`。目录、验证入口和来源说明分别见下表。tinygrad 目标项目本体与旧 E4 根工程未迁入。

## 阅读顺序

|文件或目录|用途|
|---|---|
|[E1-E3/](E1-E3/README.md)|E2/E3 接口、公共契约、过程记录、验证样例与历史证据|
|[E1-E3/GroupB04/README.md](E1-E3/GroupB04/README.md)|B1/B2/B3 交付索引及新路径下的验证命令|
|[docs/00_开始与目录.md](docs/00_开始与目录.md)|B组任务、结构和路径约定|
|[docs/01_云主机环境与上传.md](docs/01_云主机环境与上传.md)|上传、工具和Docker检查|
|[docs/03_B轨道操作指南.md](docs/03_B轨道操作指南.md)|E5–E7命令与预期结果|
|[docs/04_GitHub_CI与合并门禁.md](docs/04_GitHub_CI与合并门禁.md)|B轨道CI、保护及失败/恢复，包含当前GitLab说明|
|[docs/05_验收清单.md](docs/05_验收清单.md)|提交与现场验收|
|[docs/06_常见问题.md](docs/06_常见问题.md)|排错|
|[labs/B-draft/](labs/B-draft/README.md)|B组全部实现和证据|
|[templates/实验报告.md](templates/实验报告.md)|组级报告；同目录含验收CSV及来源JSON|
|ci/|B组分支保护教材、失败及修复测试、GitHub参考样例|

A轨道内容已排除；课程编号保留，因此没有02号A组指南。

## 快速入口

在仓库根目录进入B实验：

```bash
cd labs/B-draft
python3 scripts/lab_cloud.py --help
python3 scripts/lab_cloud.py doctor
RUN=$(date -u +%Y%m%dT%H%M%SZ)
IMAGE="course1020-draft:e7-231880168-$RUN"
python3 scripts/lab_cloud.py build --image "$IMAGE" --out "work/build-$RUN" --build-timeout 1200
# build确认退出0后再执行gate
python3 scripts/lab_cloud.py gate --image "$IMAGE" --candidate fixtures/ci-candidates/e6-241830086/Dockerfile --out "work/gate-$RUN" --build-timeout 600
```

所有Docker构建上下文为labs/B-draft，不能在仓库根误用外部文件。Makefile、Compose、依赖锁与.env.example也位于此实验目录。

## E5–E7 历史证据

E5 王佳宝（241880446）、E6 史益瑄（241830086）、E7 高吟曦（231880168）的报告与已跟踪候选保留在 `labs/B-draft/`。历史测试、gate、Job 和合并状态按原报告记录。原 B-draft 分支没有跟踪 `labs/B-draft/work/`，本次迁移未上传其中的原始运行日志；旧 featureB 仍保存部分 E5/E6 证据，后续另行补迁。历史 Job 不代表新 GitHub 仓库的 CI 已通过。

根 `.gitlab-ci.yml` 是保留的旧 E7 配置；GitHub 样例位于 `ci/github/`，目前没有启用为 GitHub Actions。E8–E10 实验代码、workflow 和个人报告目录尚待按新手册导入。

旧 B-draft 分支的目录整理过程见 [docs/目录重建说明.md](docs/目录重建说明.md)，其中状态描述以原记录日期为准。本仓库以独立 main 历史接收阶段文件，来源 SHA 记录在迁移提交和 `E1-E3/README.md` 中。
