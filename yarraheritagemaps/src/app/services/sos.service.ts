import { environment } from '../../environments/environment';

export interface SosResponse {
  error: string | undefined;
  content: string | undefined;
}


// student.service.ts

import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import {
  map,
  catchError,
  debounceTime,
} from 'rxjs/operators';


/**
 * Utility class for fetching the SOS contents.
 */

 export class SoSService {
  private _sosContent: String;

  constructor(private http: HttpClient) {}

  getSoSContents(sosLink: string): Observable<String> {
    return this.http.get(sosLink).map(res => {
          return String(res);
        });
  }
}
