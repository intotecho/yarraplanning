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
    row_num: Number = 0;
    EZI_ADD: String = '';
    HeritageStatus: String = '';
    Overlay: String ;
    Name: String = '';
    vhdplaceid: String = '';
    vhdPlacesId: String = '';
    Image: String = '';
    Authority: String = '';
    PropertyType: String = '';
    PropertyId: String = '';
    EstimatedDate: String = '';
    OriginalAddress: String = '';
    vhdLocation: String = '';
    Matched: String = '';
    PROPERTY_PFI: String = '';
    VHR: String = '';
    href: String = '';
    SosHash: String = '';
    earliest: Number = 0;
    heritageStatusClass: String = '';
    vhdList: String[];

    constructor(event) {
        if (event && event.feature) {
            this.row_num = event.feature.getProperty('row_num');
            this.EZI_ADD = event.feature.getProperty('EZI_ADD');
            this.HeritageStatus = event.feature.getProperty('HeritageStatus');
            this.Overlay = event.feature.getProperty('Overlay');
            this.Name = event.feature.getProperty('Name'); // vhd name
            this.vhdplaceid = event.feature.getProperty('vhdplaceid');
            this.vhdPlacesId = event.feature.getProperty('vhdPlacesId');
            this.Image = event.feature.getProperty('Image');
            this.Authority = event.feature.getProperty('Authority');
            this.PropertyType = event.feature.getProperty('PropertyType');
            this.PropertyId = event.feature.getProperty('PropertyId');
            this.EstimatedDate = event.feature.getProperty('EstimatedDate');
            this.OriginalAddress = event.feature.getProperty('OriginalAddress');
            this.vhdLocation = event.feature.getProperty('vhdLocation');
            this.Matched = event.feature.getProperty('Matched');
            this.PROPERTY_PFI = event.feature.getProperty('PROPERTY_PFI');
            this.VHR = event.feature.getProperty('VHR');
            this.href = event.feature.getProperty('href');
            this.SosHash = event.feature.getProperty('SosHash');
            this.earliest = event.feature.getProperty('earliest');
            this.vhdList = this.StringToList(this.vhdPlacesId);

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

    /*Take a string formatted as "['asdasd','asd']" and return a list of strings
     */

    StringToList(input_str: String): String[] {
      const a:string = input_str.replace(/'/g, '"');
      return(JSON.parse(a));
    }

    vhrLink() {
        return `${VHD_KEYWORD_SEARCH}${this.VHR}`;
    }

    sosLink() {
        return `${GCS_BUCKET_SOS}${this.SosHash}.html`;
    }

    vhdLink(vhdIndex = 0) {
      const url = this.href;
      const removelastdir: String = url.substring(0, url.lastIndexOf('/'));
      return removelastdir + '/' + vhdIndex;
    }
}
