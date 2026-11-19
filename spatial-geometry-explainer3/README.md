# Spatial Geometry Explainer · v2.1 General

通用几何与向量连续教学 Skill。目标是把**来源 → 运算 → 显示 → 连贯过渡 → 实际验收**落实为跨领域规范，不预存某一题目的计算过程、对象、变量命名或图形结果。

## 这一版本刻意不附带以前讨论过的专用实例

- 移除以前附带的专项示例页面、对应的推导文档和数值回归。
- **只保留通用操作模板**：矢量分解、坐标变换、真实角边、步骤衔接、3D 交互和视觉核查。
- 安装包仍有若干**不同领域的普适示例**，例如二维向量正交投影、斜面力、电场与机械臂。它们只说明可复用算法，不提供你未来测试题目的现成答案。
- 本版本适合另一段独立对话中的**迁移能力测试**。建议在新对话只上传这个包和同一题目，不粘贴之前课件或修复历程。

## 安装或调用

ZIP 中含完整目录 `spatial-geometry-explainer/`。支持自定义 Skill 的工具可安装 ZIP，或将完整目录解压到 Skill 搜索路径；具体依宿主工具而定。

**上传 ZIP 不等于自动安装或执行。** 开始任务前应检查当前助手是否真实读取 `SKILL.md` 和任务相关 references。不能只看文件名。

通用 3D HTML 至少读取：

- `references/continuity-protocol.md`
- `references/angle-evidence.md`（任务涉及真实几何角时）
- `references/quality-checks.md`
- `references/verification-workflow.md`
- `references/camera-controls.md`（涉及相机视角时）

## 规范升级要点

1. **加载真实性**：写明实际阅读的文件，避免声称执行了未读取的 Skill。
2. **真实角的证据**：顶点、两条方向射线、测角平面、圆弧、角值、锚点必须一致。
3. **任意步骤交接**：每对 `i → i+1` 声明 retained / introduced / source / operation，不硬编码具体编号。
4. **同源数据**：公式、几何和动画由同一状态计算。
5. **浏览器验收**：桌面/移动，关键帧、旋转与触摸、零值/反号；视觉阅读和代码通过分开报告。
6. **跨任务适配**：角不是所有任务必需；复制输入和推导、变换、合成等来源关系也不是一回事。

## 不需额外依赖的检查

在 Skill 根目录执行：

```bash
python scripts/verify_skill_package.py
python scripts/validate_continuity.py assets/example-vector-storyboard.json
python scripts/validate_visual_contract.py assets/example-visual-contract.json
python scripts/check_vector_math.py
python scripts/test_visual_contract_failures.py
```

严格人工审核模式（示例尚未人工审核，预期 FAIL）：

```bash
python scripts/validate_visual_contract.py assets/example-visual-contract.json --require-reviewed
```

## 截图验收工具

可选 Playwright + Chromium。页面需自行提供下面的测试钩子（不是自动存在）：

```javascript
window.lessonTest = {
  setStep(stepNumber) { /* update internal state from 1-based UI step */ },
  setPhase(fraction) { /* update transition fraction 0..1 */ },
  setView(viewName) { /* optional camera preset */ },
  getEvidence() { /* optional JSON geometry state */ }
};
```

之后可运行：

```bash
python scripts/capture_lesson_frames.py page.html --stages 2,3 --views default --out frames
```

脚本可以抓取真实浏览器关键帧；**截图生成成功不等于学生能认清图中的角与步骤来源**。需要实际检查画面和 G4 学生阅读测试。

## 如何评价迁移能力

- 在独立对话里给相同题目、相同参数、相同附件、相同生成要求。
- 预先约定评分点，例如：几何正确、角的可辨认性、每步来源、交互操控、视觉遮挡。
- 先验收一次输出，不在测试过程中把旧答案或修复指导发给新的助手，否则无法区分零样本泛化和迭代后的修正。
- 比较版本前后时尽量只改变 Skill，本题环境、模型、工具权限仍可能影响结论。

参见 `SKILL.md`、`references/verification-workflow.md` 和 `CHANGELOG.md`。
