"""Optional ArcPy export; requires a licensed ArcGIS Pro Python environment.

This curated adapter creates a NEW file geodatabase. It does not publish items.
Run the portable evidence build first. Add optional river downloads if desired.
"""
from pathlib import Path
import arcpy

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'results'/'arcgis'
out.mkdir(exist_ok=True)
gdb=out/'Following_the_Water.gdb'
if gdb.exists():raise SystemExit('Output already exists. Choose a fresh output folder.')
arcpy.management.CreateFileGDB(str(out),gdb.name)
arcpy.conversion.JSONToFeatures(str(ROOT/'results/community_oxygen.geojson'),str(gdb/'Community_oxygen'),'POINT')
source=ROOT/'data/external/belize_and_labouring.geojson'
if source.exists():arcpy.conversion.JSONToFeatures(str(source),str(gdb/'Focal_rivers'),'POLYLINE')
print(gdb)
