# B04 E5–E7：DRAFT 实验

本分支只保留 B 组 E5–E7 实验。课程资料在仓库根目录，B 轨道实现、样例、测试、候选和运行证据全部在 `labs/B-draft/`；不再依赖 tinygrad、E2–E4 或其他组代码。

## 阅读顺序

|文件或目录|用途|
|---|---|
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

## 当前证据

E5王佳宝（241880446）、E6史益瑄（241830086）的原报告、候选、来源和运行日志均保留。E7高吟曦（231880168）已有26项服务测试、完整gate及正常GitLab Job 688402历史成功证据；分支保护、失败拒绝、恢复与最终合并按报告中实际状态填写。旧Job不代表本次独立布局的CI已通过。

当前根.gitlab-ci.yml只运行e7_b_quality_gate，使用e7-b-shell Runner，证据来自labs/B-draft/work/ci-e7-*/。GitHub样例位于ci/github，仅供参考，不自动切换平台。

本次独立分支整理、新旧路径、仓库外备份及提交注意见 [docs/目录重建说明.md](docs/目录重建说明.md)。未执行commit、push或远程配置变更。
