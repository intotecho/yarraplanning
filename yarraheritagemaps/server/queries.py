

OVERLAYS_QUERY = """
    #standardsql
    SELECT
    Overlay,
    ZONE_DESC,
    HeritagePlace,
    Included,
    VHR,
    Image,
    TreeControls,
    PaintControls,
    InternalControls,
    FenceControls,
    AboriginalHeritagePlace,
    Prohibited,
    Expiry,
    Status,
    OverlayBoundary as bndry
    FROM
    `yarrascrape.{0}.OVERLAYS` as overlays
    """

# TODO Dataset to be a parameter.
HERITAGE_SITE_QUERY = """
  #standardsql
  SELECT
  ROW_NUMBER() OVER () AS row_num,
  EZI_ADD,
  HeritageStatus,
  Overlay,
  Name,
  vhdplaceid,
  vhdPlacesId,
  Image,
  Authority,
  PropertyType,
  PROPNUM,
  EstimatedDate,
  OriginalAddress,
  vhdLocation,
  Matched,
  VHR,
  href,
  SosHash,
  earliest,
  bndry
  FROM
  `yarrascrape.{0}.YARRAHERITAGEMAPS_PROPERTIES` as register
  WHERE
  register.Overlay='{1}'
"""


PLANNING_APPS_QUERY ="""
    WITH params AS (
      SELECT "{1}" AS overlay,
            0.01   AS maxdist_km
    ),
    overlay AS (
      SELECT ST_GeogFromGeoJson(geom) AS polygon
      FROM  `yarrascrape.{0}.YARRA_OVERLAYS`, params
      WHERE ZONE_CODE = '{1}'
    ),
    applications AS (
      SELECT
        Application_Number,
        Property_Address,
        Estimated_Cost,
        HeritageStatus,
        Date_Received,
        Description,
        Decision,
        Application_Status,
        Abandoned,
        Refused,
        Approved,
        In_Progress,
        ST_GeogPoint(longitude, latitude) AS bndry,
        ST_Distance(ST_GeogPoint(longitude, latitude), overlay.polygon) AS dist_meters
      FROM
      `yarrascrape.YarraPlanning.YARRA_APPLICATIONS_WITH_HERITAGE`,
        params,
        overlay
      WHERE ST_DWithin(ST_GeogPoint(longitude, latitude), overlay.polygon,  params.maxdist_km*1000)
    )
    SELECT * from applications;
"""