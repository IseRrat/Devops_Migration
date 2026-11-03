# tinygrad 项目 E2/E3 检查（2026-10-10）

按用户最新要求，主项目确定为当前 featureB 中的 tinygrad。版本字段、缺陷与个人信息仅依据现有文件记录；不能确认的内容留空。

## 项目与分工

`pyproject.toml` 的项目名为 `tinygrad`，声明版本为 `0.14.0`，构建后端为 `setuptools.build_meta`。包版本不是源码完整 SHA，也不能据此推断上游 tag。当前导出的文件夹没有可用 Git 历史，不能确定这份源码的完整提交。

B1 的 `Dockerfile` 从当前源码生成 wheel、在最终镜像安装 wheel，预期断网运行输出 `tinygrad-ok`。B2 的现有固定 MD 报告、Makefile 和参考 Patch 属于独立 C/GNU Make 基线。B3 维护契约与验收入口。课程 E3 第 7 页允许论文项目或自行选择的项目，第 9 页要求 B 组提交 DRAFT 项目与功能验证条件、固定 MD 报告及修复样本，并未要求两者必须是同一项目。

上述“未明确要求同一项目”只是对现有课件文字的判断，不代表独立样例已获本组或教师认可。最终是否要求 B2 使用 tinygrad 本体样例尚未确认，不据此宣称验收完成。

如果组内另要求 B2 直接修复主项目，应先确认 tinygrad 中适用的真实缺失依赖。当前 Python/setuptools 包构建不自动等同于 MDFixer 的 Makefile prerequisite 修复；根目录 Makefile 主要编排 E4 环境，也不能直接认定其中存在项目 MD。

## 按课程交付核对

| 责任 | 要求 | 当前材料 | 状态 |
|---|---|---|---|
| B1 E2 | DRAFT 接口、构建/验证命令、Dockerfile/image 输出格式 | `DRAFT_INTERFACE.md`、`OUTPUT_FORMAT.md`、相关 Schema/样例、`BUILD_AND_VERIFY.md` | 定义已具备 |
| B1 E3 | 项目、失败/参考成功候选、构建和功能验证 | tinygrad 源码与 Dockerfile；Tiny Greeting 失败/成功夹具及历史 Docker 日志 | 主项目材料已具备；当前 tinygrad Docker 成功日志尚缺 |
| B2 E2 | REPAIR 接口、MD 输入、Patch/repair report 输出格式 | `REPAIR_INTERFACE.md`、三份 Schema、有效/无效样例 | 定义已具备，示例 URI/哈希不是实际产物 |
| B2 E3 | 固定 MD、对应 Makefile、reference patch、修复前后验证 | `e3/mdfixer/`；验证脚本可归档实例化报告、补丁、快照和逐步输出 | 独立课程基线已具备；使用新目录保存本次详细证据 |
| B3 E2 | 公共契约、ADR、AI_USAGE、Backlog、无效样例 | 公共 Job/artifact Schema、交接映射、文档、25 个样例 | 材料已具备；Backlog 已补 B2 任务，个人负责人未确认 |
| B3 E3 | 验证入口、README、失败/拒绝样例和 evidence | `validate_b3.py`、`e3/`、CI 配置与证据目录 | 现有基线可验证；通过不等于主项目容器/自动修复通过 |

E2 不要求部署 API。工具自动生成/修复和跨组真实联调属于后续阶段，不能将这些实现一并当作 E2/E3 缺项。

## 证据与待补内容

1. 当前 tinygrad Dockerfile 尚缺对应源码版本的成功 build 日志、镜像 ID 和断网 verify 日志。历史 Tiny Greeting 容器证据不能替代它；已有阻塞说明见 `e3/EVIDENCE.md`。
2. `e3/evidence/local-20261010-175005/environment.txt` 保存了系统和工具版本，但 Git 查询报 `not a git repository`，所以主项目完整 SHA 未记录。日志中的 MDFixer `source_commit` 仅属于临时样例仓库。
3. 旧 MDFixer 日志仅是断言摘要。当前脚本新增 `--evidence-dir`，可以在新运行中保存每步原始输出、实例化报告、补丁和文件快照；不将新证据冒充旧运行记录。
4. 未找到 B2 个人贡献记录；B1/B3 记录不能代替 B2 本人的作者和提交证据。
5. `E2_BACKLOG.md` 已补 B2 E2/E3 任务、责任角色和验收条件，具体个人负责人留空。需要全组交付清单时，仍需补 B1 任务及确认各具体负责人。

## 未确认字段

空白表示没有可核实的值，不代表不存在缺陷或已经完成。

| 字段 | 确认值 |
|---|---|
| 主项目名称 | tinygrad |
| 当前 `pyproject.toml` 声明版本 | 0.14.0 |
| 当前源码完整 commit SHA | |
| 当前源码对应上游 tag | |
| tinygrad 本体已确认的 MD target / dependency / 位置 / 依据 | |
| tinygrad 本体 reference patch | |
| tinygrad 本体修复前后实际结果 | |
| B2 姓名、账号及个人提交 | |
| 独立 GNU Make 基线是否获认可作为本组最终 E3 交付 | |

本次删除此前添加的另一项目采集脚本、模板和待办文档，仅按 tinygrad 与现有课程基线记录交付。没有自行选择新缺陷、硬编码主项目修复结论或伪造实验结果。

## B2 详细证据补齐结果

2026-10-10 使用更新后的总入口加 `--require-toolchain --evidence-dir` 实际运行，四项退出码均为 0，`failures` 为空。记录位于 [local-b2-20261010-182634](e3/evidence/local-b2-20261010-182634/summary.json)，B2 详细产物位于该目录的 `mdfixer/`。实例化报告 SHA 与实际临时样例仓库一致，原始命令输出、无效候选失败原因、五份阶段快照及实际 Makefile diff 已归档。

新增采集测试两项通过，覆盖失败命令在异常前归档及实际样例产物。此次补齐的是独立 GNU Make 基线的详细证据，不是 tinygrad 本体的 MD 修复或 Docker 构建。主项目版本和 B2 作者归属仍未确认。

## 真实性复核与撤回说明

按用户要求再次核对新增代码与证据：32 条 stdout/stderr 文件与命令记录一致；程序实际输出序列为 `1、1、2、3、1`；唯一非零退出码是无效候选 `make` 的 2。从初始源码快照和原脚本的固定 Git 元数据重新创建样例仓库，得到相同 SHA `97db8f5ddb86f2783f4dcc13e45ac956c9732055`。未发现新增运行结果或 SHA 被编造，因此保留采集代码及实际证据。

撤回此前 README 中“满足 E3 要求”的确定性表述，改为“样例具有课件所列材料，但最终交付认可未确认”。这属于未获确认的验收判断，不能当作已经完成课程验收。

原脚本固定 Git 作者、占位邮箱和 2026-09-28 日期是人工样例元数据，用于重复生成临时 SHA，不是真实贡献身份或运行时间；本次没有新增这些固定值，也没有把它们归属给 B2。固定 MD 与参考 Patch 沿用已有人工样例，不是 tinygrad 真实缺陷或工具自动修复。报告来源标签沿用模板，不代表教师认证本次提交。旧日志保持原样，仅补充说明，不伪改为新时间或真实个人信息。

## 位置字段与 Backlog 补齐

依据样例实际文件补 `location.source`（`main.c` 第 2 行）与 `location.declaration`（Makefile 第 6 行），同时保存原行文本。验证脚本及测试检查位置与源码一致，不通过猜测推导 tinygrad 位置。

新增 B2 Backlog 的责任角色来自分工，具体个人负责人未确认而留空。历史贡献仍按已有记录归属，不将公共接口或原始夹具重新归属给 B2。

本次两个采集测试通过，总入口四项检查全部退出码为 0。新报告及原始快照位于 [local-b2-location-20261010-183750](e3/evidence/local-b2-location-20261010-183750/summary.json)，位置字段与归档初始源码逐行一致。旧报告没有改写。未能填写的仍为个人身份、负责人及个人提交 SHA，tinygrad 本体缺陷和最终交付认可也仍未确认。
