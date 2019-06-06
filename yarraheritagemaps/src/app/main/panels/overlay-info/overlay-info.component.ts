import { Component, Input, OnInit } from '@angular/core';
import { OverlayProperties } from '../overlays-properties';

@Component({
  selector: 'app-overlay-info',
  templateUrl: './overlay-info.component.html',
  styleUrls: ['./overlay-info.component.css']
})
export class OverlayInfoComponent implements OnInit {
  @Input() overlayProperties: OverlayProperties;
  @Input() title: String;
  @Input() context: String;

  constructor(
  ) { }

  ngOnInit() {

  }

  public vhrLink() {
    return 'https://vhd.heritagecouncil.vic.gov.au/search?kw=' + this.overlayProperties.VHR;
  }

  public heritagePlaceName() {
    const name = this.overlayProperties.HeritagePlace.split('Incorporated plan')[0];
    return name ? name.trim() : '';
 }

 public incorporatedPlan() {
    const plan = this.overlayProperties.HeritagePlace.split(': Incorporated Plan')[1];
    return plan ? plan.trim() : '';
 }
}
