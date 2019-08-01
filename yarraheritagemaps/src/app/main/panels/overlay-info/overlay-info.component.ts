import { Component, Input, OnInit } from '@angular/core';
import { OverlayProperties } from '../overlays-properties';

@Component({
  selector: 'app-overlay-info',
  templateUrl: './overlay-info.component.html',
  styleUrls: ['./overlay-info.component.css']
})
export class OverlayInfoComponent implements OnInit {
  @Input() title: String;
  @Input() context: String;
  public _overlayProperties: OverlayProperties;

  constructor(
  ) {
   }

  ngOnInit() {

  }

  @Input()
  set overlayProperties(overlayProperties: OverlayProperties) {
    this._overlayProperties = overlayProperties;
  }

  public vhrLink() {
    return 'https://vhd.heritagecouncil.vic.gov.au/search?kw=' + this._overlayProperties.VHR;
  }

  public heritagePlaceName() {
    const name = this._overlayProperties.HeritagePlace.split('Incorporated plan')[0];
    return name ? name.trim() : '';
 }

 public incorporatedPlan() {
    const plan = this._overlayProperties.HeritagePlace.split(': Incorporated Plan')[1];
    return plan ? plan.trim() : '';
 }
}
