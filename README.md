# Seedance 2.5 Prompt Reviewer

面向 Codex 的 Seedance 2.5 现有提示词优化与一致性质检 Skill。它的目标是修好用户已经写好的提示词，而不是把剧情、台词、角色或时长重新创作成另一套方案。

## 适用场景

- 优化现有 Seedance 2.5 视频提示词；
- 执行“只改画面，其他内容保持不变”等最小差异修改；
- 检查人物、服装、道具、时间段、空间方向和动作端点的连续性；
- 在存在真实风险时，检查说话者画面主体、口型、越肩、反打、OS/VO 与 180 度轴线。

这不是从零生成视频创意的万能模板，也不会把 Seedance 2.0 的时长、素材数量、模型 ID、API 字段或平台能力直接套用到 2.5。

## 核心行为

- 锁定用户未授权修改的剧情、台词、角色标签、服装、道具、时间戳、总时长和素材引用。
- 默认返回一份完整、可直接复制的替换稿，而不是只给局部补丁。
- 19 秒、22 秒、30 秒等 2.5 提示词不会因旧的 15 秒边界被机械拆分。
- 对白站位模块按风险条件加载；纯动作、单人独白、旁白、产品或风景镜头不会被强制改成正反打。
- 输出区分“确定冲突”“需要人工判断”“未触发此检查器”和“通过”。

## 安装

在 Codex 中发送：

> 请使用 `skill-installer` 从 `https://github.com/Aki-Jan31/seedance-25-prompt-reviewer` 安装 `seedance-25-prompt-reviewer`。

安装后开启新对话，Codex 即可通过 Skill 名称或其描述自动发现它。

## 调用示例

```text
请使用 $seedance-25-prompt-reviewer 优化下面的 Seedance 2.5 提示词。
只修改人物浮空的画面描述，剧情、台词、角色标签、时间戳和总时长逐字保持不变，返回完整提示词。
```

```text
请使用 $seedance-25-prompt-reviewer 检查这段双人对话的说话者、口型、越肩反打、左右位置和 180 度轴线，先报告问题，不要改写。
```

## 验证

项目包含结构检查、最小差异回归测试、纯动作误触发测试，以及 Raven/Draven 对白站位行为验收案例。

```bash
python3 -m unittest discover -s tests -v
```

这些验证只能证明 Skill 结构和明确的提示词内部约束正确；实际生成效果、口型精度、身份保真和平台功能仍需通过当前 Seedance 2.5 界面或实际视频验证。

## 来源与许可

本 Skill 是面向“优化现有提示词”的原创适配，没有原样复制任一上游仓库。其决策规则参考了：

- [Emily2040/seedance-2.0](https://github.com/Emily2040/seedance-2.0)：导演、镜头、动作、连续性、anti-slop 和返修方法。
- [ye4wzp/seedance2.5-prompt-skill](https://github.com/ye4wzp/seedance2.5-prompt-skill)：Seedance 2.5 版本路由、长时段组织和证据等级边界。

详细来源、审阅版本和未验证边界见 [`references/source-notes.md`](references/source-notes.md)。本项目按 [MIT License](LICENSE) 许可，并保留必要的上游版权声明。
