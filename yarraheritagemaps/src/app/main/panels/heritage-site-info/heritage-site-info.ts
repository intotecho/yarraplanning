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
    heritageStatusClass: String = '';
    earliest: Number = 0;
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
            this.earliest = event.feature.getProperty('earliest');

            switch (this.HeritageStatus.toLowerCase()) {
              case 'contributory':
                this.heritageStatusClass = 'heritage-status-contrib';
                break;
              case 'not contributory':
              this.heritageStatusClass = 'heritage-status-noncontrib' ;
              break;
              case 'individually significant':
              this.heritageStatusClass = 'heritage-status-individually';
              break;
              case 'victorian heritage register':
              this.heritageStatusClass = 'heritage-status-vhr';
              break;
              default:
              this.heritageStatusClass = 'heritage-status-unknown';
            }
          return this;
      }
    }

    vhrLink() {
        return `${VHD_KEYWORD_SEARCH}${this.VHR}`;
      }

    sosLink() {
        return `${GCS_BUCKET_SOS}${this.SosHash}.html`;
    }
}
