# B组CI与合并门禁

目标：每次提交自动构建和测试，失败阻止普通合并，修复后恢复通过。课程原题使用GitHub；当前项目仍使用学校GitLab，平台等效是否获课程认可待教师确认，不新建外部仓库或改远程。

## 当前GitLab入口

根`.gitlab-ci.yml`只包含`e7_b_quality_gate`，shell Runner标签为`e7-b-shell`。工作目录为`$CI_PROJECT_DIR/labs/B-draft`，artifact为`labs/B-draft/work/ci-e7-*/`，保留14天并在失败时上传。该分支已移除E2–E4/B3作业，不再要求docker-lab Runner。

Runner需要本机Docker socket和相同绝对路径的bind mount访问权限。脚本保存触发SHA、候选哈希、源码/历史扫描、服务构建和完整测试、镜像扫描、工具链、完整gate。新目录布局提交后必须实跑CI；历史Job688402不能替代新提交验证。

## 门禁演示顺序

1. 正常E7 CI通过，保存SHA、pipeline/job URL、完整trace及artifact。
2. 确认实际目标分支，启用保护、禁止直接push/force push、要求成功流水线。
3. 演示分支复制`ci/rejection-demo/B/test_ci_reject_demo.py`至`labs/B-draft/services/draft/tests/`，创建MR；断言version实际0、预期1导致CI失败。
4. 用有普通合并权限且无绕过权限的账号验证合并被拒绝，保留保护设置、失败日志、MR状态和拒绝时间/截图。
5. 保存拒绝证据后，在同一MR复制`ci/rejection-demo/B/fixed/test_ci_reject_demo.py`恢复预期0；最新SHA的CI通过后正常合并，保存merge SHA和时间。

精确手动命令见 [E7执行与门禁](../labs/B-draft/docs/E7_执行与门禁_231880168.md)。root模板CSV记录正常/失败/恢复与合并状态。不要将Runner故障或账号无合并权限当作预期拒绝证明。

## GitHub教材（当前不启用）

`ci/github/e7-quality-gate.yml`是B轨道参考workflow，工作目录同样为labs/B-draft；保护配置为`ci/B-main-protection.json`。仅在本人明确选择GitHub时复制至仓库根.github/workflows并按真实App ID配置必需检查`e7-b-quality-gate`。当前学校GitLab不执行此文件，也不据它宣称GitHub验收完成。
