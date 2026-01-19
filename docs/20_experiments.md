# 20 Experiments

本节列出基础实验清单，用于对比 PBD / XPBD / VBD 的行为差异。

## 实验 1：dt sweep
- 目的：观察 $dt$ 对“硬度”和稳定性的影响
- 设置：固定 iterations 与 compliance（XPBD）
- 建议值：$dt = 1/30, 1/60, 1/120$
- 记录：最大约束残差、链条长度变化、肉眼观感

## 实验 2：iterations sweep
- 目的：观察迭代次数对残差收敛与硬度的影响
- 设置：固定 $dt$ 与 compliance
- 建议值：iterations = 5, 10, 20, 40
- 记录：最大约束残差曲线

## 实验 3：compliance sweep (XPBD)
- 目的：观察 compliance 对“软硬度”的控制
- 设置：固定 $dt$ 与 iterations
- 建议值：compliance = 0, 1e-6, 1e-4, 1e-2
- 记录：链条伸长量、残差

## 输出建议
- 日志：每秒输出残差与状态
- 截图/录屏：放在 outputs/ 目录
