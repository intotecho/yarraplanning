import { Component, ChangeDetectionStrategy, ChangeDetectorRef, ViewChild, Input, Output, EventEmitter } from '@angular/core';
import { NguCarouselConfig, NguCarousel } from '@ngu/carousel';
import { SoSService } from '../../../../../src/app/services/sos.service';
import { HeritageSiteInfo } from './heritage-site-info';
import { Observable } from 'rxjs';
import { OverlayProperties } from '../overlays-properties';
import { FlexLayoutModule } from '@angular/flex-layout';

const SOS_SLIDE = 2;

@Component({
  selector: 'app-heritage-site-info',
  templateUrl: './heritage-site-info.component.html',
  styleUrls: ['./heritage-site-info.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HeritageSiteInfoComponent {
  @Input() title: String;
  @Input() context: String;

  @Input()
  set heritageSiteInfo(heritageSiteInfo: HeritageSiteInfo) {
    this._heritageSiteInfo = heritageSiteInfo;
    this.carouselTileLoad();
    gtag('event', 'site', { event_label: `siteinfo ${heritageSiteInfo.OriginalAddress}` });
  }

  @Input()
  set overlayProperties(overlayProperties: OverlayProperties) {
    this._overlayProperties = overlayProperties;
    // this.carouselTileLoad();
  }

  @Output() hideFeature$: EventEmitter<HeritageSiteInfo> =   new EventEmitter();

  _heritageSiteInfo: HeritageSiteInfo = new HeritageSiteInfo(null);
  _overlayProperties: OverlayProperties = null;
  _sosDetails: String = 'SOS Placeholder';
  sosDetails$: Observable<String>;
  sosExpanded = false;
  panelHeight = 'normal-mat-panel';
  portrait =  false;
  naturalWidth = 320;
  naturalHeight = 220;
  currentSlide = -1;
  showpanel = true;

  @ViewChild('myCarousel', {static: false}) myCarousel: NguCarousel<Number>;
  carouselConfig: NguCarouselConfig = {
    grid: { xs: 1, sm: 1, md: 1, lg: 1, all: 0 },
    load: 2,
    touch: true,
    point: {
      visible: true
    },
    slide: 3,
    speed: 250,
    velocity: 0
  };

  constructor(
    private cdr: ChangeDetectorRef,
    private sosService: SoSService
  ) { }

  onCarouselMove() {
    gtag('event', 'site', { event_label: `moveto ${this.currentSlide}` });
    this.sosExpanded = (this.currentSlide === SOS_SLIDE) ? true : false;
  }

  public carouselTileLoad() {
    if (this.myCarousel) {
      this.currentSlide = this.myCarousel.currentSlide;
      if (this.currentSlide  === SOS_SLIDE) {
        this.getDetails();
      }
    }
  }

  moveLeft() {
    const myCarousel = this.myCarousel;
    if (myCarousel) {
      const currentSlide = myCarousel.currentSlide;
      if (currentSlide > 0) {
        myCarousel.moveTo(myCarousel.currentSlide - 1);
      }
    }
  }

  moveRight() {
    const myCarousel = this.myCarousel;
    if (myCarousel) {
      if (! myCarousel.isLast) {
        const currentSlide = myCarousel.currentSlide;
        myCarousel.moveTo(myCarousel.currentSlide + 1);
      }
    }
  }

  sosLink() {
    return this._heritageSiteInfo.sosLink();
  }

  getDetails() {
    const sosLink: string = this.sosLink();
    if (sosLink.length > 0) {
      this.sosDetails$ = this.sosService.getSoSContents(this.sosLink());
      this.sosExpanded = true;
    }
  }

  vhrLink() {
    return this._heritageSiteInfo.vhrLink();
  }

  vhdLink() {
    return this._heritageSiteInfo.href;
  }

  /* 
   * minimize, maximize and restore the card by clicking on its title bar.
   */
  handleCardTitleClick() {
    switch (this.panelHeight) {
      case 'expanded-mat-panel':
        this.panelHeight = 'mini-mat-panel';
        gtag('event', 'site', { event_label: `panelsize expanded` });
        break;
      case 'normal-mat-panel':
          this.panelHeight = 'expanded-mat-panel';
          gtag('event', 'site', { event_label: `panelsize normal` });
          break;
      case 'mini-mat-panel':
            this.panelHeight = 'normal-mat-panel'; // @todo The panel is actually hidden.
            gtag('event', 'site', { event_label: `panelsize mini` });
            break;
        }
  }

  heritageStatusClass() {
    return this._heritageSiteInfo.heritageStatusClass;
  }

  onImageLoad(evt) {
    if (evt && evt.target) {
      const width = evt.srcElement.width;
      const height = evt.srcElement.height;
      const x = evt.srcElement.x;
      const y = evt.srcElement.y;
      if ((width > 0 ) && (height > 0)) {
        this.portrait = height > width ? true : false;
        console.log('Loaded: ', width, height, 'portrait: ', this.portrait);
        this.naturalWidth = width;
        this.naturalHeight = height;
        this.cdr.detectChanges();
      }
    }
  }

  getImageStyle() {
    if (this.portrait) {
      return {
        'max-width': '100%',
        'max-height': '30vh%'
      };
    } else {
      return {
        'max-width': '100%',
        'max-height': '30vh'
      };
    }
    /*
    const style = {
      'max-width.px': this.naturalWidth,
      'max-height.px': this.naturalHeight,
      'width.px': this.naturalWidth,
      'height.px': this.naturalHeight
    };
    const unusedstyle2 = `{'max-width.px': ${this.naturalWidth},
                    'max-height.px':${this.naturalHeight}}`;
    return style;
    */
  }

  hideFeature(event) {
    this.hideFeature$.emit(this._heritageSiteInfo);
  }

  closepanel() {
    this.showpanel = !this.showpanel;
  }

}
