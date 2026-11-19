# 交付门槛：确实加载 → 几何正确 → 连贯可见 → 真实验收

**代码通过 ≠ 画面正确 ≠ 教学有效。** 每个门槛必须独立给出状态；不能把一个自动化 PASS 推断为所有 PASS。适用于数学、机械、场论、数据过程等不同任务，不预设学科公式或步骤数。

## G0：证实本次真正读取了 Skill

- 用户提供 ZIP 时，先检查存档安全并解包，真正读取 `SKILL.md` 和任务相关 references。
- 只列出文件名、查看 ZIP 是否存在，或复述历史对话，**不等于执行 Skill**。
- 记录 `loadedFiles[]`（实际打开的文件）与 `appliedRules[]`（所采用的具体规则）。无法读取就说明不能确认，不捏造。
- 交互式 2D/3D 任务优先读取 `continuity-protocol.md`、`quality-checks.md`、`angle-evidence.md`；若涉及相机，另读 `camera-controls.md`。

## G1：独立定义和验证几何

- 写明每个量的来源、单位、局部/世界参考系、符号正方向、操作与有效范围；渲染和公式都使用同一数据源。
- 对每个实际需要的角，用 `angle-evidence.md` 建角度身份证：共同顶点、两条真实参考射线、平面、弧线。
- 独立数值计算检验正交、重构、点积、反号、零值和边界；若模型含奇异点需显示适用范围。
- 物理响应若超出几何运算，必须声明额外方程和假设；不能从投影直接跳到未知的物理预测。

## G2：每一对相邻步骤都要有可见交接

为所有步骤对 `i → i+1` 建表：

| 字段 | 应回答的问题 |
|---|---|
| `fromStep`, `toStep` | UI 可见编号是否连续，内部索引是否对应正确 |
| `retained` | 前一步哪些 ID 仍在**画面中实际可认** |
| `introduced` | 新出现的哪些 ID 原来不可见 |
| `source` | 新内容来自哪个输入量、旧对象或模型状态 |
| `operation` | 具体是分解、投影、复制、旋转、合成或其他操作 |
| `frames` | 0 / 25 / 50 / 75 / 100% 时如何接续 |
| `visualProof` | 不看说明能否指出哪些原样留下、哪些正在生成 |

- “保留在讲解文字里”不算“保留在场景中”。需要实际保留原位图形或提供清楚可追踪的过渡。
- 原对象若必须淡化，仍应保留 ID、来源和方向；不能把第一对象删掉并突然换到第二对象。
- 若是复制同一输入，复制过程必须保持不变量（矢量方向、模长、数据身份等）。若是物理旋转或坐标换基，应明确其各自变化规则。
- 可见标题从 1 开始、内部 stage 从 0 开始时，要求 UI 第 `i` 步恰为 `stage===i-1`；不要硬编码某一对步骤编号。

## G3：真实浏览器与交互检查

- 视口：桌面约 `1280×800`、移动约 `390×844`；还要检查用户指定尺寸。
- 步骤：每一步开始与结束；有交接的相邻步骤成对截图。
- 关键帧：每个关键过渡 `0%、25%、50%、75%、100%`；顺拖与倒拖都要检查。
- 摄像机：初始、俯视、侧视、自由旋转、复位；物体身份/角度数值不应随摄像机改变。
- 操作：鼠标横向/纵向拖动方向、触屏移动、缩放范围、旋转极点与复位；控件必须驱动实际状态。
- 参数：默认、零值、反号、等值/对称、边界等由**当前题目语义**决定，不预填任何领域特定数值。
- 可访问性：非仅颜色编码、键盘基本可用、减少动画时可逐帧检查。

可使用 `scripts/capture_lesson_frames.py` 录屏式截取关键帧；该脚本**要求页面提供 `window.lessonTest` 接口**，不应假装任何网页开箱支持。自动化浏览器没报错不能证明视觉可读。

## G4：不看说明的学生阅读测试

审核者仅凭实际画面能：

1. 指出源输入、它的物理或数学身份、单位与坐标系；
2. 指出每个关键角的顶点、两条边、测角平面及真实值；
3. 说出当前新的量从哪一个旧量、经过什么运算得到；
4. 看相邻两步的截图，说出保留了什么、出现了什么、为什么；
5. 预测零值/反向/边界的变化，再用交互控件验证。

人工复核未执行就写 `NOT RUN`，不能仅凭标签存在或工具返回 PASS 宣称通过。

## G5：交付证据

```text
Skill actually loaded: YES / NO (实际文件路径)
Geometry/numerics: PASS | FAIL | NOT RUN
Step handoffs: PASS | FAIL | NOT RUN
Browser/viewport/keyframes: PASS | FAIL | NOT RUN
Human reading without prose: PASS | FAIL | NOT RUN
Known limitations: ...
```

- `scripts/validate_visual_contract.py` 只验证**规格结构**；严格模式也需要真实截图证据与审核者备注。
- `scripts/validate_continuity.py` 只验证来源图结构；不证明绘图质量。
- 没进行浏览器或人工测试，不可将状态写成 PASS。
- 缺乏支持某个场景的数学/物理依据时，应如实写假设或限定适用范围，不能由 Skill 的通用模板代替推导。

## 对本 Skill 包的自检

```bash
python scripts/verify_skill_package.py
python scripts/validate_continuity.py assets/example-vector-storyboard.json
python scripts/validate_visual_contract.py assets/example-visual-contract.json
python scripts/check_vector_math.py
```

包的通过只证明**本 Skill 与工具文件**通过这些静态/数值检查，不证明它未来生成的某个具体交互课件已经符合 G3/G4。
