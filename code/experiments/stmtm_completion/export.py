"""Publish the completed nine-input evaluation; keep historical runs immutable."""
from pathlib import Path
import csv
import io
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from run import OUT, CONFIG, read, dump, sha
PAPER = ROOT.parent/'paper/manuscript/latex'
ORDER = ['Storms','Wildfires','OLR','PM2.5','Ring','Nucleon','Benzene','Tangaroa','Cylinder']
METHODS = ['TMTM','ST-MTM','RG-MTM-P','RG-MTM-R']


def geometry_table(data,dimension):
    lines = [r'\begin{table*}[t]',
        rf'\caption{{ST-MTM geometry metrics on {dimension}-D inputs. Lower SNS and TD and higher TW are better.}}\label{{tab:geometry{dimension}d}}',
        r'\centering\scriptsize\setlength{\tabcolsep}{3pt}',r'\begin{tabular}{lrrrrrrrrrrrr}\toprule',
        r' & \multicolumn{3}{c}{TMTM} & \multicolumn{3}{c}{ST-MTM} & \multicolumn{3}{c}{RG-MTM-P} & \multicolumn{3}{c}{RG-MTM-R20}\\',
        r'Data & SNS & TW$_1$ & TD & SNS & TW$_1$ & TD & SNS & TW$_1$ & TD & SNS & TW$_1$ & TD\\\midrule']
    for d in data:
        if d['dimension'] != dimension: continue
        row = [d['name']]
        for method in METHODS:
            m = d['geometry'][method]
            row += ['--' if m.get(k) is None else f'{m[k]:.4f}' for k in ['SNS','TW1','TD']]
        lines.append(' & '.join(row)+r'\\')
    lines += [r'\bottomrule\end{tabular}',
        r'\par\smallskip{\footnotesize\raggedright SNS uses source support-centroid distances; TW uses the common $k=1$ and only frames with more than two features. TD sums matched displacements in full-canvas units, with one fixed mapping per sequence. -- denotes static data with no temporal TD; Benzene section displacement is reported separately in the supplement. Eligible frame counts and complete precision are retained in Supplement S3.\par}',r'\end{table*}','']
    return '\n'.join(lines)


def grouped_comparison(data):
    """User-requested horizontal method groups, with all metrics in one float."""
    def number(value,precision=4):
        return '--' if value is None else f'{value:.{precision}f}'
    def primary(d,method):
        return d['methods']['RG-MTM-R20' if method=='RG-MTM-R' else method]
    def row(cells): return ' & '.join(cells)+r'\\'
    def table_start(columns):
        return (rf'\begin{{tabular*}}{{\textwidth}}{{@{{\extracolsep{{\fill}}}}{columns}@{{}}}}'
                +r'\noalign{\hrule height .8pt width \textwidth\vskip 2.5pt}')
    lines=[r'\begin{table*}[t]',
        r'\caption{Complete shared-input evaluation, grouped by method. All 2-D inputs precede the 3-D volumes in every panel.}\label{tab:tradeoff}',
        r'\centering\footnotesize\setlength{\tabcolsep}{2pt}',
        r'\textit{(a) Reference order, motion and merge-level cost}\par\smallskip',
        table_start('lrrrrrrrrrrr'),
        r' & & \multicolumn{2}{c}{TMTM} & \multicolumn{2}{c}{ST-MTM} & \multicolumn{2}{c}{RG-MTM-P (ours)} & \multicolumn{4}{c}{RG-MTM-R (ours)}\\',
        r'\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}\cmidrule(lr){9-12}',
        r'Data & $N_{\rm clear}$ & NROE$\downarrow$ & ME$\downarrow$ & NROE$\downarrow$ & ME$\downarrow$ & NROE$\downarrow$ & ME$\downarrow$ & NROE$\downarrow$ & ME$\downarrow$ & NMLE$_{\rm mean}\downarrow$ & NMLE$_{\rm max}\downarrow$\\\midrule']
    for d in data:
        event=primary(d,'RG-MTM-P').get('motion');precision=4 if d['name'] in ['Nucleon','Benzene'] else 2
        cells=[d['name'],str(event['clear']) if event else '--']
        for method in METHODS:
            m=primary(d,method);motion=m.get('motion')
            cells += [number(m['NROE'],precision),number(motion['error_fraction'],3) if motion else '--']
        r=primary(d,'RG-MTM-R')
        cells += [number(r[k],precision) for k in ['NMLE_mean','NMLE_max']]
        lines.append(row(cells))
    lines += [r'\bottomrule\end{tabular*}',r'\par\medskip',
        r'\textit{(b) Standard geometry and temporal stability}\par\smallskip',table_start('lrrrrrrrrrrrr'),
        r' & \multicolumn{3}{c}{TMTM} & \multicolumn{3}{c}{ST-MTM} & \multicolumn{3}{c}{RG-MTM-P (ours)} & \multicolumn{3}{c}{RG-MTM-R (ours)}\\',
        r'\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-10}\cmidrule(lr){11-13}',
        r'Data & SNS$\downarrow$ & TW$_1\uparrow$ & TD$\downarrow$ & SNS$\downarrow$ & TW$_1\uparrow$ & TD$\downarrow$ & SNS$\downarrow$ & TW$_1\uparrow$ & TD$\downarrow$ & SNS$\downarrow$ & TW$_1\uparrow$ & TD$\downarrow$\\\midrule']
    for d in data:
        lines.append(row([d['name'],*[number(d['geometry'][m].get(k)) for m in METHODS for k in ['SNS','TW1','TD']]]))
    lines += [r'\bottomrule\end{tabular*}',r'\par\medskip',
        r'\textit{(c) Continuous reference displacement and static-section coherence}\par\smallskip',table_start('lrrrrrrrr'),
        r' & TMTM & ST-MTM & \multicolumn{3}{c}{RG-MTM-P (ours)} & \multicolumn{3}{c}{RG-MTM-R (ours)}\\',
        r'\cmidrule(lr){2-2}\cmidrule(lr){3-3}\cmidrule(lr){4-6}\cmidrule(lr){7-9}',
        r'Data & SD$\downarrow$ & SD$\downarrow$ & $E_{\rm pool}\downarrow$ & $E_\infty\downarrow$ & SD$\downarrow$ & $E_{\rm pool}\downarrow$ & $E_\infty\downarrow$ & SD$\downarrow$\\\midrule']
    for d in data:
        cells=[d['name'],*[number(d['geometry'][m].get('section_displacement')) for m in METHODS[:2]]]
        for method in METHODS[2:]:
            m=primary(d,method);cells += [number(m.get(k),2) for k in ['E_pool','E_inf']]
            cells += [number(d['geometry'][method].get('section_displacement'))]
        lines.append(row(cells))
    lines += [r'\bottomrule\end{tabular*}',
        r'\par\smallskip{\footnotesize\raggedright NROE and continuous $E$ are percentages of reference extent; NMLE is a percentage of the fixed processed scalar range. ME is the error fraction over the shared $N_{\rm clear}$ events (lag 2; 2\% source-distance threshold). Cylinder retains its 2\%-of-full-canvas display threshold; other temporal inputs use the method-specific occupied range. SNS uses scale-fitted squared centroid-distance residuals; TW uses $k=1$ on valid frames. TD sums matched displacements in full-canvas units. SD is the separately named adjacent-section displacement, available only for Benzene (170 spatial matches). -- denotes an inapplicable metric; native axes have no direct-reference $E$ without calibration. TMTM, ST-MTM and P have zero measured NMLE. R uses $\kappa=0.2\Delta_F$, an eligibility threshold rather than an achieved-error cap. Protocols and eligible counts are in Supplement S3.\par}',
        r'\end{table*}','']
    return '\n'.join(lines)


def main():
    historical = read(ROOT/'results/submission20261023/unified_metrics.json')
    data = sorted(historical['datasets'],key=lambda d:ORDER.index(d['name']))
    sources = {'results/submission20261023/unified_metrics.json':sha(ROOT/'results/submission20261023/unified_metrics.json')}
    for d in data:
        if d['name'] in ['Storms','Wildfires','OLR','PM2.5','Ring']:
            key = {'Storms':'era5','Wildfires':'wildfire','OLR':'olr','PM2.5':'pm25','Ring':'ring'}[d['name']]
            path = ROOT/'results/pm25_2000/standard_metrics.json' if key=='pm25' else ROOT/f'results/public_metrics_20261016/{key}.json'
            d['geometry'] = {m['method']:m for m in read(path)['results']}
        else:
            key = next(k for k,c in CONFIG.items() if c[0]==d['name'])
            path = OUT/key/'metrics.json'
            assert read(OUT/key/'status.json')['status']=='complete'
            results = read(path); d['geometry'] = {m['method']:m for m in results}
            st = next(m for m in results if m['method']=='ST-MTM')
            d['methods']['ST-MTM'] = {k:st[k] for k in ['NROE','NMLE_mean','NMLE_max']}
            if 'motion' in st:
                d['methods']['ST-MTM']['motion'] = st['motion']
                assert st['motion']['clear']==d['methods']['RG-MTM-P']['motion']['clear']
        assert set(d['geometry'])==set(METHODS)
        sources[str(path.relative_to(ROOT))] = sha(path)
    result = dict(scope='Completed nine-input native ST-MTM and SNS/TW/TD evaluation; 2-D before 3-D',
        datasets=data,source_sha256=sources,
        provenance='Historical primary runs unchanged. Four new native ST-MTM runs use identical saved trees/supports/tracks and fixed generic parameters.',
        static='TD and temporal ME remain undefined for Nucleon and Benzene; adjacent-section displacement is separate.')
    dump(OUT/'unified_metrics.json',result)
    csvrows = []
    for d in data:
        for method in METHODS:
            p = d['methods']['RG-MTM-R20' if method=='RG-MTM-R' else method]
            g = d['geometry'][method]
            csvrows.append(dict(dataset=d['name'],dimension=d['dimension'],method=method,
                NROE=p['NROE'],NMLE_mean=p['NMLE_mean'],NMLE_max=p['NMLE_max'],
                motion_errors=p.get('motion',{}).get('errors'),N_clear=p.get('motion',{}).get('clear'),
                **{k:g.get(k) for k in ['SNS','TW1','TD','section_displacement','SNS_frames','TW1_frames','matched_steps']}))
    text = io.StringIO(); writer = csv.DictWriter(text,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
    (OUT/'unified_metrics.csv').write_text(text.getvalue())
    tables = {}
    tables['comparison_revision.tex']=grouped_comparison(data)
    for name in ['datasets_main.tex','achieved_reference_main.tex']:
        lines = (ROOT/'results/submission20261023/tables'/name).read_text().splitlines()
        def data_name(line): return 'PM2.5' if line.startswith(r'PM$_{2.5}$ &') else line.split(' &')[0]
        indices = [i for i,s in enumerate(lines) if data_name(s) in ORDER and ' & ' in s]
        selected = {data_name(lines[i]):lines[i] for i in indices}
        lines[min(indices):max(indices)+1] = [selected[n] for n in ORDER]
        tables[name] = '\n'.join(lines)+'\n'
    for dimension in [2,3]: tables[f'geometry{dimension}d_main.tex'] = geometry_table(data,dimension)
    lines = [r'\begingroup\small\setlength{\tabcolsep}{4pt}',r'\begin{longtable}{llrrrrrr}',
        r'\caption{Completed geometry and stability evaluation, with all 2-D inputs preceding 3-D volumes.}\label{tab:standard_geometry}\\\toprule',
        r'Data & Method & SNS & TW$_1$ & TD & Section disp. & $N_{\rm SNS}$ & $N_{\rm TW}$\\\midrule\endfirsthead',
        r'\toprule Data & Method & SNS & TW$_1$ & TD & Section disp. & $N_{\rm SNS}$ & $N_{\rm TW}$\\\midrule\endhead',r'\bottomrule\endfoot']
    for d in data:
        for method in METHODS:
            g = d['geometry'][method]
            cells = [d['name'],method]+['--' if g.get(k) is None else f'{g[k]:.4f}' for k in ['SNS','TW1','TD','section_displacement']]+[str(g[k]) for k in ['SNS_frames','TW1_frames']]
            lines.append(' & '.join(cells)+r'\\')
    lines += [r'\end{longtable}\endgroup','']
    tables['standard_metrics_supp.tex'] = '\n'.join(lines)
    # Archive editable sources before updating the active manuscript.
    backup = ROOT.parents[1]/'其他/归档/评价补全前_20261026'
    if not backup.exists():
        for path in PAPER.rglob('*.tex'):
            target=backup/'latex'/path.relative_to(PAPER);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
        for name in ['Revised_RG-MTM.pdf','Revised_Supplement.pdf']:
            shutil.copy2(PAPER.parent/name,backup/name)
    for name,text in tables.items():
        (OUT/'tables').mkdir(exist_ok=True)
        (OUT/'tables'/name).write_text(text); (PAPER/'tables'/name).write_text(text)
    evidence = PAPER/'evidence/stmtm_completion20261026'
    evidence.mkdir(parents=True,exist_ok=True)
    for name in ['unified_metrics.json','unified_metrics.csv']:
        shutil.copy2(OUT/name,evidence/name)
    for key in CONFIG:
        for name in ['protocol.json','metrics.json','frame_metrics.json','geometry_frames.json','landmarks.json','skeletons.json','solver_checks.json','status.json']:
            target=evidence/key/name;target.parent.mkdir(exist_ok=True);shutil.copy2(OUT/key/name,target)
    dump(OUT/'export_manifest.json',dict(source_sha256=sources,table_sha256={n:sha(OUT/'tables'/n) for n in tables}))
    report = ['# 评价补全（2026-10-26）','',
        '缺失原因：旧主表生成器对四个新增输入将 ST-MTM 固定为 None；第二篇论文 SNS/TW/TD 的旧复核只选取五个二维时序，并未覆盖静态和体数据。缺失不是指标天然不适用。',
        '', '本次新增：Nucleon 1、Benzene 21、Tangaroa 201、Cylinder 102，共 325 个 ST-MTM 布局和完整标量剖面。四种方法的 SNS/TW 已覆盖全部九组输入。',
        '', 'Nucleon、Benzene 不含物理时间，所以 ME、TD 保留不适用；Benzene 仅报告相邻截面位移。所有表按七组二维输入、两组三维体输入排列。','',
        '| 数据 | ST-MTM NROE (%) | SNS | TW1 | TD | ME |','|---|---:|---:|---:|---:|---|']
    for d in data:
        p=d['methods']['ST-MTM'];g=d['geometry']['ST-MTM'];m=p.get('motion')
        report.append(f'| {d["name"]} | {p["NROE"]:.6f} | {g["SNS"]:.6f} | {g["TW1"]:.6f} | '+('--' if g.get('TD') is None else f'{g["TD"]:.6f}')+' | '+(f'{m["errors"]}/{m["clear"]}' if m else '不适用')+' |')
    report += ['', '补跑采用固定通用参数，没有调参择优；三维欧氏距离直接用于原有几何目标。多叉节点用等标量、空新增弧的固定 ID 二叉细化，逐对 LCA 标量保持不变，但会限制可选叶序，属于明确声明的实现扩展。Eq.1 以 OSQP 求解相同凸目标，Eq.2 用可行目标宽度给出零目标的全局最优证书。Tangaroa 宽度使用物理体积，其他数据使用样本数。Cylinder 沿用全画布阈值，其余时序沿用占用范围阈值。',
        '', '历史数值和历史 submission20261023 快照不改写。当前活动正文表和新 evidence/stmtm_completion20261026 是本轮入口；再次运行旧表生成器会恢复旧版未补跑表。']
    (OUT/'REPORT_zh.md').write_text('\n'.join(report)+'\n')
    print('\n'.join(report))


if __name__=='__main__': main()
