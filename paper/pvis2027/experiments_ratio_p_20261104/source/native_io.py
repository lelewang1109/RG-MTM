"""Pinned project-native TTK frame adapter, no external experiment imports."""
from pathlib import Path
import numpy as np
from experiments.volume3d.paper_trees import Frame as NativeFrame
W=Path(__file__).resolve().parents[4]
R=W/'RG-MTM' if (W/'RG-MTM/code').exists() else W
RAW=R/'data/real/ERA5_MSLP/ERA5_MSLP_19991117_20000114.nc'
BIN=R/'code/tmp/volume3d/native-build/rgmtm_ttk_volume'
if not BIN.exists():BIN=Path(__file__).resolve().parent/'native/rgmtm_ttk_volume_macos_arm64'
class Frame(NativeFrame):
 def __init__(self,t,directory,coords):
  super().__init__(t,directory);self.coordinates=coords;self.domain_min=coords.min(0);self.domain_max=coords.max(0);self.sample_ids=np.arange(len(coords));self.kind='join'
 def leaf_centroid(self,k):return self.coordinates[self.leaf_feature_vertices(k)].mean(0)
 def leaf_size(self,k):return len(self.leaf_feature_vertices(k))
