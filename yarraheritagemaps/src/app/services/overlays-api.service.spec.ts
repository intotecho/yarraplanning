import { TestBed } from '@angular/core/testing';

import { OverlaysAPIService } from './overlays-api.service';

describe('OverlaysAPIService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: OverlaysAPIService = TestBed.get(OverlaysAPIService);
    expect(service).toBeTruthy();
  });
});
