import { VHD_KEYWORD_SEARCH, GCS_BUCKET_SOS } from '../../../app.constants';

/*
 *  Fields based on table YARRAHERITAGEMAPS_PROPERTIES. These must align with the Query.
    EZI_ADD,
    HeritageStatus,
    Overlay,
    Name,
    vhdplaceid,
    Image,
    href,
    VHR,
    SosHash,
    PropertyType,
    PropertyId,
    NormalAddress,
    EstimatedDate,
    Matched,
    PROPERTY_PFI
 */
export class HeritageSiteInfo {
    EZI_ADD: String = '';
    HeritageStatus: String = '';
    Overlay: String ;
    vhdOverlay: String ;
    vhdplaceid: String = '';
    Name: String = '';
    Image: String = '';
    Authority: String = '';
    href: String = '';
    PropertyType: String = '';
    NormalAddress: String = '';
    SosHash: String = '';
    EstimatedDate: String = '';
    VHR: String = '';
    // Boundary: String = '';

    constructor(event) {
        if (event && event.feature) {
            this.EZI_ADD = event.feature.getProperty('EZI_ADD');
            this.HeritageStatus = event.feature.getProperty('HeritageStatus');
            this.Overlay = event.feature.getProperty('Overlay');
            this.PropertyType = event.feature.getProperty('PropertyType');
            this.NormalAddress = event.feature.getProperty('NormalAddress');
            this.Authority = event.feature.getProperty('Authority');
            this.SosHash = event.feature.getProperty('SosHash');
            this.VHR = event.feature.getProperty('VHR');
            this.EstimatedDate = event.feature.getProperty('EstimatedDate');
            this.Image = event.feature.getProperty('Image');
            this.href = event.feature.getProperty('href');
            this.vhdplaceid = event.feature.getProperty('vhdplaceid');
            return this;
        }
    }

    /*
    setHeritageSiteInfo(event: google.maps.Data.MouseEvent) {
        if (event && event.feature) {
          this.EZI_ADD = event.feature.getProperty('EZI_ADD');
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
     */

    vhrLink() {
        return `${VHD_KEYWORD_SEARCH}${this.VHR}`;
      }

    sosLink() {
        return `${GCS_BUCKET_SOS}${this.SosHash}.html`;
    }
}
