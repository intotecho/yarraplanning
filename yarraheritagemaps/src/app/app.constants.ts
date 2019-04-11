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

export const SAMPLE_DATACENTER = 'australia-southeast1';

export const SAMPLE_PROJECT_ID = 'yarrascrape';
export const SAMPLE_QUERY = `
    #standardsql
    SELECT
    HeritageStatus,
    Overlay,
    NormalAddress,
    SAFE.ST_GeogFromGeoJson(boundary) as bndry,
    ST_GeogFromGeoJson(location) as locn
    FROM
    \`yarrascrape.YarraPlanning.HERITAGE_OVERLAY_WITH_ADDR_AND_PROPERTY\` as register
    WHERE
    register.Overlay = @overlay
  `;

export const OVERLAYS_QUERY = `
  #standardsql
  SELECT
  ZONE_DESC,
  ZONE_CODE,
  SAFE.ST_GeogFromGeoJson(geom) as bndry
  FROM
  \`yarrascrape.YarraPlanning.YARRA_OVERLAYS\` as overlays
  where LGA = "YARRA"
  AND SCHEMECODE = "HO"`;

export const HERITAGE_OVERLAY_STYLE = {
  strokeColor: '#F0A0A0',
  zIndex: 0,
  strokeWeight: 2,
  strokeOpacity: 0.6,
  fillColor: '#F0B0B0',
  opacity: 0.2
};



export const HIGHLIGHTED_HERITAGE_OVERLAY_STYLE = {
  strokeColor: '#F0B0B0',
  zIndex: 0,
  strokeWeight: 3,
  strokeOpacity: 0.8,
  fillColor: '#F09090',
  opacity: 0.6
};

export const SAMPLE_FILL_OPACITY = {isComputed: false, value: 0.7};
export const SAMPLE_FILL_COLOR = {
  isComputed: true,
  zIndex: 1,
  property: 'HeritageStatus',
  function: 'categorical',
  domain: ['Contributory', 'Not contributory', 'Individually Significant', 'Victorian Heritage Register', 'Unknown', ''],
  range: ['#75954c', '#afc3c6', '#d279e5', '#e74d4d', '#FFFF00' , '#AAAAAA']
};
export const SAMPLE_CIRCLE_RADIUS = {
  isComputed: true,
  property: 'num_bikes_available',
  function: 'linear',
  domain: [0, 60],
  range: [2, 24]
};

// Maximum number of results to be returned by BigQuery API.
export const MAX_RESULTS = 3600; // The biggest heritage overlay HO327 has 3535 sites

// Maximum number of results to be shown in the HTML preview table.
export const MAX_RESULTS_PREVIEW = 10;

// How long to wait for the query to complete, in milliseconds, before the request times out and returns.
export const TIMEOUT_MS = 120000;

export const PALETTES = Object.keys(colorbrewer).map((key) => colorbrewer[key]);

export interface HeritageOverlay {
  ZONE_CODE: String;
  ZONE_DESC: String;
}

export const matchingHeritageOverlays: Array<HeritageOverlay> = [
  {
      ZONE_CODE: 'HO317',
      ZONE_DESC: 'Clifton Hill West'
  },
  {
      ZONE_CODE: 'HO330',
      ZONE_DESC: 'Queens Parade'
  }
  ];
