# AI 使用记录

工具/模型/日期：OpenAI Codex，本次会话模型 gpt-6.1-sol，2026-11-03。

输入上下文与问题：课程 E8 B 手册、07 提交与排错、08 个人测试示例、课程 lab.py/test_profile.py、本人学号 241880446、已准备的 GitHub 仓库与服务器个人目录。任务范围为完成 E8 手工路线、自主测试、报告、PR/CI 和证据归档。 用户后续提供 MDFixer Fig. 6 设计图，用于补充报告的机制对照；未将截图当作运行证据，也未扩展为未实际实现的论文机制。

模型建议：按步骤生成固定报告、检查样例版本、生成 direct Patch、执行可应用检查、验证旧报告拒绝。自主任务选择 REDUNDANT-only，在第 08 文件 recipe 字节保持示例基础上，增加 extra.h 冗余声明并用真实 scan 报告验证空补丁与源文件保持。

采纳与理由：采用课程 fixture/scan/patch 和辅助脚本，不重写算法。保留原 7 项测试，新增 1 项有独立集合及字节预期的测试。将参考运行和新增测试后的复核放到不同 OUT，分别记录外层源码 SHA 与内部样例 SHA。

人工与生成内容的边界：用户确定任务范围、学号及仓库，并授权服务器操作。此次新增测试和报告由 Codex 协助编写与执行，没有记录用户逐行手写的修改，不虚构人工修改。课程源码、原 7 项测试和第 08 文件例子属于参考材料，不作为个人原创算法。E8 candidate.patch 来自课程 patch()，不是由对话模型直接生成。

实际验证：work/e8-B-manual.m3Z5dh 与 work/e8-B-manual.Tckga8 各 6 份步骤日志退出 0；报告精确包含 MISSING config.h 与 REDUNDANT unused.h；生成候选不修改原项目；错误 commit 被 STALE_REPORT 拒绝且源字节相同。容器 unittest discover 共 8 项通过，日志 work/unit-tests-20261103-200915.log，退出 0。

范围限制：本次只执行个人 E8。未把 git apply --check 当作完整构建验证；未声称已经完成个人 E9/E10 或跨组远程联调。后续 GitHub Actions 的通用多阶段门禁与本人的逐步实验分开记录，以对应实际 headSha、run.json 和 artifact 为准。
