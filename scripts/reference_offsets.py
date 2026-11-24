"""Optional reference-distance analysis after downloading hydrography.

python scripts/collect_public_mapping.py --out data/external
python scripts/reference_offsets.py
These offsets describe reference datasets, not exposure or river travel.
"""
import csv
import json
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform, unary_union

ROOT=Path(__file__).resolve().parents[1]


def main():
    rivers=ROOT/'data/external/belize_and_labouring.geojson'
    if not rivers.exists():
        raise SystemExit('First run scripts/collect_public_mapping.py --out data/external')
    project=Transformer.from_crs('EPSG:4326','EPSG:32616',always_xy=True).transform
    network=json.loads(rivers.read_text(encoding='utf8'))
    belize=[transform(project,shape(f['geometry'])) for f in network['features'] if f['properties'].get('Name')=='Belize River']
    if not belize:
        raise ValueError('Belize River features absent; inspect source schema')
    river=unary_union(belize)
    communities=json.loads((ROOT/'results/community_oxygen.geojson').read_text())
    with (ROOT/'results/reference_offsets.csv').open('w',newline='',encoding='utf8') as handle:
        writer=csv.writer(handle);writer.writerow(['community','reference_offset_m','crs','interpretation'])
        for f in communities['features']:
            distance=transform(project,shape(f['geometry'])).distance(river)
            writer.writerow([f['properties']['display_name'],round(distance,1),'EPSG:32616','Point-to-reference-centerline distance; not exposure, access or sample error'])
    print('Saved results/reference_offsets.csv')


if __name__=='__main__':main()
