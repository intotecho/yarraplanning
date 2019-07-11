/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { AppSettings } from './appsettings.service';

describe('Service: Appsettings.service', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [AppSettings]
    });
  });

  it('should ...', inject([AppSettings], (service: AppSettings) => {
    expect(service).toBeTruthy();
  }));
});
