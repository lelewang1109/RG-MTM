"""Install the user-selected exact PNG without rebuilding scientific evidence or PPTs."""
from _filesystem import copy_if_distinct
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1]
src=R/'figures_export/Fig1.png'
dst=R/'manuscript/latex/figures/Fig1.png'
copy_if_distinct(src,dst)
receipt=dict(source=str(src),manuscript_asset=str(dst),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),method='RG-MTM-R20',frame_count=744,event_frames=[66,405,575,610,645],direction=[0.94783175,-0.31877104],selected_variant="Fig1_DataDirection",local_utc_interval=["1999-12-26 00:00","1999-12-26 23:00"],local_event_utc="1999-12-26 10:00",local_track_ids={"A":130,"B":113,"C":133},display_interpolation='anchor-aligned; crossing/large-jump fallback; original frames unchanged',Fig1_ppt_is_current_teaser=True)
(R/'checks/manuscript_teaser_selection.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Installed exact user-selected manuscript Figure 1 PNG.')
