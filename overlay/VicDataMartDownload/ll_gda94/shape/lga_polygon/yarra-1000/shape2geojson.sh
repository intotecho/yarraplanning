#sudo apt-get install gdal-bin unzip
ogr2ogr -explodecollections -f csv -dialect sqlite -sql "select AsGeoJSON(geometry) AS geom, * from FeatureCollection" EXTRACT_POLYGON.csv EXTRACT_POLYGON.shp 
