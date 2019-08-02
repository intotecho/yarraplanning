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

 getImageStyle() {
   //const heightPx = this._browserHeight * this._panelHeight / 100 - 36;
   //const imageHeight = `${heightPx}px`;
   return {
    'max-width': '120%',
    'max-height': '100%'
   };
 }

 onImageLoad(evt) {
  if (evt && evt.target) {
    const width = evt.srcElement.width;
    const height = evt.srcElement.height;
    // const x = evt.srcElement.x;
    // const y = evt.srcElement.y;
    if ((width > 0 ) && (height > 0)) {
      //this.portrait = height > width ? true : false;
      // console.log('Loaded: ', width, height, 'portrait: ', this.portrait);
    }
  }
}

}
