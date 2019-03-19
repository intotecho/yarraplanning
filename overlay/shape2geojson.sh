#sudo apt-get install gdal-bin unzip
ogr2ogr -f csv -dialect sqlite -sql "select AsGeoJSON(geometry) AS geom, * from PLAN_OVERLAY" yarra_overlays.csv VicDataMartDownload/ll_gda94/shape/lga_polygon/yarra-1000/VMPLAN/PLAN_OVERLAY.shp
ogr2ogr -f csv -dialect sqlite -sql "select AsGeoJSON(geometry) AS geom, * from PLAN_ZONE" yarra_zones.csv VicDataMartDownload/ll_gda94/shape/lga_polygon/yarra-1000/VMPLAN/PLAN_ZONE.shp

