import { VHD_KEYWORD_SEARCH, GCS_BUCKET_SOS } from '../../../app.constants';

/*
 *  Fields based on  table YARRAHERITAGEMAPS_PROPERTIES
 */
export class HeritageSiteInfo {
    Overlay: String ;
    PropertyType: String = '';
    NormalAddress: String = '';
    Authority: String = '';
    SosHash: String = '';
    HeritageStatus: String = '';
    EstimatedDate: String = '';
    Image: String = '';
    VHR: String = '';
    href: String = '';
    vhdplaceid: String = '';
    // Boundary: String = '';

    constructor(event) {
        if (event && event.feature) {
            this.Overlay = event.feature.getProperty('Overlay');
            this.PropertyType = event.feature.getProperty('PropertyType');
            this.NormalAddress = event.feature.getProperty('NormalAddress');
            this.VHR = event.feature.getProperty('VHR');
            this.Authority = event.feature.getProperty('Authority');
            this.HeritageStatus = event.feature.getProperty('HeritageStatus');
            this.EstimatedDate = event.feature.getProperty('EstimatedDate');
            this.Image = event.feature.getProperty('Image');
            this.href = event.feature.getProperty('href');
            this.vhdplaceid = event.feature.getProperty('vhdplaceid');
            this.SosHash = event.feature.getProperty('SosHash');
            return this;
        }
    }

    setHeritageSiteInfo(event: google.maps.Data.MouseEvent) {
        if (event && event.feature) {
          this.Overlay = event.feature.getProperty('Overlay');
          this.PropertyType = event.feature.getProperty('PropertyType');
          this.NormalAddress = event.feature.getProperty('NormalAddress');
          this.VHR = event.feature.getProperty('VHR');
          this.Authority = event.feature.getProperty('Authority');
          this.HeritageStatus = event.feature.getProperty('HeritageStatus');
          this.EstimatedDate = event.feature.getProperty('EstimatedDate');
          this.Image = event.feature.getProperty('Image');
          this.href = event.feature.getProperty('href');
          this.vhdplaceid = event.feature.getProperty('vhdplaceid');
          this.SosHash = event.feature.getProperty('SosHash');
          return this;
        } else {
          return null;
        }
    }

    vhrLink() {
        return `${VHD_KEYWORD_SEARCH}${this.VHR}`;
      }

    sosLink() {
        return `${GCS_BUCKET_SOS}${this.SosHash}.html`;
    }
}
