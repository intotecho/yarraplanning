import { Component, Input, OnInit } from '@angular/core';
import { OverlayProperties } from '../overlays';

@Component({
  selector: 'app-overlay-properties',
  templateUrl: './overlay-properties.component.html',
  styleUrls: ['./overlay-properties.component.css']
})
export class OverlayPropertiesComponent implements OnInit {
  @Input() overlayProperties: OverlayProperties;

  constructor(
  ) { }

  ngOnInit() {

  }

  vhrLink() {
    return 'https://vhd.heritagecouncil.vic.gov.au/search?kw=' + this.overlayProperties.VHR;
  }
}
