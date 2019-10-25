import { Injectable } from '@angular/core';
import { HttpClientModule, HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

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

@Injectable()
export class OverlaysAPIService {
  private _apiUrl: string;
  private httpOptions;

  constructor(private httpClient: HttpClient) {
    this.httpOptions = {
      headers: new HttpHeaders({
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Content-Type': 'application/json'
      }),
      responseType: 'text'
    };
    this._apiUrl = environment.dataAPIBasePath  + '/overlays';
  }

  public getOverlays(): Observable<OverlaysResponse[]> {
    const url = this._apiUrl;
    return this.httpClient.get<OverlaysResponse[]>(url);
  }

  public getOverlay(overlayId: string ): Observable<OverlaysResponse[]> {
    const url = this._apiUrl + '/' + overlayId;
    return this.httpClient.get<OverlaysResponse[]>(url);
  }

  public getPlanningApplications(overlayId: string ): Observable<OverlaysResponse[]> {
    const url = this._apiUrl + '/' + overlayId + '?infotype=planning';
    return this.httpClient.get<OverlaysResponse[]>(url);
  }
}
