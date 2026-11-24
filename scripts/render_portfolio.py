"""Rebuild figures and a portable interactive HTML map from the saved evidence."""
from pathlib import Path
import csv
import html
import json
import math
import folium
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from build_evidence import build, ROOT

CREAM, INK, TEAL, GOLD = '#f5f5e9', '#173f43', '#27858a', '#b29448'


def finish(fig, name):
    fig.savefig(ROOT / 'figures' / name, dpi=180, facecolor=CREAM)
    plt.close(fig)


def main():
    places, readings = build()
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK,
                         'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(figsize=(12, 6), facecolor=CREAM)
    ax.set_facecolor(CREAM)
    labels = [r['reported_site'].replace(' of Santander canal', '\nof canal') for r in readings]
    ax.barh(labels, [r['reported_value'] for r in readings], color=TEAL, height=.62)
    ax.invert_yaxis(); ax.set_xlim(0, 8.5); ax.set_xlabel('Reported dissolved oxygen (mg/L)')
    for i, r in enumerate(readings):
        ax.text(r['reported_value']+.12, i, f"{r['reported_value']:.2f}", va='center', weight='bold')
    ax.set_title('Reported oxygen along the river', loc='left', fontsize=20, weight='bold', pad=22)
    fig.text(.03,.025,'Source: Love FM, 17 August 2026. Secondary transcription; sample times and exact station coordinates unavailable.',fontsize=9)
    fig.subplots_adjust(left=.31, right=.95, bottom=.14, top=.84)
    finish(fig,'reported_oxygen.png')

    stats = json.loads((ROOT/'data/tree_loss_stats.json').read_text())
    years = list(map(int,stats['annual_loss_ha']))
    values = list(stats['annual_loss_ha'].values())
    fig, ax = plt.subplots(figsize=(12,4.8),facecolor=CREAM); ax.set_facecolor(CREAM)
    ax.bar(years, [v/1000 for v in values],color=GOLD,width=.8)
    ax.set_ylabel('Mapped gross tree-cover loss (thousand ha)'); ax.set_xlabel('Loss year')
    ax.set_xticks([2001,2005,2010,2015,2020,2025])
    ax.set_title('Historical landscape context, 2001–2025',loc='left',weight='bold',fontsize=20,pad=18)
    fig.text(.04,.03,'Hansen Global Forest Change v1.13; ≥30% canopy in 2000. Fixed corridor rectangle, not the watershed. Regrowth not subtracted.',fontsize=9)
    fig.subplots_adjust(left=.09,right=.98,bottom=.19,top=.82); finish(fig,'tree_cover_loss.png')

    m = folium.Map(location=[17.50,-88.56],zoom_start=10,tiles=None,control_scale=True)
    folium.TileLayer('OpenStreetMap',name='Reference basemap').add_to(m)
    markers = folium.FeatureGroup(name='Reported oxygen and evidence gaps',show=True).add_to(m)
    for feature in places['features']:
        p=feature['properties']; lon,lat=feature['geometry']['coordinates']; value=p['reported_do_mg_l']
        text=f"{value:.2f} mg/L reported" if value is not None else 'No reading in this source; not zero'
        source = f'<p><a href="{html.escape(p["do_source_url"],quote=True)}" target="_blank" rel="noopener">Reported source</a></p>' if value is not None else ''
        popup=f'<b>{html.escape(p["display_name"])}</b><p>{text}</p><p>Settlement reference only. Exact sampling coordinates and times unknown.</p>{source}'
        folium.CircleMarker([lat,lon],radius=p['symbol_diameter_pt']/2,color=INK,weight=1.5,
                            fill=value is not None,fill_color=TEAL,fill_opacity=.8,
                            tooltip=f'{p["display_name"]}: {text}',popup=folium.Popup(popup,max_width=310)).add_to(markers)
    with (ROOT/'data/rainfall_cells.csv').open() as f:
        rain=list(csv.DictReader(f))
    weeks=json.loads((ROOT/'data/rain_weeks.json').read_text())
    for week in weeks:
        group=folium.FeatureGroup(name=f'Rainfall: {week["label"]} (mm)',show=False).add_to(m)
        for cell in rain:
            lon,lat=float(cell['longitude']),float(cell['latitude']);value=float(cell[week['field']])
            color = '#186f72' if value>400 else '#51a38d' if value>200 else '#9bceba' if value>100 else '#d7e9dc'
            folium.Rectangle([[lat-.025,lon-.025],[lat+.025,lon+.025]],color=color,weight=.2,
                             fill=True,fill_color=color,fill_opacity=.55,
                             tooltip=f'{value:.1f} mm | {week["label"]}',
                             popup='CHIRPS v3 final daily, rnl branch. Complete 7-day total; approximately 5 km cells. Not measured runoff.').add_to(group)
    folium.LayerControl(collapsed=True).add_to(m)
    box='''<div style="position:fixed;bottom:25px;left:15px;z-index:9999;background:#f5f5e9;padding:14px;max-width:310px;font:13px/1.4 sans-serif;border:1px solid #b29448;color:#173f43"><b>Following the Water | Evidence explorer</b><br>Filled circles: reported DO; area proportional to mg/L.<br>Hollow circles: no value in this source, not zero.<br>Rainfall layers: choose ONE week at a time in the layer menu. Shades: ≤100, &gt;100–200, &gt;200–400, &gt;400 mm.<br><small>Places: GeoNames CC BY 4.0. DO: Love FM, 17 Aug 2026. Rain: CHIRPS v3. Map is context, not a pollution footprint.</small></div>'''
    m.get_root().html.add_child(folium.Element(box))
    destination=ROOT/'docs/evidence_explorer.html'
    m.save(str(destination))
    destination.write_text('\n'.join(line.rstrip() for line in destination.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
    print('Wrote two figures and docs/evidence_explorer.html')


if __name__=='__main__':
    main()
