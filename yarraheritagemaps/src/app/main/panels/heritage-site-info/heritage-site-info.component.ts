
import { Component, ChangeDetectionStrategy, ChangeDetectorRef, Input, OnInit } from '@angular/core';
import { NguCarouselConfig, NguCarousel, NguCarouselStore } from '@ngu/carousel';
import { SoSService } from '../../../../../src/app/services/sos.service';
import { HeritageSiteInfo } from './heritage-site-info';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-heritage-site-info',
  templateUrl: './heritage-site-info.component.html',
  styleUrls: ['./heritage-site-info.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HeritageSiteInfoComponent implements OnInit {
  @Input() heritageSiteInfo: HeritageSiteInfo;
  @Input() title: String;
  @Input() context: String;

  _sosDetails: String = 'SOS Placeholder';
  sosDetails$: Observable<String>;

  imgags = [
    'assets/test/1.jpg',
    'assets/test/2.jpg',
    'assets/test/3.jpg',
    'assets/test/4.jpg',
  ];
  public carouselTileItems: Array<any> = [0, 1, 2, 3];
  public carouselTiles = {
    0: [],
    1: [],
    2: [],
    3: []
  };
  public carouselTile: NguCarouselConfig = {
    grid: { xs: 1, sm: 1, md: 1, lg: 1, all: 0 },
    slide: 3,
    speed: 250,
    point: {
      visible: true
    },
    load: 2,
    velocity: 0,
    touch: true
  };


  constructor(
    private cdr: ChangeDetectorRef,
    private sosService: SoSService
  ) { }

  ngOnInit() {
      this.carouselTileLoad();
  }

  onmoveFn(data: NguCarouselStore) {
    console.log(data);
  }

  public carouselTileLoad() {
    const len = this.carouselTileItems.length;
    for (let i = 0; i < len; i++) {
      this.carouselTiles[i].push(
        this.imgags[Math.floor(Math.random() * this.imgags.length)]
      );
    }
  }

  sosLink() {
    return this.heritageSiteInfo.sosLink();
  }

  getDetails() {
    const sosLink: string = this.sosLink();
    if (sosLink.length > 0) {
      this.sosDetails$ = this.sosService.getSoSContents(this.sosLink());
    }
  }

  vhrLink() {
    return this.heritageSiteInfo.vhrLink();
  }

  vhdLink() {
    return this.heritageSiteInfo.href;
  }

  heritageStatusClass() {
    switch (this.heritageSiteInfo.HeritageStatus) {
          case 'Contributory':
          return 'heritage-status-contrib';
          case 'Not contributory':
          return 'heritage-status-noncontrib' ;
          case 'Individually Significant':
          return 'heritage-status-individually';
          case 'Victorian Heritage Register':
          return 'heritage-status-vhr';
          default:
          return 'heritage-status-unknown';
    }
  }
}
