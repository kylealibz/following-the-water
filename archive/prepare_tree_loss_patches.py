from pathlib import Path
import json,math
import numpy as np
from osgeo import gdal,ogr,osr
R=Path('work/map_enrichment_20261106');O=Path('work/standalone_maps_20261106');O.mkdir(exist_ok=True)
loss=np.load(R/'lossyear.npy');tree=np.load(R/'treecover2000.npy')
gdal.UseExceptions();gdal.SetConfigOption('GDAL_HTTP_TIMEOUT','45')
url='https://storage.googleapis.com/earthenginepartners-hansen/GFC-2025-v1.13/Hansen_GFC-2025-v1.13_lossyear_20N_090W.tif'
src=gdal.Open('/vsicurl/'+url);gt=src.GetGeoTransform()
x=math.floor((-88.90-gt[0])/gt[1]);y=math.floor((17.75-gt[3])/gt[5])
aff=[gt[0]+x*gt[1],gt[1],0,gt[3]+y*gt[5],0,gt[5]]
values=np.where((tree>=30)&(loss>0)&(loss<=25),loss,0).astype('uint8')
mem=gdal.GetDriverByName('MEM').Create('',loss.shape[1],loss.shape[0],1,gdal.GDT_Byte)
mem.SetGeoTransform(aff);srs=osr.SpatialReference();srs.ImportFromEPSG(4326);mem.SetProjection(srs.ExportToWkt())
band=mem.GetRasterBand(1);band.SetNoDataValue(0);band.WriteArray(values);band.FlushCache()
ds=ogr.GetDriverByName('Memory').CreateDataSource('');lyr=ds.CreateLayer('loss',srs,ogr.wkbPolygon)
lyr.CreateField(ogr.FieldDefn('LossYear',ogr.OFTInteger));gdal.Polygonize(band,None,lyr,0,[],callback=None)
lyr.ResetReading()
print('PATCH_COUNT',lyr.GetFeatureCount(),'LOSS_PIXELS',int(np.count_nonzero(values)),flush=True)
features=[];groups={};totals={yr:0.0 for yr in range(2001,2026)}
a=6378137.;e2=.0066943799901413165
def ha_per_deg2(lat):
 phi=math.radians(lat)
 return a*a*(1-e2)*math.cos(phi)/(1-e2*math.sin(phi)**2)**2*(math.pi/180)**2/10000
for f in lyr:
 if f.GetField('LossYear')==0:continue
 geom=f.GetGeometryRef();year=2000+f.GetField('LossYear');cent=geom.Centroid()
 area=geom.GetArea()*ha_per_deg2(cent.GetY());totals[year]+=area
 key=(year,math.floor(cent.GetX()*10),math.floor(cent.GetY()*10))
 group=groups.setdefault(key,{'coords':[],'ha':0,'patches':0});group['ha']+=area;group['patches']+=1
 coords=json.loads(geom.ExportToJson())['coordinates']
 group['coords'].append([[[round(v,6) for v in point] for point in ring] for ring in coords])
for (year,tx,ty),group in groups.items():
 features.append({'type':'Feature','geometry':{'type':'MultiPolygon','coordinates':group['coords']},'properties':{'LossYear':year,'Group_ha':round(group['ha'],2),'PatchCount':group['patches'],'Source':'Hansen Global Forest Change v1.13, 2000-2025','Baseline':'At least 30% tree canopy cover in 2000','Limit':'Mapped gross tree-cover loss, not net forest change or proof of agricultural clearing. Does not include 2026. Approximately 30 m source pixels. Disconnected patches are grouped by year and display tile for efficient loading.','Source_URL':'https://developers.google.com/earth-engine/datasets/catalog/UMD_hansen_global_forest_change_2025_v1_13'}})
out={'type':'FeatureCollection','features':features}
(O/'tree_loss_patches.geojson').write_text(json.dumps(out,separators=(',',':')),encoding='utf-8')
stats={'bbox':[-88.90,17.25,-88.30,17.75],'affine':aff,'patches':sum(x['patches'] for x in groups.values()),'display_groups':len(features),'annual_loss_ha':totals,'cumulative_ha':{end:round(sum(v for yr,v in totals.items() if yr<=end),1) for end in [2005,2010,2015,2020,2025]},'source_pixel_degrees':gt[1]}
(O/'tree_loss_stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print(json.dumps(stats),flush=True)
print('GEOJSON_BYTES',(O/'tree_loss_patches.geojson').stat().st_size,flush=True)
