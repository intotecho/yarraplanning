
import { Component, Input, OnInit } from '@angular/core';
import { SoSService } from '../../../../../src/app/services/sos.service';
import { HeritageSiteInfo } from './heritage-site-info';
import { Observable } from 'rxjs/Observable';

@Component({
  selector: 'app-heritage-site-info',
  templateUrl: './heritage-site-info.component.html',
  styleUrls: ['./heritage-site-info.component.css']
})
export class HeritageSiteInfoComponent implements OnInit {
  @Input() heritageSiteInfo: HeritageSiteInfo;
  @Input() title: String;
  @Input() context: String;
  _sosDetails: String = 'SOS Placeholder';
  sosDetails$: Observable<String>;

  constructor(
    private sosService: SoSService
  ) { }

  ngOnInit() {
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
