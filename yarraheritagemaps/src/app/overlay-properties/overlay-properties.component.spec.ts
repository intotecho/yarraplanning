import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OverlayPropertiesComponent } from './overlay-properties.component';

describe('OverlayPropertiesComponent', () => {
  let component: OverlayPropertiesComponent;
  let fixture: ComponentFixture<OverlayPropertiesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OverlayPropertiesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OverlayPropertiesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
