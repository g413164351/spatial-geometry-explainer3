# 让数学运算真正可见：五种过渡模板

下列模式是**领域无关的绘制动作**。用户要求 HTML 时，将它们具体实现成一个共用状态机和屏幕空间布局，切勿只在旁白中说“已投影”。

## A. 从原量定义到参考角

- A0：一根原量蓝色 `v`，起点 `O`，终点 `O+v`，图上能读出物理解释与单位。
- A1：原箭头不动。画出参考方向 `e`、测角平面和连接两条射线的角弧 `θ`。
- A2：用颜色提示将要分解到哪个方向。先出现 `θ`，后出现 `sin θ`，不会出现公式后补找角。
- 验证：相机转动只改变屏幕角度，不改变物理 `θ`；角弧处于正确平面。

## B. 分解三角形（禁止跳边）

给定同一平面内的 `v`、单位目标方向 `e`：

```js
const vAlong = mul(e, dot(v,e));
const vAcross = sub(v,vAlong);
const O = anchor;
const A = add(O,vAlong);
const B = add(O,v);
// Draw O->B (blue), O->A (green), A->B (orange)
// Mark right angle at A; label the two legs and theta.
```

动画：先出现 O→B 与 θ；生长 O→A；再从 A 生长 A→B，补直角方框；最后高亮 `|vAlong|=|v|cosθ`、`|vAcross|=|v|sinθ`。若投影为负，保留箭头符号，不能把长度 `|v|sinθ` 当有符号标量。

## C. 从分解端点复制到多个对象（最常漏掉）

```js
const sourceV = computed.fromStep3; // exactly the earlier resulting vector
const keep = { id: sourceV.id, components: sourceV.components,
               unit: sourceV.unit, frame: sourceV.frame };
function copyAt(target, t) {
  const tail = mix(sourceV.anchor, target.anchor, smooth(t));
  const tip = add(tail, sourceV.components);
  return { ...keep, tail, tip };
}
```

- 三步动作：保留原位置半透明箭头 → 用两条虚线轨迹把**同一方向、同一长度**的副本送往目标 A 和目标 B → 到位后高亮各自目标局部轴。
- 两边的副本都用 `sourceV.components`，仅 `anchor` 不同。进入下步后可以降低原位置透明度，但不突然删除来源线索。
- 如果是来自另一坐标系的分量，先展示坐标轴变换，并完成数值变换，再开始平移。不能把“换坐标表示”误画成“物理箭头转向”。

## D. 目标 A 的投影保留，再逐渐加入目标 B 的投影

对局部单位法线 `n_A` 和 `n_B`：

```js
function splitAt(v, n, origin) {
  const normal = mul(n, dot(v,n));
  const tangent = sub(v,normal);
  return {normal, tangent,
    O:origin, A:add(origin,tangent), B:add(origin,v)};
}
// At each target, draw O->B (orange original), O->A (teal tangent),
// A->B (purple normal). The endpoint of tangent+normal must equal B.
```

- 显示箭头的完整方向和**沿面/法向直角**，不能只画一根脱离原橙箭头的紫色符号箭头。
- 投影可以在小倍率窗口展示，窗口必须用引出线连接到对象原位。完整主对象留在上半场，局部窗口在下半场，别让主体边缘或测点跑出边界。
- 先计算 `v·n` 的正负号，并显示有向法线；`v·n<0` 时紫色箭头向单位法线相反方向。对第二目标使用它自己的法线。
- 局部结果只表示**被投影的那个输入分量的贡献**，不要暗示是总物理结果；若还有竖直基础项等，需要再安排合成阶段。

## E. 从贡献到总结果

- 将多次来源分量的法向贡献在各局部轴上首尾相接，显示合成结果。
- 公式按项高亮：点击 `sinθ` → 回到有真实角边的三角形；点击投影项 → 高亮局部轴；点击正负号 → 显示带符号点积与参考方向。
- 区分：几何有符号投影、局部方向角、物理响应（力矩、加速度、运动）不是同一量。只有应用模型和假设写清楚后才继续下游。

## 进度条与状态实现

使用统一 `state = {stage, progress, params, camera, viewOptions}`，每帧根据 `progress ∈ [0,1]` 重新计算，不用累积位移使其失真。提供暂停、重播、手动拖动、倒回、零值与反向实验；每个节点的上下游高亮一致。`prefers-reduced-motion` 开启时禁用自动播放，但允许静态逐帧拖动。

如果用户说“步骤之间没有联系”，优先补 **C：可见复制平移**，随后补 **D：和来源相连的局部放大分解**，而不是额外增加文字或随机新视角。
