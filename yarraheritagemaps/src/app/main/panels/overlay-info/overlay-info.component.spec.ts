import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OverlayInfoComponent } from './overlay-info.component';

describe('OverlayPropertiesComponent', () => {
  let component: OverlayInfoComponent;
  let fixture: ComponentFixture<OverlayInfoComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OverlayInfoComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OverlayInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
