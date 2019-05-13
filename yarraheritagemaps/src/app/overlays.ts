
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

    constuctor(
    ) {}
}
