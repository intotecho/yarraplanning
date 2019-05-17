
export interface Overlay {
    id: String;
    name: String;
}

export interface HeritageOverlay {
    ZONE_CODE: String;
    ZONE_DESC: String;
}

export const matchingHeritageOverlays: Array<HeritageOverlay> = [
    {
        ZONE_CODE: 'HO317',
        ZONE_DESC: 'Clifton Hill West'
    },
    {
        ZONE_CODE: 'HO330',
        ZONE_DESC: 'Queens Parade'
    }
    ];

export class OverlayProperties {
    Overlay: String ;
    HeritagePlace: String = '';
    PaintControls: String = '';
    InternalControls: String = '';
    TreeControls: String = '';
    FenceControls: String = '';
    IncludedInVHR = false;
    Included: String = '';
    VHR: String = '';
    Prohibited: String = '';
    AboriginalHeritagePlace: String = '';
    Status: String = '';
    Expiry: Date = new Date('1900/01/01');


    constructor(event: google.maps.Data.MouseEvent) {
        if (event && event.feature) {
            this.Overlay = event.feature.getProperty('Overlay');
            this.HeritagePlace = event.feature.getProperty('HeritagePlace');
            this.Included = event.feature.getProperty('Included');
            this.VHR = event.feature.getProperty('VHR');
            this.PaintControls = event.feature.getProperty('PaintControls');
            this.InternalControls = event.feature.getProperty('InternalControls');
            this.TreeControls = event.feature.getProperty('TreeControls');
            this.FenceControls = event.feature.getProperty('FenceControls');
            this.Prohibited = event.feature.getProperty('Prohibited');
            this.AboriginalHeritagePlace = event.feature.getProperty('AboriginalHeritagePlace');
            this.Status = event.feature.getProperty('Status');
            this.Expiry = event.feature.getProperty('Expiry');
        }
    }

    setOverlayInfo(event: google.maps.Data.MouseEvent) {
        if (event && event.feature) {
          this.Overlay = event.feature.getProperty('Overlay');
          this.HeritagePlace = event.feature.getProperty('HeritagePlace');
          this.Included = event.feature.getProperty('Included');
          this.VHR = event.feature.getProperty('VHR');
          this.PaintControls = event.feature.getProperty('PaintControls');
          this.InternalControls = event.feature.getProperty('InternalControls');
          this.TreeControls = event.feature.getProperty('TreeControls');
          this.FenceControls = event.feature.getProperty('FenceControls');
          this.Prohibited = event.feature.getProperty('Prohibited');
          this.AboriginalHeritagePlace = event.feature.getProperty('AboriginalHeritagePlace');
          this.Status = event.feature.getProperty('Status');
          this.Expiry = event.feature.getProperty('Expiry');
          return this;
        } else {
          return null;
        }
      }
}
