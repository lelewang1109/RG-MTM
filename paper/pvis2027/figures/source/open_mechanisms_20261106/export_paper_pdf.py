from pathlib import Path
import pymupdf
src=Path(__file__).resolve().parent
fig=src.parents[1]
for source,target in [("01_direction.png","anchor_direction_open"),("02_conflict.png","anchor_conflict_open"),("03_relaxation.png","anchor_relaxation_open")]:
 image=pymupdf.open(stream=(src/source).read_bytes(),filetype="png")
 document=pymupdf.open("pdf",image.convert_to_pdf())
 document.save(fig/(target+".pdf"))
