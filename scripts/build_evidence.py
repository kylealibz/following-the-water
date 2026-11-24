"""Join public place references to reported DO values. No GIS licence required."""
from pathlib import Path
import csv
import json
import math

ROOT = Path(__file__).resolve().parents[1]


def read_json(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf8'))


def symbol_diameter(value, maximum=6.19, maximum_diameter=28):
    """Circle area, rather than diameter, is proportional to a positive value."""
    if value is None:
        return 10  # hollow reference marker, not a zero measurement
    if value < 0 or maximum <= 0:
        raise ValueError('DO must be nonnegative and scale maximum positive')
    return round(maximum_diameter * math.sqrt(value / maximum), 4)


def build():
    places = read_json('community_reference_points.geojson')
    readings = read_json('reported_oxygen_readings.json')
    by_id = {r['geonames_reference_id']: r for r in readings if r['geonames_reference_id']}
    names = {"Saint Paul's": "Saint Paul's Bank", 'Scotland Halfmoon': 'Scotland Half Moon'}
    for feature in places['features']:
        props = feature['properties']
        record = by_id.get(props['geonames_id'])
        props['display_name'] = names.get(props['name'], props['name'])
        props['reported_do_mg_l'] = record['reported_value'] if record else None
        props['publication_date'] = record['publication_date'] if record else None
        props['sample_datetime'] = None
        props['do_source_url'] = record['source_url'] if record else None
        props['evidence_status'] = 'Community-associated reported value' if record else 'No value in this source; not zero'
        props['symbol_diameter_pt'] = symbol_diameter(props['reported_do_mg_l'])
    out = ROOT / 'results'
    out.mkdir(exist_ok=True)
    (out / 'community_oxygen.geojson').write_text(json.dumps(places, indent=2), encoding='utf8')
    with (out / 'oxygen_readings.csv').open('w', newline='', encoding='utf8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(readings[0]))
        writer.writeheader()
        writer.writerows(readings)
    unmapped = [r for r in readings if not r['geonames_reference_id']]
    report = {'communities': len(places['features']), 'reported_readings': len(readings),
              'community_associated_values': len(by_id), 'unlocated_readings': len(unmapped),
              'missing_community_values': len(places['features']) - len(by_id),
              'note': 'No interpolated plume. Publication dates are not sampling dates.'}
    (out / 'validation.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    print(json.dumps(report, indent=2))
    return places, readings


if __name__ == '__main__':
    build()
