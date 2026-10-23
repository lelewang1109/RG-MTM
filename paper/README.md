# 当前完整论文与图件

当前编辑入口只有这一套完整稿：正文19页、14图，附录48页、18图。以用户指定的修改前版本为基准，图1—4保持原样，已合并前一扩展稿中的有效补充分析。PM2.5使用完整2000年366场和污染配色；全年结果替换主表，一月只作为历史探索控制。新增图13给出PM2.5全年总览、源场与局部追踪案例；原参数图顺延为图14。

| 入口 | 内容 |
|---|---|
| [正文](manuscript/Revised_RG-MTM.pdf) / [附录](manuscript/Revised_Supplement.pdf) | 当前完整PDF |
| [main.tex](manuscript/latex/main.tex) / [supplement.tex](manuscript/latex/supplement.tex) | 当前编辑源文件 |
| [源码包](https://github.com/lelewang1109/RG-MTM/releases/tag/research-2026-10-23) | 可独立编译的投稿源包 |
| [正文14图PPT](figures_ppt/All_Figures.pptx) / [附录18图PPT](figures_ppt/All_Supplementary_Figures.pptx) | 每页对应一幅论文图，单图母版用于编辑 |
| [修改前版本](修改前版本_20261023/README.md) | 用户要求保留的原14页正文、46页附录及源码 |
| [材料索引](../docs/正文与附录材料索引.md) / [图号索引](FIGURE_INDEX.json) | 九数据与当前图件对应 |
| [修订记录](OLD_BASE_REVISION.md) / [颜色与显示规则](COLOR_AND_DISPLAY_POLICY.md) | 本轮更改与证据边界 |

九数据使用共同的评价定义，并连续列在结果表中；不在Nucleon/Benzene前另设分隔线。当前全年PM2.5的参考顺序改善不等于运动改善：P42/95错误，R20 47/95错误。原科学数组与历史一月记录保留，显示插值不增加科学样本。

图7现用数据提供的10 km FRP网格真实边界，增加澳大利亚州界、海岸线、经纬度及200 km比例尺。17—19帧的实际记录与原有平滑分析场分上下两排，同一组A/B/C对应。实际记录保持稀疏，不据此推断连续火场；原P/R锚点、剖面和连接数值保持，时序背景改为保守显示插值。复现入口为scripts/prepare_wildfire_geographic.py，独立核对为scripts/verify_wildfire_geographic.py。

维护时先编辑单图PPT，再运行定向export和两个sync_catalog脚本。code/tools/build_submission20261023.py生成共同表，--check检查当前数值；全年入口为code/tools/run_pm25_annual.py及export_pm25_annual.py。最后编译、检查PDF、package_delivery并运行verify_comprehensive_revision。所有私有中间文件位于.build，当前交付清单为DELIVERY_MANIFEST.json。

图7、10、11及附录S10/S17/S18已统一改进时序显示，减轻逐帧方块边界；所有原帧中心像素列保持其原剖面的面积积分。Cylinder局部源场采用双线性显示，保留原网格中心值；真实FRP单元不插值。详见evidence/temporal_display20261023/README.md及checks/temporal_display20261023/numerical.json。
