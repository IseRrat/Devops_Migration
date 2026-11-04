# 决策记录：B 组候选生成、影响范围与验证

背景与约束：固定 MD 报告必须对应当前样例提交。E8 使用 direct 声明，只补 main.o 缺失的 config.h，保留冗余依赖和编译配方。原始项目和候选产物分别保存，后续才能核对候选改变了什么。

选择与替代方案：沿用课程 patch() 返回 Git diff 与修改计划，先检查版本，再执行 git apply --check。没有在生成候选时直接写回原 Makefile，也没有顺带删除 REDUNDANT。只有 RD 的真实报告应产生空候选，原文件保持相同字节。

失败保护：将报告 commit 改为不匹配值，预期 STALE_REPORT，并比较原 Makefile 字节。自主测试先在临时目录应用正确候选、核对 recipe 字节，再加入 extra.h 冗余声明形成两个 RD，确认 patch 不会删除它们。

代价与覆盖范围：保留 RD 会留下暂时冗余的 prerequisites，但符合当前只修复 MISSING 的范围。E8 未覆盖 macro、mixed 和跨目标共享变量；E9 的验证记录见下文。版本检查不能代替质量验证，完整构建、功能测试及失败回滚属于 E10。

验证命令与实际证据：按 E8 B 手册分步调用 lab_python，参考 OUT 为 work/e8-B-manual.m3Z5dh，新源码 OUT 为 work/e8-B-manual.Tckga8；两套各 6 步退出 0。按 07 的容器 unittest discover 命令运行原 7 项和新增 1 项测试，work/unit-tests-20261103-200915.log 显示 8 项 OK、退出 0。core lab.py 未变更。

## E9：保留声明结构，并记录共享变量影响

背景与选择：按 E9 手册分别创建 direct、macro、mixed 三个独立项目，沿用课程 patch()，对纯变量修改 DEPS 定义，对混合声明保留宏引用并补目标行。应用演示只在副本进行，原项目保存为对照。

自主任务选择手册列出的共享变量影响分析。新增 helper.o 对 DEPS 的引用，独立预期为：main.o 的修复会使 helper.o 也新增 config.h 声明，但 helper.o 的真实依赖仍只有 helper.c，因而增加冗余边。记录影响而不擅自重写变量隔离算法，代价是现有实现仍可能扩大跨目标作用范围。隐式规则与复杂 Make 不在本次支持和验证范围。

验证：最终 OUT work/e9-B-manual.q5PRlA 的 5 份步骤日志均退出 0；shared-variable 保存输入、补丁、计划和重检。第一次扩展验证因副本无初始提交而失败，保留在 work/e9-B-manual.r4FGb0，换新 OUT 完整重做。原 7 项、E8 的 1 项及 E9 的 2 项共 10 项测试通过，日志 work/unit-tests-20261104-130600.log。只修改 test_profile.py，核心 lab.py 不变。个人 PR 等待验收，不执行合并。

## E10：独立副本验证，全部检查通过才写回

背景：补丁能应用或首次能构建，都不足以说明缺失依赖已经修复。沿用课程 validate() 在独立 sandbox 验证 patch_applies、build、test、header_change、no_missing；只有全部为 true 且无 error 才写回源 Makefile。错误测试和坏补丁拒绝时保留源字节；第三次拒绝保护的是第二次已经接受的版本。

自主任务：第一项采用 08 的编译失败例子；第二项加入 helper.c/extra.h，故意只修 main.o/config.h。预期后者虽然能构建、运行及通过 config.h 变化检查，仍因剩余 MD 被拒绝。这个输入区分了“构建成功”和“依赖补齐”，没有修改核心算法或扩大 Make 支持范围。

代价与边界：每次复制项目并重新构建有额外开销，但能保留输入、失败现场和字节对照。构建失败时 build.log 未写出，具体编译输出由 validation.json 的 error 与步骤日志保留；不伪造缺失的成功日志。允许保留 unused.h 的冗余依赖。动态重检是教学 BuildChecker 在当前配置的真实跟踪结果，不外推为所有配置正确。

证据：参考 OUT work/e10-B-manual.ISSE3G 的 7 步退出 0；最终 OUT work/e10-B-manual.SWEYkN 的 9 步退出 0，三行 results.csv 与 gate.json 通过，BuildChecker 无 MISSING，两项个人扩展均按预期拒绝且源字节保持。work/unit-tests-20261104-132904.log 中共 12 项测试通过。个人分支提交更新已有 PR #3，等待验收，不合并。
