import { HttpClientModule, HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { environment } from '../../environments/environment';

export interface SosResponse {
  error: string | undefined;
  content: string | undefined;
}

import {
  map,
  catchError,
  debounceTime,
} from 'rxjs/operators';


/**
 * Utility class for fetching the SOS contents.
 */
@Injectable()
 export class SoSService {
  private _sosContent: String;
  private httpOptions;

  constructor(private http: HttpClient) {
     this.httpOptions = {
      headers: new HttpHeaders({
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Content-Type': 'application/x-www-form-urlencoded'
      }),
      responseType: 'text'
    };
   }

   getSoSContents(sosLink: string): Observable<String> {
    return this.http.get(sosLink, this.httpOptions).map(res => {
          return String(res);
        });
  }
}
