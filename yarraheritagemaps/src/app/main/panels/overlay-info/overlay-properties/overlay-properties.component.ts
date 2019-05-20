import { Component, Input, OnInit } from '@angular/core';
import { OverlayProperties } from '../../overlays-properties';

@Component({
  selector: 'app-overlay-properties',
  templateUrl: './overlay-properties.component.html',
  styleUrls: ['./overlay-properties.component.css']
})
export class OverlayInfoComponent implements OnInit {
  @Input() overlayProperties: OverlayProperties;
  @Input() title: String;
  @Input() context: String;

  constructor(
  ) { }

  ngOnInit() {

  }

  vhrLink() {
    return 'https://vhd.heritagecouncil.vic.gov.au/search?kw=' + this.overlayProperties.VHR;
  }
}
