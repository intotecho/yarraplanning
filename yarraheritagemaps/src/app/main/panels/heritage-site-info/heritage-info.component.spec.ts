/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';
import { MatCardModule, MatExpansionModule } from '@angular/material';
import { HeritageSiteInfoComponent } from './heritage-site-info.component';
import { NguCarouselModule } from '@ngu/carousel';
import { SoSService } from '../../../services/sos.service';
import { HttpClientModule } from '@angular/common/http';
import { HttpClient } from '@angular/common/http';

describe('HeritageSiteInfoComponent', () => {
  let component: HeritageSiteInfoComponent;
  let fixture: ComponentFixture<HeritageSiteInfoComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HeritageSiteInfoComponent ],
      providers: [SoSService, HttpClient],
      imports: [ MatExpansionModule, MatCardModule, NguCarouselModule, HttpClientModule]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HeritageSiteInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
