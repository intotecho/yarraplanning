/**
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
import { environment } from '../../environments/environment';
import { MAX_RESULTS, TIMEOUT_MS } from '../app.constants';
import { OverlayProperties } from '../main/panels/overlays-properties';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export const ColumnType = {
  STRING: 'string',
  NUMBER: 'number',
  LAT: 'latitude',
  LNG: 'longitude',
  WKT: 'wkt',
  DATE: 'date',
  ID: 'id'
};

export interface ColumnStat {
  min: number;
  max: number;
  nulls: number;
}

export interface OverlaysResponse {
  error: string | undefined;
  columns: Array<Object> | undefined;
  columnNames: Array<string> | undefined;
  rows: Array<Object> | undefined;
  stats: Map<String, ColumnStat> | undefined;
}

/**
 * Utility class for managing interaction with the Overlays API.
 */
@Injectable()
export class OverlaysService {
  constructor(private http: HttpClient) {
  }
  configUrl = 'overlays';
  getOverlays() {
        // now returns an Observable of Config
        return this.http.get<OverlaysResponse>(this.configUrl);
  }
}
