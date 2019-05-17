import { Component, Input, OnInit } from '@angular/core';
import { HeritageSiteInfo } from '../heritage-site-info';

@Component({
  selector: 'app-heritage-site-info',
  templateUrl: './heritage-site-info.component.html',
  styleUrls: ['./heritage-site-info.component.css']
})
export class HeritageSiteInfoComponent implements OnInit {
  @Input() heritageSiteInfo: HeritageSiteInfo;
  @Input() title: String;
  @Input() context: String;

  constructor() { }

  ngOnInit() {
  }

  sosLink() {
    return this.heritageSiteInfo.sosLink();
  }

  vhrLink() {
    return this.heritageSiteInfo.vhrLink();
  }

  vhdLink() {
    return this.heritageSiteInfo.href;
  }
}
