import { Component,
         AfterViewInit,
         Input,
         Output,
         HostListener,
         EventEmitter } from '@angular/core';
import { SoSService } from '../../../../../src/app/services/sos.service';
import { HeritageSiteInfo } from './heritage-site-info';
import { Observable, Subject} from 'rxjs';
import { OverlayProperties } from '../overlays-properties';

@Component({
  selector: 'app-heritage-site-info',
  templateUrl: './heritage-site-info.component.html',
  styleUrls: ['./heritage-site-info.component.css'],
})
export class HeritageSiteInfoComponent implements AfterViewInit {
  @Input() title: String;
  @Input() context: String;

  @Input()
  set heritageSiteInfo(heritageSiteInfo: HeritageSiteInfo) {
    this._heritageSiteInfo = heritageSiteInfo;
    gtag('event', 'site', { event_label: `siteinfo ${heritageSiteInfo.OriginalAddress}` });
    this.getDetails();
  }

  @Input()
  set overlayProperties(overlayProperties: OverlayProperties) {
    this._overlayProperties = overlayProperties;
  }

  @Input() panelHeightSubject: Subject<any>;

  @Output() hideFeature$: EventEmitter<HeritageSiteInfo> = new EventEmitter();

  _heritageSiteInfo: HeritageSiteInfo = new HeritageSiteInfo(null);
  _overlayProperties: OverlayProperties = null;
  sosDetails$: Observable<String>;
  portrait =  false;
  showpanel = true;
  _panelHeight = 30.0; // spliter output as a percent
  _browserHeight: number; // window height pixels.

  constructor(
    private sosService: SoSService
  ) {
     this.sosDetails$  = new Observable();
    }

  ngAfterViewInit() {
    this.onResizeWindow();
    this.panelHeightSubject.subscribe(event => {
      if (event !== null) {
          this._panelHeight = event[1];
      }
    });
    this.getDetails();
  }

  @HostListener('window:resize', ['$event'])
  onResizeWindow(event?) {
        this._browserHeight = window.innerHeight;
  }

  sosLink() {
    return this._heritageSiteInfo.sosLink();
  }

  getDetails() {
    const sosLink: string = this.sosLink();
    if (sosLink.length > 0) {
      this.sosDetails$.map(() => 'help');
      this.sosDetails$ = this.sosService.getSoSContents(this.sosLink());
    }
  }

  vhrLink() {
    return this._heritageSiteInfo.vhrLink();
  }

  vhdLink() {
    return this._heritageSiteInfo.href;
  }

  heritageStatusClass() {
    return this._heritageSiteInfo.heritageStatusClass;
  }

  onImageLoad(evt) {
    if (evt && evt.target) {
      const width = evt.srcElement.width;
      const height = evt.srcElement.height;
      // const x = evt.srcElement.x;
      // const y = evt.srcElement.y;
      if ((width > 0 ) && (height > 0)) {
        this.portrait = height > width ? true : false;
        // console.log('Loaded: ', width, height, 'portrait: ', this.portrait);
      }
    }
  }

  getImageStyle() {
    const heightPx = this._browserHeight * this._panelHeight / 100 - 36;
    const imageHeight = `${heightPx}px`;
    return {
      'max-width': '120%',
      'max-height': imageHeight
    };
  }

  hideFeature(event) {
    this.hideFeature$.emit(this._heritageSiteInfo);
  }

  closepanel() {
    this.showpanel = !this.showpanel;
  }

}
