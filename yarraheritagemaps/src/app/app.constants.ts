/**
 * Copyright 2018 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import { environment } from '../environments/environment';
import * as colorbrewer from 'colorbrewer';

export const Step = {
    DATA: 0,
    SCHEMA: 1,
    STYLE: 2
};

export const HERITAGE_SITE_DATACENTER = 'australia-southeast1';

export const HERITAGE_SITE_PROJECT_ID = 'yarrascrape';

  /*
   * Changing these fields must algin with HeritageSiteInfo
   */
  export const HERITAGE_SITE_QUERY = `
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
  \`yarrascrape.${environment._DATASET}.YARRAHERITAGEMAPS_PROPERTIES\` as register
  WHERE
  register.Overlay = @overlay
`;

export const PLANNING_APPS_QUERY = `
    #standardsql
    WITH params AS (
      SELECT "HO330" AS overlay,
            0.01   AS maxdist_km
    ),
    overlay AS (
      SELECT ST_GeogFromGeoJson(geom) AS polygon
      FROM  \`yarrascrape.${environment._DATASET}.YARRA_OVERLAYS\`, params
      WHERE Overlay = @overlay
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
      \`yarrascrape.${environment._DATASET}.YARRAHERITAGEMAPS_PROPERTIES\`,
        params,
        overlay
      WHERE ST_DWithin(ST_GeogPoint(longitude, latitude), overlay.polygon,  params.maxdist_km*1000)
    )
    SELECT * from applications
    ORDER BY dist_meters ASC`;

export const OVERLAYS_QUERY = `
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
    \`yarrascrape.${environment._DATASET}.OVERLAYS\` as overlays`;
  /*
    WHERE Overlay LIKE '%HO88%'
    OR Overlay LIKE '%HO91%'
    OR Overlay LIKE '%HO330%'
    OR Overlay LIKE '%HO317%'
    OR Overlay LIKE '%HO93%'
    */

export const HERITAGE_OVERLAY_STYLE = {
  strokeColor: '#F0A0A0',
  zIndex: 10,
  strokeWeight: 2,
  strokeOpacity: 0.6,
  fillColor: '#F0B0B0',
  fillOpacity: 0.2
};

export const HIGHLIGHTED_HERITAGE_OVERLAY_STYLE = {
  strokeColor: '#F0B0B0',
  zIndex: 50,
  strokeWeight: 3,
  strokeOpacity: 0.8,
  fillColor: '#F09090',
  fillOpacity: 0.6,
  circleRadius: 50
};

export const OVERLAY_FILL_COLOR = {
  isComputed: true,
  property: 'TreeControls',
  function: 'categorical',
  domain: ['Yes', 'No', '-'],
  range: ['#00FF00', '#FFFFAA', '#FFFFAA', '#0000FF']
};
export const OVERLAY_FILL_OPACITY = {
  /*
  isComputed: false,
  value: 0.1
  */
  isComputed: true,
  property: 'Status',
  function: 'categorical',
  domain: ['null', 'Interim'],
  range: [0.1, 0.8]
};

export const OVERLAY_STROKE_COLOR = {
  isComputed: true,
  property: 'Included',
  function: 'categorical',
  domain: ['true', 'false'],
  range: ['#FF000000', '#000000']
};

export const OVERLAY_STROKE_OPACITY = {
  isComputed: false,
  value: 0.9
};

export const OVERLAY_STROKE_WIDTH = {
  isComputed: false,
  value: 0.9
};

export const HERITAGE_SITE_FILL_OPACITY = {isComputed: false, value: 0.3};
export const HERITAGE_SITE_ZINDEX = 200; // higher than overlay

export const HERITAGE_SITE_FILL_COLOR_HERITAGESTATUS = {
  isComputed: true,
  property: 'HeritageStatus',
  function: 'categorical',
  domain: ['Contributory', 'Not contributory', 'Individually Significant', 'Victorian Heritage Register', 'Unknown'],
  range: ['#75954c', '#9DAFB2', '#d279e5', '#e74d4d', '#FFFF00' , '#AAAAAA'],
  caption: ['Contributory', 'Not Contributory', 'Individually Significant', 'Victorian Heritage Register', 'Unknown Status'],
  circleRadius: 50
};

export const HERITAGE_SITE_FILL_COLOR_EARLIESTDECADE = {
  isComputed: true,
  property: 'earliest',
  function: 'interval',
  value: '#202020',
  domain: [ 1840,           1860,        1880,        1900,        1920,        1940,        1960,        2030],
  range:  [ '#242424',      '#990000',   '#d7301f',   '#ef6548',   '#fc8d59',   '#fdbb84',   '#fdd49e',   '#fed4ff'],
  caption: ['Unknown Date', '1840-1859', '1860-1879', '1890-1899', '1900-1919', '1920-1939', '1940-1959', 'After 1960'],
  circleRadius: 50
};


export const HERITAGE_SITE_CIRCLE_RADIUS_FIXED = {
  isComputed: false,
  circleRadius: 50,
  domain: [],
  range: []
};

export const HERITAGE_SITE_CIRCLE_RADIUS = {
  isComputed: true,
  property: 'Estimated_Cost',
  function: 'linear',
  domain: [1, 5000000],
  range: [4, 20],
  circleRadius: 50
};

export const HERITAGE_SITE_STROKE_COLOR = {
  isComputed: false,
  value: '#408040'
};

export const PLANNING_APP_STROKE_COLOR = {
  isComputed: false,  value: '#202020'
};


// Maximum number of results to be returned by BigQuery API.
export const MAX_RESULTS = 3600; // The biggest heritage overlay HO327 has 3535 sites

// Maximum number of results to be shown in the HTML preview table.
export const MAX_RESULTS_PREVIEW = 10;

// How long to wait for the query to complete, in milliseconds, before the request times out and returns.
export const TIMEOUT_MS = 120000;

export const PALETTES = Object.keys(colorbrewer).map((key) => colorbrewer[key]);

export const GCS_BUCKET_SOS: String = 'https://storage.googleapis.com/historic_map_overlays/SOS/';

export const VHD_KEYWORD_SEARCH: String = 'https://vhd.heritagecouncil.vic.gov.au/search?kw=';


