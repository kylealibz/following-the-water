"""Download public reference mapping and satellite metadata. Python 3.9+.
Run: python collect_public_mapping.py --out public_mapping
No ArcGIS credentials needed. Does not publish, identify a farm, or infer pollution.
"""
import argparse
import io
import json
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

RIVERS = 'https://services9.arcgis.com/mt4kvYhNXSa5AqLG/ArcGIS/rest/services/Belize_Rivers/FeatureServer/0'
GEONAMES = 'https://download.geonames.org/export/dump/BZ.zip'
STAC = 'https://earth-search.aws.element84.com/v1/search'
BBOX = [-88.85, 17.25, -88.38, 17.68]  # Analyst-selected search extent, not an impact boundary.
IDS = {'3581246', '3581633', '3581897', '3582018', '3582099',
       '3582194', '3582514', '3582661', '13286681'}


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'BelizeRiverResearch/1.0'})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def fc(features):
    return {'type': 'FeatureCollection', 'features': features}


def communities(raw):
    rows = zipfile.ZipFile(io.BytesIO(raw)).read('BZ.txt').decode('utf-8').splitlines()
    output = []
    for row in rows:
        c = row.split('\t')
        if c[0] in IDS:
            output.append({'type': 'Feature', 'geometry': {'type': 'Point',
                'coordinates': [float(c[5]), float(c[4])]}, 'properties': {
                'geonames_id': c[0], 'name': c[2],
                'source_url': f'https://www.geonames.org/{c[0]}/',
                'source_modified': c[18], 'location_role': 'Settlement reference point only',
                'limitation': 'Not a fish-kill observation, sample station or village boundary',
                'attribution': 'GeoNames, CC BY 4.0'}})
    if len(output) != len(IDS):
        raise ValueError('Some selected community IDs were missing; inspect the source download.')
    return fc(output)


def scene_inventory(features):
    return [{'scene_id': f['id'], 'datetime': f['properties']['datetime'],
             'tile': f['properties'].get('grid:code'),
             'tile_cloud_percent': f['properties'].get('eo:cloud_cover'),
             'metadata_url': next((x['href'] for x in f.get('links', []) if x['rel']=='self'), ''),
             'assets': {k: v['href'] for k, v in f['assets'].items()},
             'status': 'Catalogue only; pixels and local cloud cover not assessed'}
            for f in features]


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    meta = json.loads(get(RIVERS + '?f=json'))
    if 'error' in meta:
        raise ValueError(meta['error'])
    save(out / 'river_service_metadata.json', meta)
    common = {'where': '1=1', 'geometry': ','.join(map(str, BBOX)),
              'geometryType': 'esriGeometryEnvelope', 'inSR': 4326,
              'spatialRel': 'esriSpatialRelIntersects'}
    id_result = json.loads(get(RIVERS+'/query?'+urllib.parse.urlencode({
        **common, 'returnIdsOnly': 'true', 'f': 'json'})))
    if 'error' in id_result:
        raise ValueError(id_result['error'])
    object_ids = id_result.get('objectIds') or []
    river_features = []
    for i in range(0, len(object_ids), 200):
        params = {'objectIds': ','.join(map(str, object_ids[i:i+200])),
                  'outFields': '*', 'outSR': 4326, 'f': 'geojson'}
        chunk = json.loads(get(RIVERS+'/query?'+urllib.parse.urlencode(params)))
        if 'error' in chunk or chunk.get('exceededTransferLimit'):
            raise ValueError('River download failed or was truncated')
        river_features.extend(chunk['features'])
    for f in river_features:
        f['properties'].update({'source_url': RIVERS,
            'mapping_limit': 'Historical 1:50,000 reference hydrography; not verified 2026 canals'})
    save(out / 'reference_rivers.geojson', fc(river_features))
    save(out / 'belize_and_labouring.geojson', fc([f for f in river_features
        if f['properties'].get('Name') in ('Belize River', 'Labouring Creek')]))
    save(out / 'community_reference_points.geojson', communities(get(GEONAMES)))
    url = STAC+'?'+urllib.parse.urlencode({'collections':'sentinel-2-l2a',
        'bbox':','.join(map(str,BBOX)), 'datetime':'2026-05-01T00:00:00Z/2026-09-30T23:59:59Z',
        'limit':100})
    scenes, visited = {}, set()
    while url:
        if url in visited:
            raise ValueError('Repeated catalogue page')
        visited.add(url)
        page = json.loads(get(url))
        for f in page['features']:
            scenes[f['id']] = f
        url = next((x['href'] for x in page.get('links', []) if x['rel']=='next'), None)
    save(out / 'satellite_inventory.json', scene_inventory(list(scenes.values())))
    save(out / 'download_manifest.json', {
        'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'search_bbox': BBOX,
        'river_segments': len(river_features), 'scenes': len(scenes),
        'sources': [RIVERS, GEONAMES, STAC],
        'limitation': 'Search extent is not a watershed or incident footprint. No farm polygon inferred.'})
    print(f'Downloaded {len(river_features)} river segments, {len(IDS)} communities, {len(scenes)} scene records to {out.resolve()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('public_mapping'))
    main(parser.parse_args().out)
