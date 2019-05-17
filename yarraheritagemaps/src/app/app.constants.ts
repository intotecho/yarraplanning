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

import * as colorbrewer from 'colorbrewer';

export const Step = {
    DATA: 0,
    SCHEMA: 1,
    STYLE: 2
};

export const HERITAGE_SITE_DATACENTER = 'australia-southeast1';

export const HERITAGE_SITE_PROJECT_ID = 'yarrascrape';
export const HERITAGE_SITE_QUERY = `
    #standardsql
    SELECT
    HeritageStatus,
    Overlay,
    NormalAddress,
    EstimatedDate,
    Image,
    VHR,
    href,
    vhdplaceid,
    SosHash,
    SAFE.ST_GeogFromGeoJson(boundary) as bndry,
    ST_GeogFromGeoJson(location) as locn
    FROM
    \`yarrascrape.YarraPlanning.YARRAHERITAGEMAPS_PROPERTIES\` as register
    WHERE
    register.Overlay = @overlay
  `;


export const OVERLAYS_QUERY = `
  #standardsql
  SELECT
  ZONE_DESC,
  ZONE_CODE,
  Overlay,
  HeritagePlace,
  Included,
  VHR,
  TreeControls,
  PaintControls,
  InternalControls,
  FenceControls,
  AboriginalHeritagePlace,
  Prohibited,
  Status,
  Expiry,
  SAFE.ST_GeogFromGeoJson(geom) as bndry
  FROM
  \`yarrascrape.YarraPlanning.OVERLAYS\` as overlays
  where LGA = "YARRA"
  AND SCHEMECODE = "HO"`;


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
  fillOpacity: 0.6
};

export const OVERLAY_FILL_COLOR = {
  isComputed: true,
  property: 'TreeControls',
  function: 'categorical',
  domain: ['Yes', 'No', '-'],
  range: ['#00FF00', '#FFFFAA', '#AAAAAA', '#0000FF']
};
export const OVERLAY_FILL_OPACITY = {isComputed: false, value: 0.1};

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


export const HERITAGE_SITE_FILL_OPACITY = {isComputed: false, value: 0.3};
export const HERITAGE_SITE_ZINDEX = 200; // higher than overlay

export const HERITAGE_SITE_FILL_COLOR = {
  isComputed: true,
  property: 'HeritageStatus',
  function: 'categorical',
  domain: ['Contributory', 'Not contributory', 'Individually Significant', 'Victorian Heritage Register', 'Unknown', ''],
  range: ['#75954c', '#9DAFB2', '#d279e5', '#e74d4d', '#FFFF00' , '#AAAAAA']
};

export const HERITAGE_SITE_CIRCLE_RADIUS = {
  isComputed: true,
  property: 'num_bikes_available',
  function: 'linear',
  domain: [0, 60],
  range: [2, 24]
};

export const HERITAGE_SITE_STROKE_COLOR = {
  isComputed: false,
  value: '#408040'
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

