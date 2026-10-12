---
name: museum-archaeology-notebook
description: Turn museum artifact photographs into restrained vintage archaeological notebook artwork while preserving the photographed object's shape, patterns, inscriptions, and spatial relationships. Use for bronze, jade, pottery, oracle bone, and stone artifact photos; not for landscapes, architecture, archaeological-site reconstruction, or video.
---

# 博物馆考古手记

把用户上传的单张博物馆文物照片制作成一张复古考古研究手记 PNG。默认直接完成，不要求用户逐步确认；只有用户明确提出“先讨论方案”时，才先给文字方案并等待确认。

## 不可妥协的真实性规则

- 把原始文物摄影视为事实层。不得重绘、替换或“优化”文物主体，不得改变器形、纹饰、铭文、裂纹、修复痕迹及重要空间关系。
- 最终画面中的真实照片区域必须由程序直接放置原图；不要让图像模型重新生成这一部分。默认完整容纳原图，只有确认不会裁掉文物主体时才可裁切。
- 铭文和复杂纹饰的研究局部优先直接裁取原照片。不得让图像模型发明或补齐看不清的文字、纹样或结构。
- 线稿可艺术化笔触，但轮廓和可见细节必须来自照片。无法确认时省略，不要猜测。
- 商代抽象动物纹饰不得解释或绘制成现代写实动物。
- 文物事实不确定时省略或明确标注“待考”，绝不把推测写成定论。

## 工作流程

1. 检查输入是否为单件或清晰主体的博物馆文物照片。本 Skill 适用于青铜器、玉器、陶器、甲骨、石刻等；不处理自然风光、城市、建筑、遗址空间复原或视频。
2. 检查照片内展签与用户文字。需要补充关键事实时，按 [fact-checking.md](references/fact-checking.md) 查询；无关紧要的信息不要无限搜索。
3. 分析器物长宽方向、整体轮廓、铭文/纹饰密度和照片留白，按 [design-language.md](references/design-language.md) 选择 3:4 竖版或 4:3 横版。不要机械套用固定模板。
4. 规划上方真实照片与下方研究手记。信息通常包括名称、年代、出土地点（可确认时）、一张整体线稿，以及一至两处真正有研究价值的局部；根据素材密度取舍。
5. 按 [image-workflow.md](references/image-workflow.md) 制作辅助素材。优先使用现有内置图像生成能力；不要未经用户同意切换到需要付费 API 或 API Key 的流程。
6. 使用 `scripts/compose_notebook.py` 或等价的确定性合成方法，把原图直接放入画布并以程序渲染中文。脚本缺少 Pillow 时说明依赖，不要假装已运行成功。
7. 输出一张 PNG。检查照片主体、中文、事实、比例和文件是否实际保存；不要主动生成多个候选版本。

## 版式与文案

- 常用结构是“上半部真实照片 + 下半部研究手记”，以克制的撕纸边缘衔接。
- 可少量使用旧纸纹理、胶带、装订孔、测绘线、箭头和局部框；装饰不能压过文物。
- 文案中文优先、简洁客观。不要加入诗句、心灵鸡汤、夸张叙事或营销口号。
- AI 生成的线稿只作辅助研究图，不得冒充正式考古测绘图。

## 完成前检查

- 原照片文件未被覆盖，最终照片区域来自原文件。
- 器形、铭文、纹饰、裂纹与修复痕迹没有被虚构或更改。
- 标题和事实有依据；不确定内容已省略或标注。
- 中文可读，输出为一张实际存在的 PNG。
- 若图像生成能力不可用，使用脚本的机械边缘线稿回退，并向用户说明视觉效果限制。
