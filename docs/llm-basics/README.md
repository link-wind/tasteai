# TasteAI

从原理到实践，理解语言、多模态与生成式 AI。当前已发布十二节大模型基础课程；后续扩展多模态、Diffusion 等方向。

从 `index.html` 查看完整目录，基础知识十二个课目已全部发布（01～12），另有 `transformer-lm.html` 系列导读。目录中的系统工程与动手训练仍待编写。原六课 `lesson-01.html` 至 `lesson-06.html` 保留为旧版概览。

## 阅读与维护

本次已验证本地 HTTP 预览。仓库根目录运行以下命令，再访问 http://localhost:8766/docs/llm-basics/：

```sh
python3 -m http.server 8766 --bind 127.0.0.1
```

页面不依赖在线字体、远程脚本或接口；直接打开文件的离线浏览器验收受当前工具安全策略限制，尚未完成。不要将静态资源完整性检查等同于 file:// 实测。

- `catalog.json`：目录、原站链接、编写状态的唯一数据源。
- `content/*.html`：每节正文源文件。
- `reading.css`、`reading.js`：详细课程共享样式与第一节实验。
- `bpe.js`、`bpe-playground.js`：第二节算法内核与网页训练/编码实验。
- `foundation-math.js`、`foundations.js`：第三至十二课的本地数学与交互。
- `tokenizer-samples.js`、`engineering-counts.js`：配套脚本生成的实测快照，前者为 tiktoken 0.12.0 固定样本，后者为处理计数（不是时长）。
- `../../labs/04-foundations/README.md`：新增五个实验的运行方式、可选分词库和数值约定。
- `../../scripts/build_llm_course.py`：按已发布目录生成入口、章节页面、旧版提示；不会替换旧正文。
- `previews/`：浏览器验收截图，不参与页面运行。

修改正文或目录后从仓库根目录运行：

```sh
python3 scripts/build_llm_course.py
node --check docs/llm-basics/reading.js
.venv/bin/python -m unittest discover -s tests
```

编写状态与用户掌握状态分开；本次不修改 `.learn`。后续章节各自使用 OpenSpec change，只有完成正文并验证后才添加本地正文链接。

## 图解与交互

十二课各有一张原创概念图，Transformer LM 导读复用全景图。每张图附中文读图说明；“放大查看”打开大图，Escape 或关闭按钮退出并回到原按钮。手机上静态图自适应宽度，复杂交互图可在图框内横向滑动，正文不会整体横向滚动。无脚本时仍可阅读静态图、图注与正文。

- `figures/*.svg`：页面直接使用的本地矢量图。
- `figures/*.drawio`：BPE 局部更新、模型全景、Attention 流程三张结构图的可编辑源。
- `../../scripts/build_llm_figures.py`：生成字节边界、BPE 合并、预分词、共享权重、缓存窗口、位置波形、RoPE 平面、offset 与插值轴；同时生成三张 draw.io 源。
- `visual-explanations.js`：已有十二课实验的同步图形，使用现有数学、训练状态与固定实测样本，不请求外部接口。首课长输入图只显示前十二个码点，全部数据仍在原表格。
- `../../tests/test_course_visuals.py`：检查图形中的因果权重、RoPE 坐标/不变量、BPE 边界、字节、缓存与插值。

重建原生 SVG 和结构图源：

```sh
python3 scripts/build_llm_figures.py
```

如需同时重导出三张结构图 SVG，需安装 draw.io 桌面版（当前脚本使用 macOS 标准安装路径）：

```sh
python3 scripts/build_llm_figures.py --export-drawio
python3 scripts/build_llm_course.py
```

普通阅读和课程页面重建不要求 draw.io。图形原理参考 CookLLM 公开主题结构，自行设计与绘制；会员受限正文及未能访问的交互内容未复制。条形图、热力图、旋转平面和缓存时间线沿用各课注明的教学数据与适用边界。
