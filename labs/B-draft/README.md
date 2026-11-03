# B04 DRAFT：B组E5–E7实验

当前目录包含完整运行所需文件：services/为服务和26项测试，fixtures/为实验样例和稳定E6候选，scripts/为环境/构建/gate入口，work/为原始证据及新输出，docs/为各阶段个人报告。

```bash
# 从仓库根进入
cd labs/B-draft
python3 scripts/lab_cloud.py --help
python3 scripts/lab_cloud.py doctor
```

运行方法见 [B轨道指南](../../docs/03_B轨道操作指南.md)，CI/演示步骤见 [E7执行与门禁](docs/E7_执行与门禁_231880168.md)。构建和gate都从当前目录执行，重跑必须使用全新work子目录。

- [E5报告（王佳宝，241880446）](docs/实验报告.md)与work/e5-01/、work/candidate/保留原件。
- [E6报告（史益瑄，241830086）](docs/E6_实验报告_241830086.md)与work/e6-241830086*/保留原件。
- [E7报告（高吟曦，231880168）](docs/E7_实验报告_231880168.md)。
- [E7服务器备份及校验](work/backups/E7-231880168/README.md)，CI原始脱敏日志位于work/e7-evidence-231880168/。

历史报告和日志内服务器旧路径保持原样，不应改写为当前分支路径。新旧位置映射见 [目录重建说明](../../docs/目录重建说明.md)。
