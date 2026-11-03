# E1–E3 阶段作业归档

本目录按组内约定命名为 `E1-E3`，本次迁入的是已检索确认的 E2/E3 产物。E2 的接口、Schema、过程文档与 E3 的样例、验证程序、历史证据保留原有内部结构。

|入口|内容|
|---|---|
|[GroupB04/README.md](GroupB04/README.md)|B1/B2/B3 交付索引、验证命令及阶段边界|
|[JOB_MODEL.md](JOB_MODEL.md)、[schemas/](schemas/)|跨组公共 Job 与 artifact 契约|
|[GroupB04/schemas/](GroupB04/schemas/)、[GroupB04/examples/](GroupB04/examples/)|B 组专用 Schema 和 25 个接口样例|
|[GroupB04/e3/](GroupB04/e3/README.md)|DRAFT 与 MDFixer 固定基线及验证程序|
|[GroupB04/e3/evidence/](GroupB04/e3/evidence/README.md)|旧 GitLab、WSL 和 B2 真实运行记录|
|[GroupB04/BUILD_AND_VERIFY.md](GroupB04/BUILD_AND_VERIFY.md)|历史 B1 Dockerfile 的外部 tinygrad 构建上下文说明|

在仓库根目录执行：

```bash
python3 -m pip install -r E1-E3/GroupB04/validation-requirements.in
python3 E1-E3/GroupB04/validate_b3.py --require-toolchain
```

第二条命令需要 Linux 上的 Git、GNU Make 和 C 编译器。没有完整工具链时可不传 `--require-toolchain` 进行静态核查，静态通过不代表动态验证通过。

## 来源与迁移范围

- 来源：`https://git.nju.edu.cn/IseRrat/devops.git`，`featureB`，提交 `651db294be99e03ed22dd3f229fe7833740519a0`。
- 迁入该提交中 `devops_product/` 下筛选确认的 133 个文件，路径前缀改为 `E1-E3/`，不包含 `GroupB04/e5-e7/`。提交 `d71f865` 晚补的 B2 E2/E3 材料在范围内。
- 本次更新运行命令、入口与依赖提示中的本地路径；历史证据、作者贡献、历史 SHA 和原始日志保持原件。
- JSON Schema 的 `$id` / `$ref` 是既有公共契约标识，保留原 URI；验证器通过本地 Schema store 解析，不要求存在旧目录或访问旧站点。
- `AI_USAGE.md`、历史运行命令等保留的 `devops_product/` 字样表示原位置，不是当前目录。
- 未引入旧 E4 根工程、tinygrad 本体、旧项目历史及旧 E2/E3 GitLab CI 配置；本次也没有重新宣称历史主项目容器已构建成功。

E5–E7 位于 [labs/B-draft/](../labs/B-draft/README.md)。新阶段个人报告后续按手册放入 `docs/students/<学号>/e8-e10/`。
