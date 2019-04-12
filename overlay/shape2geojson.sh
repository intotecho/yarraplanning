#sudo apt-get install gdal-bin unzip
#ogr2ogr -f csv -dialect sqlite -sql "select AsGeoJSON(geometry) AS geom, * from PLAN_OVERLAY" yarra_overlays.csv ZonesAndOverlaysOrder/ll_gda94/shape/lga_polygon/yarra-1000/VMPLAN/PLAN_OVERLAY.shp
#ogr2ogr -f csv -dialect sqlite -sql "select AsGeoJSON(geometry) AS geom, * from PLAN_ZONE" yarra_zones.csv ZonesAndOverlaysOrder/ll_gda94/shape/lga_polygon/yarra-1000/VMPLAN/PLAN_ZONE.shp
#ogr2ogr -f csv -dialect sqlite -sql "select AsGeoJSON(geometry) AS geom, * from PROPERTY_PRIMARY_APPROVED" yarra_properties.csv PropertyCadastreOrder/ll_gda94/shape/lga_polygon/yarra-1000/VMPROP/PROPERTY_PRIMARY_APPROVED.shp
ogr2ogr -f csv -dialect sqlite -sql "select AsGeoJSON(geometry) AS geom, * from ADDRESS" yarra_addresses.csv VicMapAddresses/ll_gda94/shape/lga_polygon/yarra-1000/VMADD 
