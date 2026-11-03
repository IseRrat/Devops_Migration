# Tiny Greeting DRAFT 验证样例

构建命令为 `make`，功能验证命令为 `./hello`，标准输出必须精确为 `hello E3`。

`Dockerfile.broken` 故意不安装 `make` 和 C 编译器，预期在 `RUN make` 返回非零退出码。`Dockerfile.reference` 安装工具链后应成功构建，并能在 `--network none` 下运行。

两份 Dockerfile 只是 B3 用于验收 DRAFT 边界的固定样例，不是 DRAFT 工具的生成输出。
