# 原生可编辑机制图（2026-11-06）

对应三页：运动方向、拓扑与空间位置冲突、选择性放松。映射图不包含在内。

正式 PPT：[图4–6](../../../最新论文与三张PPT/Fig4-6_方向_冲突_放松.pptx)。三页分别含 398、136、85 个原生形状，无图片、无图片填充。标签为 Times New Roman 斜体文本框；曲线为可编辑的 PowerPoint 自由曲线；圆点、菱形、区间、箭头和填充区域均为原生形状。可在 PowerPoint 的选择窗格按英文语义名称选择对象，自由曲线可通过“编辑顶点”修改。

参考源为 `../open_mechanisms_20261106/01_direction.png`、`02_conflict.png`、`03_relaxation.png` 的当前白底版本。保持原图布局、关系、节点位置及颜色，微细栅格纹理改用平滑原生填充，字体渲染和个别曲线细节不保证逐像素相同。正文配图 PDF 仍使用已批准的原图，本次不更改论文排版。

`extract_geometry.py` 从方向图识别等高线中心线，拟合为三次贝塞尔曲线；场的淡色区域分解为可编辑轮廓区域。该脚本仅导出几何 JSON，不生成图片。`direction_geometry.json` 为重建数据。`build.mjs` 以 Artifact Tool 创建全部原生对象，导出、渲染并验证 PPT。

重建时设置 `RUNTIME_NODE_MODULES`、`PRESENTATIONS_SKILL_DIR`、`RUNTIME_PYTHON`，并用 `ANCHORMTM_FIGURE_OUTPUT_DIR` 指向新的输出目录后运行 `build.mjs`。几何 JSON 已保留，无需每次重新提取。

PPT 在两套渲染器中逐页检查。包审计确认媒体目录为空、三页均无 `p:pic` 或 `a:blip`。检查记录及旧贴图版备份保留在 `output/native_mechanisms_20261106/.build/`。


最新同步：三图说明文字统一为Times New Roman正体、32 px；数学标签保留斜体。第二图AB/CD根节点等高，第三图圈出放松节点。正式PPT共632个原生对象，正文图4–6现使用该PPT经办公软件渲染的3072×2048截图，替代上一版图面。
